# Gap Analysis Report

This report analyzes the current state of the WikiContest codebase against the requirements provided.

## Module Analysis

### 1. Core Setup & API Integration
**Status: Partially Implemented**
- **Implemented:**
  - OAuth 1.0a authentication (`mwoauth`) is fully implemented in `backend/app/routes/user_routes.py`.
  - Basic MediaWiki API integration (`requests`) exists for fetching article metadata (`backend/app/utils/__init__.py`).
- **Missing:**
  - **Category Crawling Logic:** There is no logic to automatically crawl a category (`categorymembers` API) to fetch articles. Submissions are currently manual (user provides a URL).
  - **Pagination Handling:** Logic to handle pagination for fetching large numbers of articles (e.g., 5,000) from a category is missing.
  - **Bot Account Setup:** While OAuth is present, the specific logic for a "Bot" that runs autonomously to process thousands of articles is not structured; the current app acts as a web platform for user interaction.

### 2. Config System
**Status: Partially Implemented**
- **Implemented:**
  - Configuration (dates, categories, point multipliers) is implemented via a **Database-driven** approach. Contests are created/edited via the Admin UI and stored in the `contests` table.
- **Missing:**
  - **On-Wiki Config Parsing:** The requirement to "read the config page" (parsing a MediaWiki page for config variables) is missing. The system currently relies on the API/Web UI for configuration, not an on-wiki syntax.

### 3. User Eligibility System
**Status: Partially Implemented**
- **Implemented:**
  - Logic exists to check if a user is a "Trusted Member" (creator) based on edit counts (`get_mediawiki_user_edit_count`).
- **Missing:**
  - **Submitter Whitelist:** Logic to gatekeep *participants* based on "user registration dates" or "project-specific edits" is missing. Currently, any authenticated user can submit articles.

### 4. Article Filtering (Gatekeeping)
**Status: Partially Implemented**
- **Implemented:**
  - **Creation Date:** Checks if article was created/expanded within contest dates.
  - **Minimum Requirements:** Checks for `min_byte_count` and `min_reference_count`.
- **Missing:**
  - **Author Whitelist:** Logic to check the article author against a specific whitelist is missing.
  - **Basic Links:** While reference count is checked, specific "basic links" requirements (beyond references) are not explicitly implemented.

### 5. Content Scoring (Data Collection)
**Status: Partially Implemented**
- **Implemented:**
  - Counts **bytes** and **words** via MediaWiki API metadata.
  - Checks **categories** (for enforcement).
- **Missing:**
  - **Infoboxes & Image Tags:** Logic to count the number of infoboxes and image tags in the article text is missing. The `Submission` model does not store these metrics.

### 6. Link Analysis (Inbound/Outbound)
**Status: Missing**
- **Missing:**
  - No logic found to query `backlinks` or `linkshere` APIs.
  - No logic to count "mainspace connections".

### 7. Reference Analysis
**Status: Partially Implemented**
- **Implemented:**
  - Counts total references (footnotes + external links) in `get_article_reference_count`.
- **Missing:**
  - **New vs. Reused:** Logic to distinguish between "new" references (added during the contest) and "reused" references (existing) is missing. It currently only counts the total present in the latest revision.

### 8. Reporting & Notifications
**Status: Missing**
- **Missing:**
  - **Wikitext Table Generation:** No logic found to generate a Wikitext report table.
  - **Daily Overwrite:** No scheduled task or logic to update an evaluation report page daily.
  - **Talk Page Alerts:** No logic to post notifications to User Talk pages.

### 9. Testing & Error Handling
**Status: Partially Implemented**
- **Implemented:**
  - Basic API error handling (timeouts, status codes) exists in `backend/app/utils/__init__.py`.
  - Database error handling exists.
- **Missing:**
  - **Large Scale Robustness:** Since the "crawler bot" aspect is missing, the specific handling for ensuring the bot doesn't crash during a 5,000-article run is not applicable/implemented.

## Good to Have Features

### Language Detection (English vs. Telugu)
**Status: Missing**
- No logic found for language detection or percentage calculation.

### Typo Inspection (AWB Typos list)
**Status: Missing**
- No logic or data files found for AWB typo checking.

### Source Link Analysis ("See also" vs "Body text")
**Status: Missing**
- No logic to parse article sections and distinguish link locations.

### Admin UI
**Status: Implemented**
- A comprehensive Web-based Dashboard (Vue.js) exists for creating and managing contests, which fulfills the "custom interface to edit the Config" requirement (albeit via DB, not on-wiki Config page).
