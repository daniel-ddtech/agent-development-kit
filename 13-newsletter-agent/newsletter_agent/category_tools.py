from datetime import datetime
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext


def categorize_articles(tool_context: ToolContext) -> dict:
    """Categorize articles into predefined sections based on content.
    
    Args:
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with categorized articles
    """
    print("--- Tool: categorize_articles called ---")
    
    # Get curated or summarized articles from state
    articles = tool_context.state.get("summarized_articles", tool_context.state.get("curated_articles", []))
    
    if not articles:
        return {
            "action": "categorize_articles",
            "status": "error",
            "message": "No articles found to categorize. Please curate or summarize articles first."
        }
    
    # Define categories with titles and keywords
    categories = {
        "gaming_ai": {
            "title": "🎮 Gaming & AI",
            "keywords": ["game", "gaming", "nintendo", "xbox", "playstation", "unity", "unreal", 
                        "game engine", "game development", "game design", "npc", "character", 
                        "procedural generation", "level design", "player experience"],
            "articles": []
        },
        "ai_models": {
            "title": "🧠 Major AI Models & Features",
            "keywords": ["model", "llm", "gpt", "claude", "gemini", "mistral", "llama", "feature",
                        "large language model", "diffusion model", "stable diffusion", "midjourney", 
                        "dall-e", "text-to-image", "generative ai", "gen ai", "deep learning"],
            "articles": []
        },
        "tech_regulation": {
            "title": "🔬 Breakthrough Tech & Regulation",
            "keywords": ["regulation", "law", "policy", "breakthrough", "research", "robotics",
                        "ethics", "privacy", "bias", "fairness", "safety", "security", 
                        "content moderation", "copyright", "legal"],
            "articles": []
        },
        "business": {
            "title": "💰 Business & Funding News",
            "keywords": ["funding", "investment", "million", "billion", "startup", "acquisition",
                        "venture capital", "series a", "series b", "raised", "valuation", 
                        "partnership", "collaboration", "deal", "merger"],
            "articles": []
        }
    }
    
    # Categorize each article
    for article in articles:
        best_category = None
        best_score = 0
        
        # Combine title and summary for content analysis
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        content = title + " " + summary
        
        # Score each category based on keyword matches
        for cat_id, category in categories.items():
            score = 0
            for keyword in category["keywords"]:
                if keyword.lower() in content:
                    score += 1
            
            # Select the category with the highest score
            if score > best_score:
                best_score = score
                best_category = cat_id
        
        # Assign to best category or "other" if no good match
        if best_category and best_score > 0:
            categories[best_category]["articles"].append(article)
        else:
            # Create "other" category if it doesn't exist
            if "other" not in categories:
                categories["other"] = {
                    "title": "📌 Other Interesting News",
                    "keywords": [],
                    "articles": []
                }
            categories["other"]["articles"].append(article)
    
    # Store categorized articles in state
    tool_context.state["categorized_articles"] = categories
    
    # Count articles in each category
    category_counts = {cat_id: len(category["articles"]) for cat_id, category in categories.items()}
    
    return {
        "action": "categorize_articles",
        "status": "success",
        "categories": [cat["title"] for cat in categories.values() if cat["articles"]],
        "category_counts": category_counts,
        "message": f"Categorized {len(articles)} articles into {len([c for c in category_counts.values() if c > 0])} categories."
    }


def format_bullet_points(tool_context: ToolContext) -> dict:
    """Format articles as bullet points by category.
    
    Args:
        tool_context: Context for accessing session state
        
    Returns:
        A dictionary with the formatted newsletter
    """
    print("--- Tool: format_bullet_points called ---")
    
    # Get categorized articles from state
    categories = tool_context.state.get("categorized_articles", {})
    
    if not categories:
        return {
            "action": "format_bullet_points",
            "status": "error",
            "message": "No categorized articles found. Please categorize articles first."
        }
    
    # Create the newsletter with bullet points
    current_date = tool_context.state.get("date", datetime.now().strftime("%Y-%m-%d"))
    output = f"# This Week in Generative AI 🤖 and Gaming 🎮\n\n"
    output += f"*{current_date}*\n\n"
    
    # Add each category with bullet points
    for cat_id, category in categories.items():
        if category["articles"]:
            output += f"## {category['title']}\n\n"
            
            for article in category["articles"]:
                # Use headline if available, otherwise use title
                headline = article.get("headline", article.get("title", "Untitled"))
                
                # Add source if available
                source = article.get("source", "")
                if source:
                    output += f"- **{headline}** - *{source}*\n"
                else:
                    output += f"- **{headline}**\n"
            
            output += "\n"
    
    # Store the bullet point newsletter in state
    tool_context.state["bullet_point_newsletter"] = output
    
    return {
        "action": "format_bullet_points",
        "status": "success",
        "content": output[:500] + "..." if len(output) > 500 else output,
        "message": f"Formatted newsletter with bullet points by category."
    }
