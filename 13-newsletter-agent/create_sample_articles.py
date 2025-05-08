#!/usr/bin/env python3
"""
Create sample articles file for quick testing
"""

import json
from google.adk.tools.tool_context import SimpleToolContext
from newsletter_agent.rss_tools import fetch_rss_articles

# Create context
context = SimpleToolContext()

# Fetch articles
print("Fetching articles...")
fetch_rss_articles(7, context)

# Get articles
articles = context.state.get('articles', [])[:20]
print(f"Got {len(articles)} articles")

# Save to file
with open('sample_articles.json', 'w') as f:
    json.dump(articles, f, indent=2)

print(f"Saved {len(articles)} articles to sample_articles.json")
