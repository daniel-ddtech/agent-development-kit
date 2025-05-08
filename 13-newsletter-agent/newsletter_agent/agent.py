from datetime import datetime, timedelta
import json
import os
import requests
from typing import Optional, List, Dict, Any

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext

# Import custom tools
from .rss_tools import fetch_rss_articles, manage_feeds
from .curator_tools import curate_articles, get_trending_topics
from .summarizer_tools import summarize_articles, generate_intro
from .formatter_tools import format_newsletter


def fetch_feedly_articles(query: str, days: int, tool_context: ToolContext) -> dict:
    """Fetch recent articles from Feedly based on a query.
    
    Args:
        query: The search query (e.g., "AI in games")
        days: Number of days to look back
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with fetched articles
    """
    print(f"--- Tool: fetch_feedly_articles called for '{query}' (last {days} days) ---")
    
    # Get current articles from state or initialize empty list
    articles = tool_context.state.get("articles", [])
    feedly_articles = tool_context.state.get("feedly_articles", [])
    
    # In a real implementation, you would use the Feedly API here
    # This is a placeholder implementation
    # Example: https://developer.feedly.com/v3/search/
    
    # Mock fetching articles from Feedly
    # In production, replace with actual API call
    mock_feedly_articles = [
        {
            "id": "feedly_1",
            "title": f"[FEEDLY] New AI Game Development Techniques - {datetime.now().strftime('%Y-%m-%d')}",
            "url": "https://example.com/ai-game-dev",
            "published": datetime.now().strftime("%Y-%m-%d"),
            "source": "Feedly",
            "summary": "Recent advancements in AI for game development..."
        },
        {
            "id": "feedly_2",
            "title": f"[FEEDLY] Machine Learning in Gaming - {datetime.now().strftime('%Y-%m-%d')}",
            "url": "https://example.com/ml-gaming",
            "published": datetime.now().strftime("%Y-%m-%d"),
            "source": "Feedly",
            "summary": "How machine learning is transforming gaming experiences..."
        }
    ]
    
    # Store the fetched articles in state
    feedly_articles = mock_feedly_articles
    tool_context.state["feedly_articles"] = feedly_articles
    
    # Merge with existing articles (avoiding duplicates by ID)
    existing_ids = {article["id"] for article in articles}
    for article in feedly_articles:
        if article["id"] not in existing_ids:
            articles.append(article)
            existing_ids.add(article["id"])
    
    # Update the combined articles in state
    tool_context.state["articles"] = articles
    
    return {
        "action": "fetch_feedly_articles",
        "query": query,
        "days": days,
        "articles_found": len(feedly_articles),
        "total_articles": len(articles),
        "message": f"Found {len(feedly_articles)} articles from Feedly for '{query}' in the last {days} days."
    }


def fetch_google_articles(query: str, days: int, tool_context: ToolContext) -> dict:
    """Fetch recent articles from Google Search based on a query.
    
    Args:
        query: The search query (e.g., "AI in games")
        days: Number of days to look back
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with fetched articles
    """
    print(f"--- Tool: fetch_google_articles called for '{query}' (last {days} days) ---")
    
    # Get current articles from state or initialize empty list
    articles = tool_context.state.get("articles", [])
    google_articles = tool_context.state.get("google_articles", [])
    
    # In a real implementation, you would use the Google Custom Search API here
    # This is a placeholder implementation
    # Example: https://developers.google.com/custom-search/v1/overview
    
    # Mock fetching articles from Google
    # In production, replace with actual API call
    mock_google_articles = [
        {
            "id": "google_1",
            "title": f"[GOOGLE] AI Revolution in Gaming Industry - {datetime.now().strftime('%Y-%m-%d')}",
            "url": "https://example.com/ai-revolution-gaming",
            "published": datetime.now().strftime("%Y-%m-%d"),
            "source": "Google Search",
            "summary": "The gaming industry is experiencing an AI revolution..."
        },
        {
            "id": "google_2",
            "title": f"[GOOGLE] Procedural Generation with AI - {datetime.now().strftime('%Y-%m-%d')}",
            "url": "https://example.com/procedural-ai",
            "published": datetime.now().strftime("%Y-%m-%d"),
            "source": "Google Search",
            "summary": "How AI is enabling more sophisticated procedural generation in games..."
        }
    ]
    
    # Store the fetched articles in state
    google_articles = mock_google_articles
    tool_context.state["google_articles"] = google_articles
    
    # Merge with existing articles (avoiding duplicates by ID)
    existing_ids = {article["id"] for article in articles}
    for article in google_articles:
        if article["id"] not in existing_ids:
            articles.append(article)
            existing_ids.add(article["id"])
    
    # Update the combined articles in state
    tool_context.state["articles"] = articles
    
    return {
        "action": "fetch_google_articles",
        "query": query,
        "days": days,
        "articles_found": len(google_articles),
        "total_articles": len(articles),
        "message": f"Found {len(google_articles)} articles from Google for '{query}' in the last {days} days."
    }


def view_articles(tool_context: ToolContext) -> dict:
    """View all collected articles.
    
    Args:
        tool_context: Context for accessing session state
        
    Returns:
        A dictionary with all articles
    """
    print("--- Tool: view_articles called ---")
    
    # Get articles from state
    articles = tool_context.state.get("articles", [])
    
    return {
        "action": "view_articles",
        "articles": articles,
        "count": len(articles),
        "message": f"Found {len(articles)} total articles."
    }


def generate_newsletter_draft(title: str, tool_context: ToolContext) -> dict:
    """Generate a draft newsletter from collected articles.
    
    Args:
        title: The title for the newsletter
        tool_context: Context for accessing session state
        
    Returns:
        A dictionary with the newsletter draft
    """
    print(f"--- Tool: generate_newsletter_draft called with title '{title}' ---")
    
    # Get articles from state
    articles = tool_context.state.get("articles", [])
    
    # Get the current date for the newsletter
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create a simple newsletter draft
    newsletter_draft = {
        "title": title,
        "date": current_date,
        "intro": f"Welcome to this week's AI in Games newsletter! Here are the top stories for {current_date}:",
        "articles": articles,
        "conclusion": "That's all for this week! Stay tuned for more AI in games news next week."
    }
    
    # Store the newsletter draft in state
    tool_context.state["newsletter_draft"] = newsletter_draft
    
    return {
        "action": "generate_newsletter_draft",
        "title": title,
        "article_count": len(articles),
        "date": current_date,
        "message": f"Generated newsletter draft titled '{title}' with {len(articles)} articles."
    }


def export_newsletter(format: str, tool_context: ToolContext) -> dict:
    """Export the newsletter draft to a specific format.
    
    Args:
        format: The format to export to (e.g., "markdown", "json")
        tool_context: Context for accessing session state
        
    Returns:
        A dictionary with the exported newsletter
    """
    print(f"--- Tool: export_newsletter called with format '{format}' ---")
    
    # Get newsletter draft from state
    newsletter_draft = tool_context.state.get("newsletter_draft", {})
    
    if not newsletter_draft:
        return {
            "action": "export_newsletter",
            "format": format,
            "success": False,
            "message": "No newsletter draft found. Please generate a draft first."
        }
    
    # Export based on format
    if format.lower() == "markdown":
        # Create a markdown version of the newsletter
        markdown_content = f"# {newsletter_draft.get('title', 'AI in Games Newsletter')}\n\n"
        markdown_content += f"*{newsletter_draft.get('date', datetime.now().strftime('%Y-%m-%d'))}*\n\n"
        markdown_content += f"{newsletter_draft.get('intro', '')}\n\n"
        
        # Add articles
        for i, article in enumerate(newsletter_draft.get('articles', []), 1):
            markdown_content += f"## {i}. {article.get('title', 'Untitled')}\n\n"
            markdown_content += f"*Source: {article.get('source', 'Unknown')} - {article.get('published', 'Unknown date')}*\n\n"
            markdown_content += f"{article.get('summary', 'No summary available.')}\n\n"
            markdown_content += f"[Read more]({article.get('url', '#')})\n\n"
        
        markdown_content += f"{newsletter_draft.get('conclusion', '')}\n"
        
        # Store the exported content
        tool_context.state["exported_newsletter"] = markdown_content
        
        return {
            "action": "export_newsletter",
            "format": format,
            "success": True,
            "content": markdown_content,
            "message": f"Exported newsletter to {format} format."
        }
    
    elif format.lower() == "json":
        # Export as JSON
        json_content = json.dumps(newsletter_draft, indent=2)
        
        # Store the exported content
        tool_context.state["exported_newsletter"] = json_content
        
        return {
            "action": "export_newsletter",
            "format": format,
            "success": True,
            "content": json_content,
            "message": f"Exported newsletter to {format} format."
        }
    
    else:
        return {
            "action": "export_newsletter",
            "format": format,
            "success": False,
            "message": f"Unsupported format: {format}. Supported formats are 'markdown' and 'json'."
        }


# Create the source agent for fetching articles
source_agent = Agent(
    name="source_agent",
    model="gemini-2.0-flash",
    description="Fetches articles from multiple sources",
    instruction="""
    You are responsible for fetching articles about AI in gaming from multiple sources.
    
    First, check if there are RSS feeds configured using the manage_feeds tool.
    If no feeds are configured, suggest some relevant AI and gaming RSS feeds to the user.
    
    Use the fetch_rss_articles tool to collect articles from RSS feeds.
    Use the fetch_google_articles tool to collect articles from Google Search.
    
    Make sure to fetch articles from the last 7 days by default, unless specified otherwise.
    """,
    tools=[
        manage_feeds,
        fetch_rss_articles,
        fetch_google_articles,
        view_articles,
    ],
)

# Create the curator agent for filtering and ranking articles
curator_agent = Agent(
    name="curator_agent",
    model="gemini-2.0-flash",
    description="Filters and ranks articles by relevance",
    instruction="""
    You are responsible for filtering and ranking articles based on relevance to AI in gaming.
    
    Use the curate_articles tool to filter and rank the articles based on keywords and other criteria.
    Use the get_trending_topics tool to identify trending topics from the curated articles.
    
    Make sure to prioritize articles about AI applications in game development, NPCs, procedural generation,
    and player experience personalization.
    """,
    tools=[
        curate_articles,
        get_trending_topics,
        view_articles,
    ],
)

# Create the summarizer agent for generating concise summaries
summarizer_agent = Agent(
    name="summarizer_agent",
    model="gemini-2.0-flash",
    description="Generates concise summaries for articles",
    instruction="""
    You are responsible for generating concise, engaging summaries for articles.
    
    Use the summarize_articles tool to create LinkedIn-style headlines for each article.
    Use the generate_intro tool to create an introduction for the newsletter.
    
    Make sure to maintain a consistent tone throughout the summaries.
    """,
    tools=[
        summarize_articles,
        generate_intro,
        view_articles,
    ],
)

# Create the formatter agent for generating the final newsletter
formatter_agent = Agent(
    name="formatter_agent",
    model="gemini-2.0-flash",
    description="Formats the newsletter for different platforms",
    instruction="""
    You are responsible for formatting the newsletter into different formats.
    
    Use the format_newsletter tool to generate the newsletter in the requested format.
    Supported formats are markdown, HTML, and JSON.
    
    Make sure the newsletter is well-structured and ready for publishing.
    """,
    tools=[
        format_newsletter,
        export_newsletter,
    ],
)

# Create the main newsletter agent with all tools
newsletter_agent = Agent(
    name="newsletter_agent",
    model="gemini-2.0-flash",
    description="AI in Gaming Newsletter Generator",
    instruction="""
    You are a helpful assistant that manages an "AI in Games" newsletter.
    
    You can help users collect articles about AI in games from different sources and generate a newsletter.
    
    You have the following capabilities:
    1. Manage RSS feeds to track (add, remove, list)
    2. Fetch articles from RSS feeds and Google Search
    3. Filter and rank articles by relevance
    4. Generate concise summaries in a consistent tone
    5. Format the newsletter for different platforms (markdown, HTML, JSON)
    
    When the user wants to create a newsletter, guide them through the process:
    1. First make sure there are RSS feeds configured using manage_feeds
    2. Fetch articles using fetch_rss_articles and fetch_google_articles
    3. Curate the most relevant articles using curate_articles
    4. Generate summaries with summarize_articles and an introduction with generate_intro
    5. Format the newsletter using format_newsletter
    
    Always be helpful and guide the user through the process of creating their newsletter.
    """,
    tools=[
        # Source tools
        manage_feeds,
        fetch_rss_articles,
        fetch_google_articles,
        
        # Curator tools
        curate_articles,
        get_trending_topics,
        
        # Summarizer tools
        summarize_articles,
        generate_intro,
        
        # Formatter tools
        format_newsletter,
        export_newsletter,
        
        # Utility tools
        view_articles,
    ],
)
