# Database Migrations

This directory contains database migration scripts for the WikiContest application.

## Migration: Add Article Metadata to Submissions

**File**: `add_article_metadata_to_submissions.py` and `add_article_metadata_to_submissions.sql`

**Purpose**: Adds new columns to the `submissions` table to store article metadata fetched from MediaWiki API:
- `article_author` - Author/creator of the article
- `article_created_at` - When article was created
- `article_word_count` - Word count/size of article
- `article_page_id` - MediaWiki page ID

## Automatic Migration

The application will automatically run this migration on startup if the columns don't exist. You don't need to run it manually unless you prefer to do so.

## Manual Migration

If you want to run the migration manually, you have two options:

### Option 1: Python Script (Recommended)

```bash
cd backend
python migrations/add_article_metadata_to_submissions.py
```

### Option 2: SQL Script

If you're using MySQL directly:

```bash
mysql -u root -p wikicontest < migrations/add_article_metadata_to_submissions.sql
```

## Notes

- All new columns are **nullable**, so existing submissions will continue to work
- The migration is **safe to run multiple times** - it checks if columns exist before adding them
- If you're starting with a fresh database, `db.create_all()` will create the columns automatically

