import os
import json
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Import our custom tools
from newsletter_agent.rss_tools import fetch_rss_articles
from newsletter_agent.curator_tools import curate_articles, get_trending_topics
from newsletter_agent.summarizer_tools import summarize_articles
from newsletter_agent.category_tools import categorize_articles
from newsletter_agent.llm_formatter import generate_newsletter_with_llm
from newsletter_agent.rating_system import rate_articles, add_ratings_to_newsletter

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("ERROR: GOOGLE_API_KEY not found in environment variables. LLM formatting will not work.")
    exit(1)

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

# We'll also add a function to scrape FutureTools.io since they don't have an RSS feed
def fetch_futuretools_news(days=7):
    """
    Scrape news from FutureTools.io
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of article dictionaries
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        from datetime import datetime, timedelta
        
        # Get the current date and the date 'days' days ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch the FutureTools.io news page
        response = requests.get("https://www.futuretools.io/news")
        if response.status_code != 200:
            print(f"Error fetching FutureTools.io: {response.status_code}")
            return []
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all news articles
        articles = []
        news_links = soup.find_all('a', href=True)
        
        for link in news_links:
            # Skip navigation links
            if not link.text or link.text in ['Terms Of Use', 'Privacy Policy', 'Built by Matt Wolfe']:
                continue
                
            # Extract article information
            title = link.text.strip()
            url = link['href']
            
            # Extract source from URL
            source = "Unknown"
            if "utm_source=futuretools.io" in url:
                # Extract the base URL
                base_url = url.split("?")[0]
                # Try to extract domain
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(base_url).netloc
                    source = domain
                except:
                    source = "FutureTools.io"
            
            # We don't have exact publish dates from the scrape, so we'll assume all are recent
            # and rely on our curation to filter for relevance
            article = {
                "title": title,
                "url": url,
                "source": source,
                "published": end_date.strftime("%Y-%m-%d"),
                "summary": f"From FutureTools.io: {title}",
                "content": "",
                "keywords": ["ai", "artificial intelligence", "machine learning"]
            }
            
            articles.append(article)
        
        print(f"Found {len(articles)} articles from FutureTools.io")
        return articles
    except Exception as e:
        print(f"Error scraping FutureTools.io: {str(e)}")
        return []

def main():
    print("\n=== AI in Gaming Newsletter Generator (With Content Rating) ===\n")
    
    # Initialize tool context with initial state
    context = SimpleToolContext({
        "articles": [],
        "rss_articles": [],
        "rss_feeds": rss_feeds,
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "date": datetime.now().strftime("%Y-%m-%d"),
    })
    
    # Step 1: Fetch articles from RSS feeds and FutureTools.io (last 7 days only)
    print("Step 1: Fetching articles from sources (last 7 days)...")
    days_to_fetch = 7  # Explicitly set to fetch only the last week
    
    # Fetch from RSS feeds
    result = fetch_rss_articles(rss_feeds, days_to_fetch, context)
    rss_article_count = len(context.state.get("rss_articles", []))
    print(f"  {result['message']}")
    
    # Fetch from FutureTools.io
    print("  Fetching from FutureTools.io...")
    futuretools_articles = fetch_futuretools_news(days_to_fetch)
    
    # Add FutureTools articles to the state
    if futuretools_articles:
        all_articles = context.state.get("rss_articles", []) + futuretools_articles
        context.state["rss_articles"] = all_articles
        print(f"  Added {len(futuretools_articles)} articles from FutureTools.io")
    
    total_articles = len(context.state.get("rss_articles", []))
    print(f"  Total articles fetched: {total_articles}")
    print(f"  Time period: Last {days_to_fetch} days")
    
    # Step 2: Curate articles
    print("\nStep 2: Curating articles...")
    curation_criteria = {
        "keywords": [
            "generative AI", "gen AI", "diffusion model", "large language model", 
            "AI in games", "game development", "NPC", "character behavior",
            "funding", "investment", "regulation", "policy"
        ],
        "min_score": 2,  # Lower threshold to ensure we get some results
        "max_articles": 15  # Limit to 15 articles to stay within API quota
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
    
    # Step 6: Rate articles
    print("\nStep 6: Rating article content...")
    result = rate_articles(context)
    print(f"  {result['message']}")
    
    if result['status'] == 'success' and 'category_ratings' in result:
        print("  Category ratings:")
        for category, rating in result['category_ratings'].items():
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            print(f"    - {category}: {rating}/5 {stars}")
    
    # Step 7: Generate newsletter with LLM
    print("\nStep 7: Generating newsletter with LLM...")
    result = generate_newsletter_with_llm(context)
    print(f"  {result['message']}")
    
    # Step 8: Add ratings to newsletter
    print("\nStep 8: Adding ratings to newsletter...")
    result = add_ratings_to_newsletter(context)
    print(f"  {result['message']}")
    
    # Save the newsletter to a file
    newsletter_file = f"newsletter_rated_{datetime.now().strftime('%Y%m%d')}.md"
    with open(newsletter_file, "w") as f:
        f.write(context.state.get("rated_newsletter", "No newsletter generated"))
    
    print(f"\nRated newsletter saved to {newsletter_file}")
    
    # Print a sample of the newsletter
    print("\nNewsletter Preview:")
    print("-" * 80)
    preview = context.state.get("rated_newsletter", "No newsletter generated")
    print(preview[:800] + "..." if len(preview) > 800 else preview)
    print("-" * 80)

if __name__ == "__main__":
    main()
