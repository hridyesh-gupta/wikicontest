#!/usr/bin/env python3
"""
Backfill script to fetch article information for existing submissions
that don't have author or word count data.

Usage:
    python backfill_article_info.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.submission import Submission
import requests
from urllib.parse import urlparse, unquote, parse_qs

def fetch_article_info(article_link):
    """Fetch article information from MediaWiki API"""
    try:
        # Parse the article URL
        url_obj = urlparse(article_link)
        base_url = f"{url_obj.scheme}://{url_obj.netloc}"
        
        # Extract page title
        page_title = ''
        if '/wiki/' in url_obj.path:
            page_title = unquote(url_obj.path.split('/wiki/')[1])
        elif 'title=' in url_obj.query:
            query_params = parse_qs(url_obj.query)
            page_title = unquote(query_params.get('title', [''])[0])
        else:
            parts = url_obj.path.split('/')
            page_title = unquote(parts[-1]) if parts else ''
        
        if not page_title:
            return None
        
        # Build API request
        api_url = f"{base_url}/w/api.php"
        api_params = {
            'action': 'query',
            'titles': page_title,
            'format': 'json',
            'formatversion': '2',
            'prop': 'info|revisions',
            'rvprop': 'timestamp|user|userid|comment|size',
            'rvlimit': '1',
            'rvdir': 'newer',
            'redirects': 'true',
            'converttitles': 'true'
        }
        headers = {
            'User-Agent': 'WikiContest/1.0 (https://wikicontest.toolforge.org; contact@wikicontest.org) Python/requests'
        }
        
        response = requests.get(api_url, params=api_params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if 'error' in data:
            return None
        
        pages = data.get('query', {}).get('pages', [])
        if not pages:
            return None
        
        page_data = pages[0]
        is_missing = page_data.get('missing', False)
        page_id = str(page_data.get('pageid', ''))
        
        if is_missing or not page_id or page_id == '-1':
            return None
        
        # Get revision info
        revisions = page_data.get('revisions', [])
        if not revisions or len(revisions) == 0:
            return None
        
        first_revision = revisions[0]
        article_author = first_revision.get('user')
        if not article_author:
            userid = first_revision.get('userid')
            if userid:
                article_author = f'User ID: {userid}'
            else:
                article_author = None
        
        return {
            'article_author': article_author,
            'article_created_at': first_revision.get('timestamp', ''),
            'article_word_count': first_revision.get('size', 0),
            'article_page_id': page_id
        }
        
    except Exception as e:
        print(f"Error fetching article info: {e}")
        return None

def backfill_submissions():
    """Backfill article information for submissions missing author or word count"""
    with app.app_context():
        # First, list all submissions to see what we have
        all_submissions = Submission.query.all()
        print(f"Total submissions in database: {len(all_submissions)}")
        for sub in all_submissions:
            print(f"  ID {sub.id}: author='{sub.article_author}', word_count={sub.article_word_count}, title='{sub.article_title}'")
        
        print("\n" + "=" * 60)
        
        # Find submissions that need backfilling
        # (missing author, author is "Unknown", or word_count is None/0)
        from sqlalchemy import or_
        submissions = Submission.query.filter(
            or_(
                Submission.article_author == None,
                Submission.article_author == '',
                Submission.article_author == 'Unknown',
                Submission.article_word_count == None,
                Submission.article_word_count == 0
            )
        ).all()
        
        print(f"Found {len(submissions)} submissions to backfill")
        print("=" * 60)
        
        updated = 0
        failed = 0
        
        for submission in submissions:
            print(f"\nProcessing submission {submission.id}: {submission.article_title}")
            print(f"  URL: {submission.article_link}")
            
            # Fetch article info
            info = fetch_article_info(submission.article_link)
            
            if info:
                # Update submission
                if info.get('article_author'):
                    submission.article_author = info['article_author']
                if info.get('article_created_at'):
                    submission.article_created_at = info['article_created_at']
                if info.get('article_word_count'):
                    submission.article_word_count = info['article_word_count']
                if info.get('article_page_id'):
                    submission.article_page_id = info['article_page_id']
                
                db.session.commit()
                updated += 1
                print(f"  [OK] Updated: author={info.get('article_author')}, word_count={info.get('article_word_count')}")
            else:
                failed += 1
                print(f"  [FAILED] Could not fetch article info (page may not exist)")
        
        print("\n" + "=" * 60)
        print(f"Backfill complete!")
        print(f"  Updated: {updated}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(submissions)}")

if __name__ == '__main__':
    backfill_submissions()

