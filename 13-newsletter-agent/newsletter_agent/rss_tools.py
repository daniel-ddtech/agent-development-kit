import feedparser
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext


def fetch_rss_articles(feed_urls: List[str], days: int, tool_context: ToolContext) -> dict:
    """Fetch recent articles from RSS feeds.
    
    Args:
        feed_urls: List of RSS feed URLs to fetch
        days: Number of days to look back
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with fetched articles
    """
    print(f"--- Tool: fetch_rss_articles called for {len(feed_urls)} feeds (last {days} days) ---")
    
    # Get current articles from state or initialize empty list
    articles = tool_context.state.get("articles", [])
    rss_articles = tool_context.state.get("rss_articles", [])
    
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Fetch and parse each feed
    new_articles = []
    for feed_url in feed_urls:
        try:
            # Parse the feed
            feed = feedparser.parse(feed_url)
            feed_title = feed.get('feed', {}).get('title', 'Unknown Source')
            
            # Process each entry
            for entry in feed.entries:
                # Get publication date
                published_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_date = datetime(*entry.updated_parsed[:6])
                else:
                    # If no date, assume it's recent
                    published_date = datetime.now()
                
                # Skip if older than cutoff date
                if published_date < cutoff_date:
                    continue
                
                # Extract summary/content
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = entry.summary
                elif hasattr(entry, 'content'):
                    summary = entry.content[0].value
                
                # Clean HTML from summary
                if summary:
                    soup = BeautifulSoup(summary, 'html.parser')
                    summary = soup.get_text(separator=' ', strip=True)
                
                # Create article object
                article = {
                    "id": entry.get('id', entry.get('link', '')),
                    "title": entry.get('title', 'Untitled'),
                    "url": entry.get('link', ''),
                    "published": published_date.strftime("%Y-%m-%d"),
                    "source": feed_title,
                    "summary": summary[:500] + ('...' if len(summary) > 500 else '')
                }
                
                new_articles.append(article)
        
        except Exception as e:
            print(f"Error fetching feed {feed_url}: {str(e)}")
    
    # Store the fetched articles in state
    rss_articles = new_articles
    tool_context.state["rss_articles"] = rss_articles
    
    # Merge with existing articles (avoiding duplicates by ID)
    existing_ids = {article["id"] for article in articles}
    for article in rss_articles:
        if article["id"] not in existing_ids:
            articles.append(article)
            existing_ids.add(article["id"])
    
    # Update the combined articles in state
    tool_context.state["articles"] = articles
    
    return {
        "action": "fetch_rss_articles",
        "feeds_processed": len(feed_urls),
        "articles_found": len(rss_articles),
        "total_articles": len(articles),
        "message": f"Found {len(rss_articles)} articles from {len(feed_urls)} RSS feeds in the last {days} days."
    }


def manage_feeds(action: str, tool_context: ToolContext, feed_url: str = None) -> dict:
    """Manage the list of RSS feeds to track.
    
    Args:
        action: The action to perform ('add', 'remove', 'list')
        feed_url: The URL of the RSS feed (for add/remove actions)
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with the result of the action
    """
    # Get current feeds from state or initialize empty list
    feeds = tool_context.state.get("rss_feeds", [])
    
    if action.lower() == 'add' and feed_url:
        # Check if feed already exists
        if feed_url in feeds:
            return {
                "action": "manage_feeds",
                "status": "unchanged",
                "message": f"Feed {feed_url} already exists."
            }
        
        # Add the feed
        feeds.append(feed_url)
        tool_context.state["rss_feeds"] = feeds
        
        return {
            "action": "manage_feeds",
            "status": "added",
            "feed_count": len(feeds),
            "message": f"Added feed {feed_url}. Total feeds: {len(feeds)}"
        }
    
    elif action.lower() == 'remove' and feed_url:
        # Check if feed exists
        if feed_url not in feeds:
            return {
                "action": "manage_feeds",
                "status": "unchanged",
                "message": f"Feed {feed_url} not found."
            }
        
        # Remove the feed
        feeds.remove(feed_url)
        tool_context.state["rss_feeds"] = feeds
        
        return {
            "action": "manage_feeds",
            "status": "removed",
            "feed_count": len(feeds),
            "message": f"Removed feed {feed_url}. Total feeds: {len(feeds)}"
        }
    
    elif action.lower() == 'list':
        return {
            "action": "manage_feeds",
            "status": "listed",
            "feeds": feeds,
            "feed_count": len(feeds),
            "message": f"Currently tracking {len(feeds)} feeds."
        }
    
    else:
        return {
            "action": "manage_feeds",
            "status": "error",
            "message": f"Invalid action: {action}. Valid actions are 'add', 'remove', and 'list'."
        }
