# Google Spreadsheet Integration for Newsletter Agent

This document explains how to use the new Google Spreadsheet integration for collecting news articles for your newsletter generator.

## Overview

The newsletter agent now supports three sources of articles:
1. RSS feeds (existing functionality)
2. Perplexity API search (replacing mock Feedly and Google Search)
3. Google Spreadsheet (new functionality)

## Setup Instructions

### 1. Perplexity API Setup

1. Sign up for a Perplexity API account at [https://www.perplexity.ai/](https://www.perplexity.ai/)
2. Navigate to your API Group section in your Account page
3. Generate an API key
4. Add the API key to your `.env` file:
   ```
   PERPLEXITY_API_KEY=your_perplexity_api_key_here
   ```

### 2. Google Spreadsheet Setup

1. Create a Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Sheets API and Google Drive API

2. Create Service Account Credentials:
   - In your Google Cloud Project, go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in the details and create the service account
   - Create a key for the service account (JSON format)
   - Download the JSON key file and save it securely

3. Share your spreadsheet:
   - Share your Google Spreadsheet with the email address of the service account (it looks like: `service-account-name@project-id.iam.gserviceaccount.com`)
   - Give it at least "Viewer" access

4. Configure the environment:
   - Add the path to your credentials file in the `.env` file:
     ```
     GOOGLE_CREDENTIALS_FILE=path_to_your_credentials.json
     DEFAULT_SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/103g1TNDIyp1h0kiiZ43ReJWuUnrz_GGTNsFcrjjMxEE/edit?usp=sharing
     ```

## Spreadsheet Format

Your spreadsheet should have the following columns:
- **Title**: The title of the article
- **URL**: The URL of the article
- **Date**: The publication date (YYYY-MM-DD format preferred)
- **Source**: The source of the article
- **Summary**: A brief summary of the article

Example:

| Title | URL | Date | Source | Summary |
|-------|-----|------|--------|---------|
| AI Revolutionizes Game NPCs | https://example.com/article1 | 2025-05-10 | GameDev Magazine | This article discusses how AI is changing the way NPCs behave in modern games... |
| Procedural Generation with LLMs | https://example.com/article2 | 2025-05-12 | AI Weekly | Large language models are now being used to generate game content... |

## Using the Spreadsheet Integration

You can use the following commands with the agent:

1. Fetch articles from your spreadsheet:
   ```
   Fetch articles from our spreadsheet for the last 7 days
   ```

2. Specify a different spreadsheet:
   ```
   Fetch articles from spreadsheet https://docs.google.com/spreadsheets/d/your_spreadsheet_id/edit for the last 14 days
   ```

3. Create a complete newsletter using all sources:
   ```
   Create a complete newsletter about AI in games using RSS feeds, Perplexity search, and our spreadsheet
   ```

## Troubleshooting

- **Authentication Errors**: Make sure your credentials file is correct and the service account has access to the spreadsheet
- **Format Errors**: Ensure your spreadsheet has the expected column headers
- **Date Parsing Errors**: The system tries to parse several date formats, but using YYYY-MM-DD is recommended

## Notes

- The system will only fetch articles from the spreadsheet that are within the specified date range
- Articles are deduplicated based on URL to avoid repetition
- The first sheet in the spreadsheet is used by default
