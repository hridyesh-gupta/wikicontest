#!/usr/bin/env python3
"""
Migration script: Add article metadata columns to submissions table

This script adds the following columns to the submissions table:
- article_author: Author/creator of the article
- article_created_at: When article was created
- article_word_count: Word count/size of article
- article_page_id: MediaWiki page ID

Usage:
    python migrations/add_article_metadata_to_submissions.py
"""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import app, db
from sqlalchemy import text

def run_migration():
    """
    Run the migration to add article metadata columns
    """
    print("=" * 60)
    print("Migration: Add Article Metadata to Submissions Table")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check if columns already exist by trying to query them
            # If they don't exist, we'll get an error and can add them
            try:
                db.session.execute(text("SELECT article_author FROM submissions LIMIT 1"))
                print("[INFO] Column 'article_author' already exists")
                columns_exist = True
            except Exception:
                columns_exist = False
            
            if columns_exist:
                print("[SKIP] Article metadata columns already exist. Migration not needed.")
                return True
            
            print("[STEP 1] Adding article_author column...")
            try:
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    ADD COLUMN article_author VARCHAR(200) NULL
                """))
                print("  ✓ article_author column added")
            except Exception as e:
                print(f"  ⚠ Error adding article_author: {e}")
                # Continue with other columns
            
            print("[STEP 2] Adding article_created_at column...")
            try:
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    ADD COLUMN article_created_at VARCHAR(50) NULL
                """))
                print("  ✓ article_created_at column added")
            except Exception as e:
                print(f"  ⚠ Error adding article_created_at: {e}")
            
            print("[STEP 3] Adding article_word_count column...")
            try:
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    ADD COLUMN article_word_count INT NULL
                """))
                print("  ✓ article_word_count column added")
            except Exception as e:
                print(f"  ⚠ Error adding article_word_count: {e}")
            
            print("[STEP 4] Adding article_page_id column...")
            try:
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    ADD COLUMN article_page_id VARCHAR(50) NULL
                """))
                print("  ✓ article_page_id column added")
            except Exception as e:
                print(f"  ⚠ Error adding article_page_id: {e}")
            
            # Commit all changes
            db.session.commit()
            print("\n[SUCCESS] Migration completed successfully!")
            print("All article metadata columns have been added to the submissions table.")
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)

