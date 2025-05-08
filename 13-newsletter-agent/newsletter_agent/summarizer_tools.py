from datetime import datetime
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext


def summarize_articles(tone: str, tool_context: ToolContext) -> dict:
    """Generate concise summaries for curated articles.
    
    Args:
        tone: The tone to use for summaries (e.g., 'professional', 'casual', 'enthusiastic')
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with summarized articles
    """
    print(f"--- Tool: summarize_articles called with tone: {tone} ---")
    
    # Get curated articles from state
    articles = tool_context.state.get("curated_articles", [])
    
    if not articles:
        return {
            "action": "summarize_articles",
            "status": "error",
            "message": "No curated articles found. Please curate articles first."
        }
    
    # In a real implementation, you would use an LLM API here
    # For now, we'll create simplified summaries based on the existing data
    
    summarized_articles = []
    for article in articles:
        title = article.get("title", "")
        original_summary = article.get("summary", "")
        
        # Create a summary based on tone and content type
        title_lower = title.lower()
        summary_lower = original_summary.lower()
        content = title_lower + " " + summary_lower
        
        # Detect content type
        is_generative_ai = any(term in content for term in [
            "generative ai", "gen ai", "llm", "gpt", "diffusion", "text-to-image", 
            "dall-e", "midjourney", "stable diffusion"])
            
        is_game_dev = any(term in content for term in [
            "game engine", "unity", "unreal", "game development", "game design"])
            
        is_security = any(term in content for term in [
            "security", "privacy", "ethics", "owasp", "risk", "safety"])
        
        # Customize prefix based on content type and tone
        if tone.lower() == 'professional':
            if is_generative_ai:
                prefix = "New generative AI capabilities: "
            elif is_game_dev:
                prefix = "Game development innovation: "
            elif is_security:
                prefix = "Security consideration: "
            else:
                prefix = "Industry analysis: "
                
        elif tone.lower() == 'casual':
            if is_generative_ai:
                prefix = "Cool AI tech alert: "
            elif is_game_dev:
                prefix = "Game dev update: "
            elif is_security:
                prefix = "Heads up on AI safety: "
            else:
                prefix = "Check this out: "
                
        elif tone.lower() == 'enthusiastic':
            if is_generative_ai:
                prefix = "Mind-blowing AI breakthrough! "
            elif is_game_dev:
                prefix = "Game-changing development! "
            elif is_security:
                prefix = "Critical AI safety update! "
            else:
                prefix = "Exciting news! "
        else:
            prefix = ""
        
        # Create a LinkedIn-style headline (short summary)
        if len(original_summary) > 100:
            linkedin_headline = original_summary[:100] + "..."
        else:
            linkedin_headline = original_summary
            
        # Add the article with its new summary
        summarized_article = article.copy()
        summarized_article["linkedin_headline"] = prefix + linkedin_headline
        summarized_article["tone"] = tone
        
        summarized_articles.append(summarized_article)
    
    # Store summarized articles in state
    tool_context.state["summarized_articles"] = summarized_articles
    
    return {
        "action": "summarize_articles",
        "status": "success",
        "count": len(summarized_articles),
        "message": f"Generated {len(summarized_articles)} article summaries with '{tone}' tone."
    }


def generate_intro(title: str, tone: str, tool_context: ToolContext) -> dict:
    """Generate an introduction for the newsletter.
    
    Args:
        title: The title for the newsletter
        tone: The tone to use (e.g., 'professional', 'casual', 'enthusiastic')
        tool_context: Context for accessing session state
        
    Returns:
        A dictionary with the generated introduction
    """
    print(f"--- Tool: generate_intro called with title: {title}, tone: {tone} ---")
    
    # Get trending topics if available
    trending_topics = tool_context.state.get("trending_topics", [])
    topic_mentions = []
    
    for topic_data in trending_topics[:3]:  # Use top 3 topics
        topic = topic_data.get("topic", "").replace("_", " ").title()
        topic_mentions.append(topic)
    
    # Generate intro based on tone and topics
    current_date = datetime.now().strftime("%B %d, %Y")
    
    if tone.lower() == 'professional':
        if topic_mentions:
            intro = f"Welcome to this week's {title} for {current_date}. In this edition, we explore significant developments in {', '.join(topic_mentions[:-1])}{' and ' if len(topic_mentions) > 1 else ''}{topic_mentions[-1] if topic_mentions else ''}, with a focus on how generative AI is transforming game development and player experiences."
        else:
            intro = f"Welcome to this week's {title} for {current_date}. In this edition, we analyze the latest advancements in generative AI technologies and their applications in gaming and interactive entertainment."
    
    elif tone.lower() == 'casual':
        if topic_mentions:
            intro = f"Hey there! Welcome to {title} for {current_date}. This week we're checking out some cool innovations in {', '.join(topic_mentions[:-1])}{' and ' if len(topic_mentions) > 1 else ''}{topic_mentions[-1] if topic_mentions else ''}. Let's see how generative AI is changing the game!"
        else:
            intro = f"Hey there! Welcome to {title} for {current_date}. We've got some fascinating generative AI and gaming news for you this week - from new tools that help developers create content faster to AI systems that make games more engaging."
    
    elif tone.lower() == 'enthusiastic':
        if topic_mentions:
            intro = f"Exciting breakthroughs in generative AI! Welcome to {title} for {current_date}! This week is packed with game-changing developments in {', '.join(topic_mentions[:-1])}{' and ' if len(topic_mentions) > 1 else ''}{topic_mentions[-1] if topic_mentions else ''}! The future of gaming is being rewritten as we speak!"
        else:
            intro = f"Incredible advances in generative AI! Welcome to {title} for {current_date}! We've got some mind-blowing innovations to share this week that are revolutionizing how games are created, played, and experienced!"
    
    else:
        intro = f"Welcome to {title} for {current_date}. Here are this week's top stories in generative AI and gaming."
    
    # Store the intro in state
    tool_context.state["newsletter_intro"] = intro
    
    return {
        "action": "generate_intro",
        "status": "success",
        "intro": intro,
        "message": f"Generated newsletter introduction with '{tone}' tone."
    }
