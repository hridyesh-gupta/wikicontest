#!/usr/bin/env python3
"""
Script to set or update template_link for a contest.

Usage:
    python set_contest_template_link.py <contest_id> <template_url>

Example:
    python set_contest_template_link.py 1 "https://en.wikipedia.org/wiki/Template:Editathon2025"
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import db
from app.models.contest import Contest
from app.utils import validate_template_link


def set_contest_template_link(contest_id, template_url):
    """
    Set template_link for a contest.
    
    Args:
        contest_id: ID of the contest to update
        template_url: Template URL to set (must be a valid Wiki template page)
    
    Returns:
        bool: True if successful, False otherwise
    """
    app = create_app()
    
    with app.app_context():
        # Get contest from database
        contest = Contest.query.get(contest_id)
        if not contest:
            print(f"Error: Contest with ID {contest_id} not found.")
            return False
        
        print(f"Found contest: {contest.name} (ID: {contest.id})")
        print(f"Current template_link: {contest.template_link}")
        
        # Validate template URL if provided
        if template_url:
            template_url = template_url.strip()
            if template_url:
                print(f"\nValidating template URL: {template_url}")
                validation_result = validate_template_link(template_url)
                
                if not validation_result['valid']:
                    print(f"Error: Invalid template link: {validation_result['error']}")
                    return False
                
                print(f"✓ Template URL is valid")
                print(f"  Template name: {validation_result.get('template_name', 'N/A')}")
                print(f"  Page exists: {validation_result.get('page_exists', False)}")
                print(f"  Is template: {validation_result.get('is_template', False)}")
        
        # Update template_link
        if template_url:
            contest.template_link = template_url
            print(f"\nSetting template_link to: {template_url}")
        else:
            contest.template_link = None
            print(f"\nClearing template_link (setting to None)")
        
        # Save to database
        try:
            db.session.commit()
            print(f"✓ Successfully updated contest {contest_id}")
            print(f"  New template_link: {contest.template_link}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error: Failed to update contest: {str(e)}")
            return False


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 3:
        print("Usage: python set_contest_template_link.py <contest_id> <template_url>")
        print("\nExample:")
        print('  python set_contest_template_link.py 1 "https://en.wikipedia.org/wiki/Template:Editathon2025"')
        print("\nTo clear template_link:")
        print('  python set_contest_template_link.py 1 ""')
        sys.exit(1)
    
    try:
        contest_id = int(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid contest ID: {sys.argv[1]}")
        print("Contest ID must be a number.")
        sys.exit(1)
    
    template_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = set_contest_template_link(contest_id, template_url)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

