import os
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext
import google.generativeai as genai
from datetime import datetime

# Configure the Google Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

# Default model to use
DEFAULT_MODEL = "gemini-1.5-pro"

def format_with_llm(articles: List[Dict], category: str, tool_context: ToolContext) -> dict:
    """Use Google's Generative AI to format articles into concise, engaging bullet points.
    
    Args:
        articles: List of articles to format
        category: Category name (e.g., "Gaming & AI", "Major AI Models")
        tool_context: Context for accessing state
        
    Returns:
        Dictionary with formatted bullet points
    """
    print(f"--- Tool: format_with_llm called for category: {category} ---")
    
    if not articles:
        return {
            "action": "format_with_llm",
            "status": "error",
            "message": f"No articles found for category: {category}"
        }
    
    # Prepare the articles data for the LLM
    articles_data = []
    for article in articles:
        articles_data.append({
            "title": article.get("title", ""),
            "summary": article.get("summary", ""),
            "source": article.get("source", ""),
            "url": article.get("url", ""),
            "published": article.get("published", "")
        })
    
    # Create the prompt for the LLM
    prompt = f"""
    You are a newsletter editor specializing in AI and gaming technology news.
    
    Format the following articles into concise, engaging bullet points for the "{category}" section of a newsletter.
    
    For each article:
    1. Extract the key entity (company, product, technology)
    2. Create a concise headline in the format: "{{key entity}}: {{main point}}"
    3. Keep each bullet point under 100 characters if possible
    4. Focus on the most important information
    5. Use professional, clear language
    
    Here are the articles:
    {articles_data}
    
    Return ONLY the formatted bullet points in Markdown format, with each bullet starting with "- **" and ending with "**".
    If source information is available, add it after the headline in italics like this: "- **Headline** - *Source*"
    """
    
    try:
        # Call the Generative AI model
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        
        # Extract the formatted bullet points
        formatted_content = response.text.strip()
        
        # Store in state for the category
        if "formatted_categories" not in tool_context.state:
            tool_context.state["formatted_categories"] = {}
        
        tool_context.state["formatted_categories"][category] = formatted_content
        
        return {
            "action": "format_with_llm",
            "status": "success",
            "category": category,
            "content": formatted_content,
            "message": f"Formatted {len(articles)} articles for category: {category}"
        }
        
    except Exception as e:
        print(f"Error in LLM formatting: {str(e)}")
        return {
            "action": "format_with_llm",
            "status": "error",
            "message": f"Error formatting articles with LLM: {str(e)}"
        }


def generate_newsletter_with_llm(tool_context: ToolContext) -> dict:
    """Generate a complete newsletter using LLM for all formatting.
    
    Args:
        tool_context: Context for accessing state
        
    Returns:
        Dictionary with the complete newsletter
    """
    print("--- Tool: generate_newsletter_with_llm called ---")
    
    # Get the categorized articles from the context
    categorized_articles = tool_context.state.get("categorized_articles", [])
    
    if not categorized_articles:
        return {
            "action": "generate_newsletter_with_llm",
            "status": "error",
            "message": "No categorized articles found. Please categorize articles first."
        }
    
    # Get trending topics
    trending_topics = tool_context.state.get("trending_topics", [])
    
    # Group articles by category
    articles_by_category = {}
    for article in categorized_articles:
        categories = article.get("categories", [])
        if categories:
            category = categories[0]  # Use the first category
            if category not in articles_by_category:
                articles_by_category[category] = []
            articles_by_category[category].append(article)
    
    # Create the prompt for the LLM using the bullet-point format
    prompt = f"""
    You are an expert newsletter writer specializing in AI and gaming. Create a professional weekly roundup newsletter using the following categorized articles and trending topics.
    
    CATEGORIES AND ARTICLES:
    {articles_by_category}
    
    TRENDING TOPICS:
    {trending_topics}
    
    INSTRUCTIONS:
    Format the newsletter using EXACTLY this template structure:
    
    # This Week in Generative AI 🤖 and Gaming 🎮👇
    *→ Each headline should be 6–12 words max for quick scanning.*
    
    ---
    
    ## 🎮 Gaming & AI
    <!-- Add headlines about AI in games, dev tools, content, engines -->
    - [Company] emphasizes "human touch" amid rising AI usage
    - [Studio] launches AI-generated game demo using internal model
    - [Platform] adds procedural content generation support
    - [Dev tool] integrates agent-based NPC design
    - [Publisher] explores LLM-based dialogue systems in new title
    
    ---
    
    ## 🧠 Major AI Models & Features
    <!-- Include major model releases, feature upgrades, dev APIs -->
    - [Model name] outperforms competitors with fewer parameters
    - [Startup] releases open-source model for code generation
    - [API] now supports multi-turn prompt evaluation
    - [Voice AI] launches server-based low-latency integration
    - [Image tool] improves prompt handling for visuals
    
    ---
    
    ## 🔬 Breakthrough Tech & Regulation
    <!-- Add news on hardware, robotics, policy, and ethics -->
    - [Robotaxi] pilot begins in [location]
    - [AI device] combines robotics with hydrogen engine tech
    - [Court ruling] impacts model training transparency
    - [Company] pauses hiring for roles replaced by AI
    - [Watchdog] raises transparency concerns over model benchmarks
    
    ---
    
    ## 💰 Business & Funding News
    <!-- Add funding rounds, M&A, product launches, and market moves -->
    - [Startup] raises $XM for AI-native dev tooling
    - [Big Tech] explores acquisition of AI hardware startup
    - [New company] emerges from stealth with agent-focused platform
    - [Platform] adds Pro+ pricing tier with new features
    - [VC firm] backs agentic framework for enterprise apps
    
    ---
    
    *→ Thread and long-form summary coming later this week.
    → Subscribe to get weekly dev-focused signals.*
    
    IMPORTANT INSTRUCTIONS:
    1. Replace the placeholder text with ACTUAL content from the provided articles.
    2. Each bullet point should be 6-12 words maximum for quick scanning.
    3. Include ALL articles from the provided data - do not omit any articles.
    4. Categorize each article into the most appropriate section.
    5. If there are no relevant articles for a section, include 1-2 bullets with "No major updates this week" or similar.
    6. Keep the emoji headers and section dividers exactly as shown.
    7. Focus on generative AI in gaming and its impact on game development.
    8. DO NOT include the HTML comments in the final output.
    9. Maintain the footer text about thread and subscribe.
    """
    
    try:
        # Generate the newsletter using the LLM
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        
        # Get the generated newsletter
        newsletter = response.text
        
        # Store the newsletter in the context
        tool_context.state["llm_newsletter"] = newsletter
        
        return {
            "action": "generate_newsletter_with_llm",
            "status": "success",
            "message": "Generated newsletter with LLM",
            "newsletter": newsletter
        }
    except Exception as e:
        return {
            "action": "generate_newsletter_with_llm",
            "status": "error",
            "message": f"Error generating newsletter with LLM: {str(e)}"
        }
