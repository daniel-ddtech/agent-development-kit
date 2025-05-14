import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext
from openai import OpenAI

def fetch_perplexity_articles(query: str, days: int, tool_context: ToolContext) -> dict:
    """Fetch recent articles using Perplexity API based on a query.
    
    Args:
        query: The search query (e.g., "AI in games")
        days: Number of days to look back
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with fetched articles
    """
    print(f"--- Tool: fetch_perplexity_articles called for '{query}' (last {days} days) ---")
    
    # Get current articles from state or initialize empty list
    articles = tool_context.state.get("articles", [])
    perplexity_articles = tool_context.state.get("perplexity_articles", [])
    
    # Get API key from environment variable
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {
            "action": "fetch_perplexity_articles",
            "status": "error",
            "message": "PERPLEXITY_API_KEY environment variable not set."
        }
    
    # Calculate date range for search
    current_date = datetime.now()
    past_date = current_date - timedelta(days=days)
    date_range = f"after:{past_date.strftime('%Y-%m-%d')}"
    
    try:
        # Initialize OpenAI client with Perplexity base URL
        client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        
        # Construct the search query with date range
        search_query = f"{query} {date_range}"
        
        # Create messages for the API call
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a research assistant that finds recent articles about a specific topic. "
                    "For each article, provide the title, URL, publication date, source name, and a brief summary. "
                    "Format your response as a JSON array with objects containing these fields: "
                    "title, url, published_date, source, and summary. "
                    "Ensure all dates are in YYYY-MM-DD format. "
                    "Find at least 5 relevant articles if available."
                )
            },
            {
                "role": "user",
                "content": f"Find recent articles about: {search_query}"
            }
        ]
        
        # Make the API call
        response = client.chat.completions.create(
            model="sonar-pro",  # Using the search-optimized model
            messages=messages,
            temperature=0.0,  # Lower temperature for more factual responses
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        # Parse the JSON response
        # Note: We need to handle potential JSON parsing issues
        try:
            # Try to extract JSON from the response if it's not pure JSON
            if not content.strip().startswith('['):
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
            
            # Parse the JSON content
            article_data = json.loads(content)
            
            # Process the articles
            new_articles = []
            for idx, item in enumerate(article_data):
                article = {
                    "id": f"perplexity_{idx}_{item.get('url', '')}",
                    "title": item.get('title', 'Untitled'),
                    "url": item.get('url', ''),
                    "published": item.get('published_date', current_date.strftime("%Y-%m-%d")),
                    "source": item.get('source', 'Perplexity Search'),
                    "summary": item.get('summary', '')[:500] + ('...' if len(item.get('summary', '')) > 500 else '')
                }
                new_articles.append(article)
            
            # Store the fetched articles in state
            perplexity_articles = new_articles
            tool_context.state["perplexity_articles"] = perplexity_articles
            
            # Merge with existing articles (avoiding duplicates by ID)
            existing_ids = {article["id"] for article in articles}
            for article in perplexity_articles:
                if article["id"] not in existing_ids:
                    articles.append(article)
                    existing_ids.add(article["id"])
            
            # Update the combined articles in state
            tool_context.state["articles"] = articles
            
            return {
                "action": "fetch_perplexity_articles",
                "query": query,
                "days": days,
                "articles_found": len(perplexity_articles),
                "total_articles": len(articles),
                "message": f"Found {len(perplexity_articles)} articles from Perplexity for '{query}' in the last {days} days."
            }
            
        except json.JSONDecodeError as e:
            return {
                "action": "fetch_perplexity_articles",
                "status": "error",
                "message": f"Error parsing JSON response: {str(e)}",
                "raw_response": content
            }
            
    except Exception as e:
        return {
            "action": "fetch_perplexity_articles",
            "status": "error",
            "message": f"Error calling Perplexity API: {str(e)}"
        }
