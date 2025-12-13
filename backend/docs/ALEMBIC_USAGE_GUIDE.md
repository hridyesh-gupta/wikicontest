# Alembic Database Migrations

This directory contains Alembic migration scripts for the WikiContest application. Alembic is a database migration tool for SQLAlchemy that provides version control for database schemas.

## Overview

Alembic is configured to work with Flask's application factory pattern. The database URL is automatically retrieved from the Flask app configuration, so you don't need to set it manually in `alembic.ini`.

## Initial Setup

Alembic is already initialized. If you need to reinitialize:

```bash
alembic init alembic
```

## Creating Migrations

### Auto-generate Migration from Models

To create a new migration based on model changes:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Example:
alembic revision --autogenerate -m "Add user profile fields"
```

### Manual Migration

To create an empty migration file for manual SQL:

```bash
alembic revision -m "Description of changes"
```

Then edit the generated file in `alembic/versions/` to add your migration logic.

## Running Migrations

### Apply All Pending Migrations

```bash
# Upgrade to the latest version
alembic upgrade head

# Upgrade to a specific revision
alembic upgrade <revision_id>
```

### Rollback Migrations

```bash
# Rollback one revision
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

## Checking Migration Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

## Migration Workflow

1. **Make model changes** in `app/models/`
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Description"
   ```
3. **Review the generated migration** in `alembic/versions/`
4. **Test the migration**:
   ```bash
   alembic upgrade head
   ```
5. **Commit the migration file** to version control

## Important Notes

- **Always review auto-generated migrations** before applying them
- **Test migrations on a development database** first
- **Backup your database** before running migrations in production
- **Never edit existing migration files** that have been applied to production
- The database URL is read from Flask app configuration (`SQLALCHEMY_DATABASE_URI`)
- All models must be imported in `alembic/env.py` for autogenerate to work

## Configuration

The Alembic configuration is in:
- `alembic.ini` - Main configuration file
- `alembic/env.py` - Environment setup (connects to Flask app)

## Troubleshooting

### Migration Not Detecting Model Changes

Ensure all models are imported in `alembic/env.py`:
```python
from app.models.user import User
from app.models.contest import Contest
from app.models.submission import Submission
```

### Database Connection Errors

- Check that your `.env` file has the correct `DATABASE_URL`
- Verify the database server is running
- Ensure database credentials are correct

### Migration Conflicts

If you have conflicts with existing migrations:
1. Check current revision: `alembic current`
2. Review migration history: `alembic history`
3. Resolve conflicts manually or create a merge migration

## Best Practices

1. **One logical change per migration** - Keep migrations focused
2. **Use descriptive names** - Migration names should clearly describe the change
3. **Test both upgrade and downgrade** - Ensure migrations are reversible
4. **Don't modify applied migrations** - Create new migrations for fixes
5. **Use transactions** - Alembic wraps migrations in transactions by default
6. **Document complex migrations** - Add comments for non-obvious changes

## Integration with Existing Migrations

The project also has custom migration scripts in the `migrations/` directory. These can coexist with Alembic migrations:

- **Custom migrations** (`migrations/`): For one-time data migrations or complex changes
- **Alembic migrations** (`alembic/versions/`): For schema version control

For new schema changes, prefer Alembic migrations. Use custom scripts for data migrations or one-time operations.

