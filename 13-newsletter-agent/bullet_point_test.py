import os
import json
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
import requests

# Import our custom tools
from newsletter_agent.rss_tools import fetch_rss_articles
from newsletter_agent.curator_tools import curate_articles, get_trending_topics
from newsletter_agent.summarizer_tools import summarize_articles, generate_intro
from newsletter_agent.category_tools import categorize_articles, format_bullet_points

# Simple tool context to mimic the ADK's ToolContext
class SimpleToolContext:
    def __init__(self, initial_state=None):
        self.state = initial_state or {}

# List of RSS feeds for AI in gaming
rss_feeds = [
    # Game development news
    "https://www.gamedeveloper.com/rss.xml",
    "https://venturebeat.com/category/games/feed/",
    
    # Generative AI news
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
    
    # AI and gaming news
    "https://www.engadget.com/tag/gaming/rss.xml",
    "https://www.polygon.com/rss/index.xml",
    
    # Tech and business news
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://cloud.google.com/blog/feed/"
]

def main():
    print("\n=== AI in Gaming Newsletter Generator (Bullet Point Format) ===\n")
    
    # Initialize tool context with initial state
    context = SimpleToolContext({
        "articles": [],
        "rss_articles": [],
        "rss_feeds": rss_feeds,
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "date": datetime.now().strftime("%Y-%m-%d"),
    })
    
    # Step 1: Fetch articles from RSS feeds
    print("Step 1: Fetching articles from RSS feeds...")
    result = fetch_rss_articles(rss_feeds, 7, context)
    print(f"  {result['message']}")
    
    # Step 2: Curate articles
    print("\nStep 2: Curating articles...")
    curation_criteria = {
        "keywords": [
            "generative AI", "gen AI", "diffusion model", "large language model", 
            "AI in games", "game development", "NPC", "character behavior",
            "funding", "investment", "regulation", "policy"
        ],
        "min_score": 2,  # Lower threshold to ensure we get some results
        "max_articles": 20  # Increase to get more articles for categories
    }
    result = curate_articles(curation_criteria, context)
    print(f"  {result['message']}")
    
    # Step 3: Identify trending topics
    print("\nStep 3: Identifying trending topics...")
    result = get_trending_topics(context)
    print(f"  {result['message']}")
    if result['topics']:
        print("  Trending topics:")
        for topic in result['topics']:
            print(f"    - {topic['topic'].replace('_', ' ').title()}")
    
    # Step 4: Generate summaries
    print("\nStep 4: Generating article summaries...")
    result = summarize_articles("professional", context)
    print(f"  {result['message']}")
    
    # Step 5: Categorize articles
    print("\nStep 5: Categorizing articles...")
    result = categorize_articles(context)
    print(f"  {result['message']}")
    print("  Categories:")
    for category, count in result['category_counts'].items():
        if count > 0:
            print(f"    - {category}: {count} articles")
    
    # Step 6: Format as bullet points
    print("\nStep 6: Formatting newsletter as bullet points...")
    result = format_bullet_points(context)
    print(f"  {result['message']}")
    
    # Save the newsletter to a file
    newsletter_file = f"newsletter_bullets_{datetime.now().strftime('%Y%m%d')}.md"
    with open(newsletter_file, "w") as f:
        f.write(context.state.get("bullet_point_newsletter", "No newsletter generated"))
    
    print(f"\nNewsletter saved to {newsletter_file}")
    
    # Print a sample of the newsletter
    print("\nNewsletter Preview:")
    print("-" * 80)
    preview = context.state.get("bullet_point_newsletter", "No newsletter generated")
    print(preview[:800] + "..." if len(preview) > 800 else preview)
    print("-" * 80)

if __name__ == "__main__":
    main()
