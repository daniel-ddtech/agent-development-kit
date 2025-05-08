# AI in Games Newsletter Agent

This agent helps automate the process of collecting articles about AI in games from Feedly and Google Search, and generating a weekly newsletter.

## Features

- Fetch articles from Feedly (currently mocked, can be replaced with actual API)
- Fetch articles from Google Search (currently mocked, can be replaced with actual API)
- View all collected articles
- Generate a newsletter draft
- Export the newsletter to different formats (markdown, json)
- Persistent storage of articles and newsletter drafts

## Getting Started

### Prerequisites

- Python 3.7+
- The dependencies from the main agent-development-kit

### Installation

This agent uses the same virtual environment as the main agent-development-kit. Make sure you have activated the virtual environment from the root directory:

```bash
# macOS/Linux:
source ../.venv/bin/activate
# Windows CMD:
..\.venv\Scripts\activate.bat
# Windows PowerShell:
..\.venv\Scripts\Activate.ps1
```

### Running the Agent

You can run the agent in two ways:

1. Using the main.py script (with persistent storage):
```bash
python main.py
```

2. Using the ADK CLI (without persistent storage):
```bash
adk web
```

Then access the web UI by opening the URL shown in your terminal (typically http://localhost:8000) and select "newsletter_agent" from the dropdown menu.

## Usage Examples

Here are some example prompts to try with the agent:

- "Fetch articles about AI in games from Feedly for the last 7 days"
- "Search for AI in games articles on Google from this week"
- "Show me all the articles you've collected"
- "Generate a newsletter draft titled 'Weekly AI in Games Update'"
- "Export the newsletter to markdown format"
- "Create a complete newsletter about AI in games for this week"

## Customization

### Adding Real API Integration

To replace the mock implementations with real API calls:

1. For Feedly:
   - Sign up for a Feedly Developer account
   - Get your API key
   - Update the `fetch_feedly_articles` function to use the Feedly API

2. For Google Search:
   - Set up a Google Custom Search Engine
   - Get your API key and search engine ID
   - Update the `fetch_google_articles` function to use the Google Custom Search API

### Scheduling

For full automation, you can set up a cron job or scheduled task to run the agent weekly:

```bash
# Example cron job to run every Monday at 9 AM
0 9 * * 1 cd /path/to/agent-development-kit/13-newsletter-agent && python main.py
```

## Notes

- This implementation uses a SQLite database for persistent storage
- The agent maintains state between sessions, so you can collect articles over time
- Currently, the article fetching is mocked - replace with actual API calls for production use
