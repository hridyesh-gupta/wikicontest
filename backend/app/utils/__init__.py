"""
Utility Functions for WikiContest Application.

This module contains shared helpers that are used by the Flask routes,
Alembic‑backed models, and maintenance scripts.

The focus here is small, well‑documented functions:
- Permission and access control helpers.
- MediaWiki API helpers.
- Simple parsing helpers.

All functions are intentionally simple and safe.
They catch network / parsing errors and return `None` instead of crashing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse, unquote, parse_qs

import requests
from flask import jsonify


__all__ = [
    "validate_contest_submission_access",
    "get_article_size_at_timestamp",
    "extract_page_title_from_url",
    "get_latest_revision_author",
    "build_mediawiki_revisions_api_params",
    "get_mediawiki_headers",
]


# ---------------------------------------------------------------------------
# Access control helpers
# ---------------------------------------------------------------------------

def validate_contest_submission_access(contest_id, user, Contest):
    """
    Check if a user is allowed to view or manage submissions for a contest.

    This is used by multiple routes and must stay very small and clear.

    Returns:
        (contest, error_response)
        - contest: Contest object when access is allowed, else None.
        - error_response: (Response, status_code) when access is denied, else None.
    """
    # Fetch contest from the database.
    contest = Contest.query.get(contest_id)

    if not contest:
        # Contest does not exist.
        return None, (jsonify({"error": "Contest not found"}), 404)

    # Admin users are always allowed.
    # Our User model exposes this as a method (see app.models.user.User).
    if hasattr(user, "is_admin") and callable(getattr(user, "is_admin")):
        if user.is_admin():
            return contest, None

    # Contest creator is allowed.
    # created_by stores the creator's username.
    if getattr(user, "username", None) == getattr(contest, "created_by", None):
        return contest, None

    # Jury members are allowed.
    # Contest keeps jury members as a comma‑separated string of usernames.
    try:
        from app.models.user import User  # local import to avoid circular deps
    except Exception:  # pylint: disable=broad-exception-caught
        User = None  # type: ignore

    if User is not None and hasattr(user, "is_jury_member"):
        try:
            # Prefer the dedicated helper on the User model.
            if user.is_jury_member(contest):
                return contest, None
        except Exception:  # pylint: disable=broad-exception-caught
            # Fall back to manual parsing if something goes wrong.
            pass

    # Manual fallback: parse jury_members as usernames list.
    jury_members_raw = getattr(contest, "jury_members", "") or ""
    jury_usernames = [u.strip() for u in jury_members_raw.split(",") if u.strip()]
    if getattr(user, "username", None) in jury_usernames:
        return contest, None

    # No matching permission rule → deny access.
    return None, (jsonify({"error": "Permission denied"}), 403)


# ---------------------------------------------------------------------------
# MediaWiki helpers
# ---------------------------------------------------------------------------

def extract_page_title_from_url(article_url: str) -> Optional[str]:
    """
    Extract a MediaWiki page title from a full article URL.

    This mirrors the logic used in the maintenance scripts.
    It supports:
    - `/wiki/Page_Title` style URLs.
    - `/w/index.php?title=Page_Title` style URLs.
    - Fallback to the last path segment.

    Returns:
        The decoded page title string, or None when it cannot be extracted.
    """
    if not article_url:
        return None

    url_obj = urlparse(article_url)

    # Standard `/wiki/Page_Title` format.
    if "/wiki/" in url_obj.path:
        return unquote(url_obj.path.split("/wiki/")[1])

    # Old style `/w/index.php?title=Page_Title` format.
    if "title=" in url_obj.query:
        query_params = parse_qs(url_obj.query)
        return unquote(query_params.get("title", [""])[0])

    # Fallback: last non‑empty path segment.
    parts = [p for p in url_obj.path.split("/") if p]
    if parts:
        return unquote(parts[-1])

    return None


def build_mediawiki_revisions_api_params(page_title: str) -> Dict[str, Any]:
    """
    Build a standard parameter set for MediaWiki `revisions` queries.

    This is shared by the routes and scripts so that any change to the
    API contract is done in a single place.
    """
    return {
        "action": "query",
        "titles": page_title,
        "format": "json",
        "formatversion": "2",
        "prop": "info|revisions",
        # We request timestamp, user, userid, and size so that callers can
        # compute authorship and word/byte counts.
        "rvprop": "timestamp|user|userid|comment|size",
        # Get both newest and oldest revisions in a tiny window.
        "rvlimit": "2",
        # With rvdir='older', the first revision in the list is the newest.
        "rvdir": "older",
        "redirects": "true",
        "converttitles": "true",
    }


def get_mediawiki_headers() -> Dict[str, str]:
    """
    Return a standard set of HTTP headers for MediaWiki API calls.

    MediaWiki requires a descriptive User‑Agent.
    Using one shared helper keeps this string consistent.
    """
    return {
        "User-Agent": (
            "WikiContest/1.0 (https://wikicontest.toolforge.org; "
            "contact@wikicontest.org) Python/requests"
        )
    }


def get_latest_revision_author(revisions: Iterable[Dict[str, Any]]) -> Optional[str]:
    """
    Get the author of the latest revision from a revisions list.

    The calling code usually passes the list returned by the MediaWiki API.
    With `rvdir='older'`, the first element is the newest revision.

    Returns:
        Username string when available, a simple "User ID: <id>" fallback,
        or None when no author information is present.
    """
    revisions_list: List[Dict[str, Any]] = list(revisions or [])
    if not revisions_list:
        return None

    latest = revisions_list[0]

    # Prefer the human‑readable username when available.
    user_name = latest.get("user")
    if user_name:
        return user_name

    # Fallback to numeric user id when username is missing.
    user_id = latest.get("userid")
    if user_id:
        return f"User ID: {user_id}"

    return None


def get_article_size_at_timestamp(article_url: str, when: datetime) -> Optional[int]:
    """
    Get the article size (bytes) at or before a specific timestamp.

    This is used to compute expansion bytes for contests.
    It keeps the logic small by doing a single `revisions` API call and
    returning the size of the newest revision that is not newer than `when`.

    Args:
        article_url: Full article URL.
        when: UTC datetime to look back from.

    Returns:
        Integer byte size if available, otherwise None.
    """
    page_title = extract_page_title_from_url(article_url)
    if not page_title:
        return None

    url_obj = urlparse(article_url)
    base_url = f"{url_obj.scheme}://{url_obj.netloc}"
    api_url = f"{base_url}/w/api.php"

    # ISO timestamp in the format expected by MediaWiki.
    when_iso = when.strftime("%Y-%m-%dT%H:%M:%SZ")

    params: Dict[str, Any] = {
        "action": "query",
        "titles": page_title,
        "format": "json",
        "formatversion": "2",
        "prop": "revisions",
        "rvprop": "timestamp|size",
        # We want the newest revision at or before `when`.
        "rvlimit": "1",
        "rvdir": "older",
        "rvstart": when_iso,
        "redirects": "true",
        "converttitles": "true",
    }

    try:
        response = requests.get(api_url, params=params, headers=get_mediawiki_headers(), timeout=10)
    except requests.RequestException:
        # Network error. Caller will handle `None` gracefully.
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except ValueError:
        return None

    if "error" in data:
        return None

    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return None

    page_data = pages[0]
    revisions = page_data.get("revisions", [])
    if not revisions:
        return None

    # Single revision because we requested `rvlimit=1`.
    rev = revisions[0]
    return rev.get("size")
