# implementation Guide: Telugu Wikipedia Article Evaluation Platform

This guide outlines how to implement the specific automated evaluation features requested for the Telugu Wikipedia Article Evaluation project within the existing WikiContest Flask application.

## 1. Feature Existence Analysis

| Requirement | Exists? | Location / Notes |
| :--- | :--- | :--- |
| **Config via Wiki Page** | **No** | Replaced by "Contest Creation" UI in the platform (as per user instruction). |
| **Crawl Articles from Category** | **No** | Current system only supports manual single-link submission. |
| **Eligibility: Whitelist** | **No** | Logic exists for *Creator* whitelist (`get_mediawiki_user_edit_count`), but not for *Submitter* whitelist. |
| **Eligibility: Link Counts** | **No** | Incoming/Outgoing link counts are not checked. |
| **Metrics: Bytes/Words** | **Yes** | `backend/app/utils/__init__.py` fetches `size` (bytes). Words can be derived. |
| **Metrics: Images/Infoboxes** | **No** | Not currently fetched or counted. |
| **Metrics: Ref Analysis** | **Partial** | Total refs counted, but "New vs Reused" distinction is missing. |
| **Scoring: Formula-based** | **No** | Current system uses Human Scoring (0-10) or simple Pass/Fail. |
| **Reporting: Write to Wiki** | **No** | System saves to DB but does not write reports back to Wiki. |

---

## 2. Implementation Steps

### Step 1: Bulk Import & Category Crawling
**Goal:** Allow admins to import all articles from a specific category instead of waiting for users to submit them manually.

1.  **Modify `backend/app/utils/__init__.py`**:
    *   Add a function `get_category_members(category_name, depth=0)` using MediaWiki API `list=categorymembers`.
    *   Implement pagination using `cmcontinue` to handle 5,000+ articles.

2.  **Add Route in `backend/app/routes/contest_routes.py`**:
    *   `POST /contest/<id>/import-category`: Accepts a category name.
    *   Calls `get_category_members`.
    *   Loops through results and creates `Submission` records (checking for duplicates).

### Step 2: Expanded Data Collection (Metrics)
**Goal:** Collect images, infoboxes, and reference details.

1.  **Update `fetch_article_info` in `backend/app/routes/submission_routes.py`** (or utils):
    *   Modify the MediaWiki API request to include `prop=images|categories|extlinks|revisions&rvprop=content`.
    *   **Images:** Count `len(data['images'])`.
    *   **Infoboxes:** Parse `revisions[0]['slots']['main']['content']` using Regex (e.g., `r'{{Infobox'`).
    *   **References:**
        *   **Total:** Count `<ref>` tags in wikitext.
        *   **Reused:** Count `<ref name="..."/>` tags.
        *   **New:** Total - Reused.

2.  **Update `Submission` Model (`backend/app/models/submission.py`)**:
    *   Add columns: `image_count`, `infobox_count`, `ref_new_count`, `ref_reused_count`, `incoming_links_count`, `outgoing_links_count`.

### Step 3: Eligibility Logic
**Goal:** Filter users and articles based on rules.

1.  **Update `Contest` Model**:
    *   Add columns for criteria: `min_incoming_links`, `min_outgoing_links`, `user_whitelist_url`.

2.  **Implement Whitelist Check**:
    *   In `backend/app/utils/__init__.py`, add `fetch_wiki_page_list(page_title)` to parse a list of usernames from a wiki page.
    *   In `contest.py`, add `validate_user_eligibility(user)` that checks if `user.username` is in the fetched list.

3.  **Update Validation Logic**:
    *   In `backend/app/routes/submission_routes.py`, inside the `submit` function:
        *   Run `contest.validate_user_eligibility(user)`.
        *   Run link count checks.
        *   If failed, mark status as `auto_rejected` and (optionally) post to User Talk Page.

### Step 4: Automated Scoring
**Goal:** Calculate score based on `0.01 per byte`, etc.

1.  **Update `Contest` Model**:
    *   Add `auto_scoring_config` (JSON) column to store the multipliers (e.g., `{"byte_weight": 0.01, "image_weight": 3}`).

2.  **Implement Scoring Method in `Submission`**:
    ```python
    def calculate_auto_score(self, config):
        score = 10 # Base points for accepted
        score += self.word_count * config.get('word_weight', 0.1)
        score += self.image_count * config.get('image_weight', 3)
        # ... add other metrics
        return round(score)
    ```

3.  **Trigger Scoring**:
    *   Call this method automatically when a submission is created/imported.

### Step 5: Report Generation & Write-Back
**Goal:** Publish the evaluation table to the Wiki.

1.  **Add `generate_wikitext_report(contest_id)` in `utils`**:
    *   Query all submissions for the contest.
    *   Format them into a Wikitext table string:
        ```wikitext
        {| class="wikitable sortable"
        ! Article !! User !! Bytes !! Score
        |-
        | [[Article Name]] || [[User:Name]] || 6000 || 85
        |}
        ```

2.  **Add `post_to_wiki(page_title, content)`**:
    *   Use the existing `mwoauth` session of the **Contest Admin** (the user who clicked "Publish").
    *   Call MediaWiki `edit` API to overwrite the report page.

3.  **Add Route**:
    *   `POST /contest/<id>/publish-report`: Triggers the generation and write-back.

## Summary of Files to Touch
1.  `backend/app/models/contest.py` (New config fields)
2.  `backend/app/models/submission.py` (New metric columns)
3.  `backend/app/utils/__init__.py` (Crawling, Expanded Metadata Fetching, Wikitext Generation)
4.  `backend/app/routes/contest_routes.py` (Import & Publish routes)
