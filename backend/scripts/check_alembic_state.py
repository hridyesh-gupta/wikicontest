#!/usr/bin/env python3
"""
Check Alembic migration state and find the head revision.

This script helps diagnose Alembic issues by:
1. Checking what revision the database thinks it's at
2. Finding the actual head revision from migration files
3. Identifying any mismatches
"""

import sys
import os
import re
from pathlib import Path

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import create_app
from app.database import db

def find_all_revisions():
    """Find all revision IDs from migration files."""
    versions_dir = Path(backend_dir) / "alembic" / "versions"
    revisions = {}
    
    for migration_file in versions_dir.glob("*.py"):
        if migration_file.name == "__init__.py":
            continue
            
        content = migration_file.read_text()
        
        # Extract revision ID
        revision_match = re.search(r"revision\s*=\s*['\"]([a-f0-9]+)['\"]", content)
        if not revision_match:
            continue
            
        revision = revision_match.group(1)
        
        # Extract down_revision
        down_revision_match = re.search(r"down_revision\s*=\s*(?:\(|['\"]?)([a-f0-9,]+)(?:['\"]?|\))", content)
        down_revision = None
        if down_revision_match:
            down_rev_str = down_revision_match.group(1)
            # Handle tuple format for merge migrations
            if "," in down_rev_str:
                down_revision = tuple(d.strip().strip("'\"") for d in down_rev_str.split(","))
            else:
                down_revision = down_rev_str.strip().strip("'\"")
        
        revisions[revision] = {
            "file": migration_file.name,
            "down_revision": down_revision
        }
    
    return revisions

def find_head_revision(revisions):
    """Find the head revision (revision not referenced as down_revision by any other)."""
    # Get all revisions that are referenced as down_revisions
    referenced = set()
    for rev_data in revisions.values():
        down_rev = rev_data["down_revision"]
        if down_rev is None:
            continue
        if isinstance(down_rev, tuple):
            # Merge migration - all items in tuple are referenced
            referenced.update(down_rev)
        else:
            referenced.add(down_rev)
    
    # Head revisions are those not referenced by any other migration
    heads = [rev for rev in revisions.keys() if rev not in referenced]
    
    # If there are multiple heads, try to find the actual latest one
    # by following the chain from each head
    if len(heads) > 1:
        # Build a reverse map: revision -> migrations that point to it
        reverse_map = {}
        for rev, rev_data in revisions.items():
            down_rev = rev_data["down_revision"]
            if isinstance(down_rev, tuple):
                for dr in down_rev:
                    if dr not in reverse_map:
                        reverse_map[dr] = []
                    reverse_map[dr].append(rev)
            elif down_rev:
                if down_rev not in reverse_map:
                    reverse_map[down_rev] = []
                reverse_map[down_rev].append(rev)
        
        # Find the longest chain from each head
        def get_chain_length(rev, visited=None):
            if visited is None:
                visited = set()
            if rev in visited:
                return 0
            visited.add(rev)
            if rev not in reverse_map:
                return 1
            max_len = 1
            for next_rev in reverse_map[rev]:
                max_len = max(max_len, 1 + get_chain_length(next_rev, visited.copy()))
            return max_len
        
        # Sort heads by chain length (longest first)
        heads_with_length = [(rev, get_chain_length(rev)) for rev in heads]
        heads_with_length.sort(key=lambda x: x[1], reverse=True)
        
        # Return the head with the longest chain (most likely the actual head)
        return [h[0] for h in heads_with_length]
    
    return heads

def check_database_revision():
    """Check what revision the database thinks it's at."""
    app = create_app()
    with app.app_context():
        try:
            result = db.session.execute(db.text("SELECT version_num FROM alembic_version"))
            row = result.fetchone()
            if row:
                return row[0]
            return None
        except Exception as e:
            print(f"Error checking database revision: {e}")
            return None

def main():
    """Main function to check Alembic state."""
    print("Checking Alembic migration state...\n")
    
    # Find all revisions from migration files
    print("Scanning migration files...")
    revisions = find_all_revisions()
    print(f"Found {len(revisions)} migration files\n")
    
    # Find head revisions
    heads = find_head_revision(revisions)
    print(f"Head revision(s): {', '.join(heads) if heads else 'None found'}\n")
    
    # Check database state
    print("Checking database state...")
    db_revision = check_database_revision()
    if db_revision:
        print(f"Database revision: {db_revision}")
        if db_revision in revisions:
            print(f"  OK This revision exists in migration files")
        else:
            print(f"  X This revision does NOT exist in migration files!")
            print(f"    This is the problem - the database references a missing migration.")
    else:
        print("  No revision found in database (database may not be initialized)")
    
    print("\n" + "="*60)
    print("RECOMMENDATION:")
    print("="*60)
    
    if db_revision and db_revision not in revisions:
        if heads:
            print(f"\nThe database references revision '{db_revision}' which doesn't exist.")
            print(f"To fix this, update the database to a valid revision.")
            print(f"\nIf your database schema matches the current models, set it to the head:")
            if len(heads) == 1:
                print(f"\n  python scripts/fix_alembic_version.py {heads[0]}")
            else:
                print(f"\n  Multiple heads found. Choose one:")
                for head in heads:
                    print(f"    python scripts/fix_alembic_version.py {head}")
        else:
            print("\nCould not determine head revision. Please check migration files.")
    elif db_revision in revisions:
        print(f"\nDatabase is at a valid revision: {db_revision}")
        if heads and db_revision not in heads:
            print(f"To upgrade to head, run:")
            print(f"  alembic upgrade head")
    else:
        print("\nDatabase may need initialization. Run:")
        print(f"  alembic upgrade head")

if __name__ == '__main__':
    main()
