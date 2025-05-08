import os
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext
import google.generativeai as genai

# Configure the Google Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

# Default model to use
DEFAULT_MODEL = "gemini-1.5-pro"

def rate_article_content(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rate an article based on its content quality, relevance, and impact.
    
    Args:
        article: Dictionary containing article information
        
    Returns:
        Dictionary with ratings for the article
    """
    title = article.get("title", "")
    summary = article.get("summary", "")
    keywords = article.get("keywords", [])
    
    # Simple algorithm to rate articles based on keywords and title
    # This avoids LLM API calls which can be unreliable for structured data
    
    # Define rating criteria
    ai_gaming_keywords = [
        "ai", "artificial intelligence", "machine learning", "neural network",
        "game", "gaming", "player", "npc", "character", "gameplay"
    ]
    
    technical_keywords = [
        "model", "algorithm", "framework", "architecture", "implementation",
        "diffusion", "transformer", "neural", "deep learning", "training"
    ]
    
    business_keywords = [
        "funding", "investment", "million", "billion", "startup", "venture",
        "acquisition", "partnership", "revenue", "growth", "market"
    ]
    
    # Calculate scores
    title_lower = title.lower()
    summary_lower = summary.lower()
    
    # Relevance score (1-5)
    relevance_score = 3  # Default score
    ai_gaming_matches = sum(1 for kw in ai_gaming_keywords if kw in title_lower or kw in summary_lower)
    if ai_gaming_matches >= 4:
        relevance_score = 5
    elif ai_gaming_matches >= 2:
        relevance_score = 4
    
    # Technical depth score (1-5)
    technical_score = 3  # Default score
    technical_matches = sum(1 for kw in technical_keywords if kw in title_lower or kw in summary_lower)
    if technical_matches >= 3:
        technical_score = 5
    elif technical_matches >= 1:
        technical_score = 4
    
    # Timeliness score (1-5)
    # Assume all articles are recent since we're filtering by date
    timeliness_score = 4
    
    # Educational value score (1-5)
    educational_score = 3
    if technical_score >= 4 or relevance_score >= 4:
        educational_score = 4
    
    # Business relevance score (1-5)
    business_score = 3
    business_matches = sum(1 for kw in business_keywords if kw in title_lower or kw in summary_lower)
    if business_matches >= 2:
        business_score = 5
    elif business_matches >= 1:
        business_score = 4
    
    # Overall quality score (1-5)
    overall_score = (relevance_score + technical_score + timeliness_score + educational_score) / 4
    overall_score = round(overall_score)
    
    # Create ratings dictionary
    ratings = {
        "relevance": {
            "score": relevance_score,
            "justification": f"Contains {ai_gaming_matches} AI/gaming related keywords"
        },
        "technical_depth": {
            "score": technical_score,
            "justification": f"Contains {technical_matches} technical keywords"
        },
        "timeliness": {
            "score": timeliness_score,
            "justification": "Recent article from curated feed"
        },
        "educational_value": {
            "score": educational_score,
            "justification": "Based on technical depth and relevance scores"
        },
        "business_relevance": {
            "score": business_score,
            "justification": f"Contains {business_matches} business/funding keywords"
        },
        "overall_quality": {
            "score": overall_score,
            "justification": "Average of other scores"
        },
        "average_score": round((relevance_score + technical_score + timeliness_score + educational_score + business_score) / 5, 1)
    }
    
    return ratings


def rate_articles(tool_context: ToolContext) -> dict:
    """
    Rate all curated articles in the tool context.
    
    Args:
        tool_context: Context for accessing state
        
    Returns:
        Dictionary with rating results
    """
    print("--- Tool: rate_articles called ---")
    
    # Get curated articles
    articles = tool_context.state.get("curated_articles", [])
    
    if not articles:
        return {
            "action": "rate_articles",
            "status": "error",
            "message": "No curated articles found. Please curate articles first."
        }
    
    # Rate each article
    rated_articles = []
    for article in articles:
        ratings = rate_article_content(article)
        article["ratings"] = ratings
        rated_articles.append(article)
    
    # Sort articles by average rating
    rated_articles.sort(key=lambda x: x.get("ratings", {}).get("average_score", 0), reverse=True)
    
    # Store rated articles in state
    tool_context.state["rated_articles"] = rated_articles
    
    # First, ensure all articles in categorized_articles have ratings
    # We need to update the articles in the categorized_articles with their ratings
    categorized_articles = tool_context.state.get("categorized_articles", [])
    
    # Create a lookup dictionary for quick access to rated articles by URL
    rated_lookup = {article.get("url"): article for article in rated_articles if article.get("url")}
    
    # Update articles with their ratings
    updated_articles = []
    for article in categorized_articles:
        url = article.get("url")
        if url and url in rated_lookup:
            # Copy ratings from the rated article to this article
            article["ratings"] = rated_lookup[url].get("ratings", {})
        updated_articles.append(article)
    
    # Store the updated articles back
    tool_context.state["categorized_articles"] = updated_articles
    
    # Now calculate average ratings by category
    category_ratings = {}
    
    # Group articles by category
    articles_by_category = {}
    for article in updated_articles:
        for category in article.get("categories", []):
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)
    
    # Calculate average rating for each category
    for category, cat_articles in articles_by_category.items():
        if cat_articles:
            # Filter articles that have ratings
            rated_cat_articles = [a for a in cat_articles if "ratings" in a]
            if rated_cat_articles:
                avg_scores = [a["ratings"].get("average_score", 0) for a in rated_cat_articles]
                category_ratings[category] = round(sum(avg_scores) / len(avg_scores), 1)
    
    # Store category ratings in state
    tool_context.state["category_ratings"] = category_ratings
    
    return {
        "action": "rate_articles",
        "status": "success",
        "message": f"Rated {len(rated_articles)} articles",
        "top_articles": rated_articles[:3] if rated_articles else [],
        "category_ratings": category_ratings
    }


def add_ratings_to_newsletter(tool_context: ToolContext) -> dict:
    """
    Add rating information to the newsletter.
    
    Args:
        tool_context: Context for accessing state
        
    Returns:
        Dictionary with updated newsletter
    """
    print("--- Tool: add_ratings_to_newsletter called ---")
    
    # Get the newsletter content
    newsletter = tool_context.state.get("llm_newsletter", "")
    
    if not newsletter:
        return {
            "action": "add_ratings_to_newsletter",
            "status": "error",
            "message": "No newsletter found. Please generate newsletter first."
        }
    
    # Get category ratings
    category_ratings = tool_context.state.get("category_ratings", {})
    
    if not category_ratings:
        return {
            "action": "add_ratings_to_newsletter",
            "status": "error",
            "message": "No category ratings found. Please rate articles first."
        }
    
    # Get top rated articles
    rated_articles = tool_context.state.get("rated_articles", [])
    top_articles = rated_articles[:3] if rated_articles else []
    
    # Create rating section
    rating_section = "\n## 🌟 Content Quality Ratings\n\n"
    
    # Add category ratings
    rating_section += "### Category Ratings\n\n"
    for category, rating in category_ratings.items():
        stars = "★" * int(rating) + "☆" * (5 - int(rating))
        rating_section += f"- **{category}**: {rating}/5 {stars}\n"
    
    # Add top articles
    if top_articles:
        rating_section += "\n### Top Rated Articles\n\n"
        for i, article in enumerate(top_articles):
            title = article.get("title", "Untitled")
            source = article.get("source", "")
            avg_score = article.get("ratings", {}).get("average_score", 0)
            stars = "★" * int(avg_score) + "☆" * (5 - int(avg_score))
            
            rating_section += f"{i+1}. **{title}** - {source} ({avg_score}/5 {stars})\n"
    
    # Add rating section to newsletter
    # Find the end of the newsletter (before any trailing newlines)
    newsletter = newsletter.rstrip()
    updated_newsletter = newsletter + "\n\n" + rating_section
    
    # Store updated newsletter in state
    tool_context.state["rated_newsletter"] = updated_newsletter
    
    return {
        "action": "add_ratings_to_newsletter",
        "status": "success",
        "message": "Added ratings to newsletter",
        "content": updated_newsletter[:500] + "..." if len(updated_newsletter) > 500 else updated_newsletter
    }
