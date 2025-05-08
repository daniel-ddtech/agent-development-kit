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
    
    # Get categorized articles
    categories = tool_context.state.get("categorized_articles", {})
    
    if not categories:
        return {
            "action": "generate_newsletter_with_llm",
            "status": "error",
            "message": "No categorized articles found. Please categorize articles first."
        }
    
    # Format each category with LLM
    for cat_id, category in categories.items():
        if category["articles"]:
            format_with_llm(category["articles"], category["title"], tool_context)
    
    # Get the formatted categories
    formatted_categories = tool_context.state.get("formatted_categories", {})
    
    # Create the newsletter structure
    current_date = datetime.now().strftime("%Y-%m-%d")
    newsletter_structure = {
        "title": "This Week in Generative AI 🤖 and Gaming 🎮",
        "date": current_date,
        "categories": formatted_categories,
        "trending_topics": tool_context.state.get("trending_topics", [])
    }
    
    # Generate the complete newsletter with LLM
    prompt = f"""
    You are a newsletter editor specializing in AI and gaming technology.
    
    Create a complete newsletter using the following structure and content:
    
    Title: {newsletter_structure['title']}
    Date: {newsletter_structure['date']}
    
    Categories and their bullet points:
    {newsletter_structure['categories']}
    
    Trending topics this week:
    {[topic.get('topic', '').replace('_', ' ').title() for topic in newsletter_structure['trending_topics']]}
    
    Format the newsletter in Markdown with:
    1. A compelling title and date at the top
    2. A brief introduction summarizing the key themes this week (2-3 sentences)
    3. Each category with its emoji and bullet points
    4. Proper spacing and formatting for readability
    
    Return ONLY the formatted newsletter in Markdown.
    """
    
    try:
        # Call the Generative AI model
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        
        # Extract the formatted newsletter
        newsletter_content = response.text.strip()
        
        # Store the newsletter in state
        tool_context.state["llm_newsletter"] = newsletter_content
        
        return {
            "action": "generate_newsletter_with_llm",
            "status": "success",
            "content": newsletter_content[:500] + "..." if len(newsletter_content) > 500 else newsletter_content,
            "message": "Generated complete newsletter with LLM formatting."
        }
        
    except Exception as e:
        print(f"Error in LLM newsletter generation: {str(e)}")
        return {
            "action": "generate_newsletter_with_llm",
            "status": "error",
            "message": f"Error generating newsletter with LLM: {str(e)}"
        }
