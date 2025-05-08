from datetime import datetime
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext


def curate_articles(criteria: Dict[str, Any], tool_context: ToolContext) -> dict:
    """Filter and rank articles based on relevance criteria.
    
    Args:
        criteria: Dictionary of criteria for filtering and ranking
            - keywords: List of keywords to prioritize
            - min_score: Minimum relevance score (0-10)
            - max_articles: Maximum number of articles to include
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with curated articles
    """
    print(f"--- Tool: curate_articles called with criteria: {criteria} ---")
    
    # Get articles from state
    articles = tool_context.state.get("articles", [])
    
    if not articles:
        return {
            "action": "curate_articles",
            "status": "error",
            "message": "No articles found to curate. Please fetch articles first."
        }
    
    # Extract criteria
    default_keywords = [
        # Generative AI keywords
        "generative AI", "gen AI", "diffusion model", "large language model", "LLM", 
        "stable diffusion", "midjourney", "DALL-E", "GPT", "Vertex AI", "AWS Bedrock",
        "text-to-image", "text-to-3D", "text-to-audio", "procedural generation",
        
        # Gaming AI keywords
        "AI in games", "gaming", "game development", "NPC", "character behavior",
        "game assets", "game design", "Unity", "Unreal Engine", "simulation",
        
        # Security and ethics
        "OWASP", "AI security", "AI ethics", "UGC", "user-generated content",
        "content moderation", "AI safety"
    ]
    
    keywords = criteria.get("keywords", default_keywords)
    min_score = criteria.get("min_score", 3)
    max_articles = criteria.get("max_articles", 10)
    
    # Score and rank articles
    scored_articles = []
    for article in articles:
        # Initialize score
        score = 0
        
        # Score based on keywords in title (higher weight)
        title = article.get("title", "").lower()
        for keyword in keywords:
            if keyword.lower() in title:
                score += 2
        
        # Score based on keywords in summary
        summary = article.get("summary", "").lower()
        for keyword in keywords:
            if keyword.lower() in summary:
                score += 1
        
        # Bonus for recency
        try:
            pub_date = datetime.strptime(article.get("published", "2000-01-01"), "%Y-%m-%d")
            days_old = (datetime.now() - pub_date).days
            if days_old <= 1:  # Today or yesterday
                score += 3
            elif days_old <= 3:  # Last 3 days
                score += 2
            elif days_old <= 7:  # Last week
                score += 1
        except:
            # If date parsing fails, no bonus
            pass
        
        # Only include articles that meet minimum score
        if score >= min_score:
            scored_articles.append({
                "article": article,
                "score": score
            })
    
    # Sort by score (descending)
    scored_articles.sort(key=lambda x: x["score"], reverse=True)
    
    # Limit to max_articles
    top_articles = scored_articles[:max_articles]
    
    # Extract just the articles (without scores) for the final list
    curated_articles = [item["article"] for item in top_articles]
    
    # Store curated articles in state
    tool_context.state["curated_articles"] = curated_articles
    
    return {
        "action": "curate_articles",
        "status": "success",
        "total_articles": len(articles),
        "curated_count": len(curated_articles),
        "message": f"Curated {len(curated_articles)} articles from a total of {len(articles)}."
    }


def get_trending_topics(tool_context: ToolContext) -> dict:
    """Identify trending topics from the curated articles.
    
    Args:
        tool_context: Context for accessing session state
        
    Returns:
        A dictionary with trending topics
    """
    print("--- Tool: get_trending_topics called ---")
    
    # Get curated articles from state
    articles = tool_context.state.get("curated_articles", [])
    
    if not articles:
        return {
            "action": "get_trending_topics",
            "status": "error",
            "message": "No curated articles found. Please curate articles first."
        }
    
    # Comprehensive keyword frequency analysis for generative AI in gaming
    topic_keywords = {
        # Generative AI models and technologies
        "generative_models": ["gpt", "llm", "large language model", "diffusion model", "stable diffusion", 
                            "midjourney", "dall-e", "text-to-image", "text-to-3d", "generative ai", "gen ai"],
        
        # Cloud AI platforms
        "ai_platforms": ["vertex ai", "aws bedrock", "azure openai", "hugging face", "replicate", 
                        "anthropic", "claude", "nvidia", "cloud ai"],
        
        # Game development and engines
        "game_development": ["game engine", "unity", "unreal", "godot", "game design", "developer", 
                           "asset creation", "game assets", "3d models"],
        
        # NPC and character AI
        "npc_behavior": ["npc", "character", "behavior", "pathfinding", "dialogue", "character ai", 
                       "conversation", "agent", "autonomous"],
        
        # Procedural and content generation
        "content_generation": ["procedural", "generation", "content", "level design", "world building", 
                             "terrain", "texture", "asset generation"],
        
        # Player experience and personalization
        "player_experience": ["player", "experience", "engagement", "personalization", "adaptive", 
                            "dynamic difficulty", "recommendation"],
        
        # Security and ethics
        "security_ethics": ["security", "ethics", "privacy", "bias", "fairness", "owasp", 
                          "content moderation", "safety", "ugc", "user-generated"]
    }
    
    # Count occurrences of each topic
    topic_counts = {topic: 0 for topic in topic_keywords}
    
    for article in articles:
        title = article.get("title", "").lower()
        summary = article.get("summary", "").lower()
        content = title + " " + summary
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content:
                    topic_counts[topic] += 1
    
    # Sort topics by frequency
    trending_topics = [
        {"topic": topic, "count": count}
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        if count > 0
    ]
    
    # Store trending topics in state
    tool_context.state["trending_topics"] = trending_topics
    
    return {
        "action": "get_trending_topics",
        "status": "success",
        "topics": trending_topics,
        "message": f"Identified {len(trending_topics)} trending topics from {len(articles)} articles."
    }
