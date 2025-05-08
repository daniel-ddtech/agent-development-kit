import json
from datetime import datetime
from typing import Dict, Any
from google.adk.tools.tool_context import ToolContext


def format_newsletter(format_type: str, tool_context: ToolContext) -> dict:
    """Format the newsletter into the specified format.
    
    Args:
        format_type: The format to use ('markdown', 'html', 'json')
        tool_context: Context for accessing session state
        
    Returns:
        A dictionary with the formatted newsletter
    """
    print(f"--- Tool: format_newsletter called with format: {format_type} ---")
    
    # Get required data from state
    summarized_articles = tool_context.state.get("summarized_articles", [])
    intro = tool_context.state.get("newsletter_intro", "Welcome to this week's AI in Gaming newsletter!")
    trending_topics = tool_context.state.get("trending_topics", [])
    
    if not summarized_articles:
        return {
            "action": "format_newsletter",
            "status": "error",
            "message": "No summarized articles found. Please summarize articles first."
        }
    
    # Get current date for the newsletter
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create newsletter structure
    newsletter = {
        "title": "AI in Gaming Weekly",
        "date": current_date,
        "intro": intro,
        "articles": summarized_articles,
        "trending_topics": trending_topics,
        "conclusion": "That's all for this week! Stay tuned for more AI in games news next week."
    }
    
    # Format based on requested type
    if format_type.lower() == 'markdown':
        formatted_content = _format_markdown(newsletter)
    elif format_type.lower() == 'html':
        formatted_content = _format_html(newsletter)
    elif format_type.lower() == 'json':
        formatted_content = json.dumps(newsletter, indent=2)
    else:
        return {
            "action": "format_newsletter",
            "status": "error",
            "message": f"Unsupported format: {format_type}. Supported formats are 'markdown', 'html', and 'json'."
        }
    
    # Store the formatted newsletter in state
    tool_context.state["formatted_newsletter"] = formatted_content
    tool_context.state["newsletter_format"] = format_type.lower()
    
    return {
        "action": "format_newsletter",
        "status": "success",
        "format": format_type,
        "content": formatted_content[:500] + "..." if len(formatted_content) > 500 else formatted_content,
        "message": f"Formatted newsletter as {format_type}."
    }


def _format_markdown(newsletter: Dict[str, Any]) -> str:
    """Format newsletter as Markdown."""
    md_content = f"# {newsletter.get('title', 'AI in Gaming Weekly')}\n\n"
    md_content += f"*{newsletter.get('date', datetime.now().strftime('%Y-%m-%d'))}*\n\n"
    md_content += f"{newsletter.get('intro', '')}\n\n"
    
    # Add trending topics if available
    trending_topics = newsletter.get('trending_topics', [])
    if trending_topics:
        md_content += "## Trending Topics\n\n"
        for topic in trending_topics:
            topic_name = topic.get('topic', '').replace('_', ' ').title()
            md_content += f"- {topic_name}\n"
        md_content += "\n"
    
    # Add articles
    md_content += "## Top Stories\n\n"
    for i, article in enumerate(newsletter.get('articles', []), 1):
        md_content += f"### {i}. {article.get('title', 'Untitled')}\n\n"
        md_content += f"*Source: {article.get('source', 'Unknown')} - {article.get('published', 'Unknown date')}*\n\n"
        
        # Use LinkedIn headline if available, otherwise use summary
        if 'linkedin_headline' in article:
            md_content += f"{article.get('linkedin_headline')}\n\n"
        else:
            md_content += f"{article.get('summary', 'No summary available.')}\n\n"
        
        md_content += f"[Read more]({article.get('url', '#')})\n\n"
    
    md_content += f"---\n\n{newsletter.get('conclusion', '')}\n"
    
    return md_content


def _format_html(newsletter: Dict[str, Any]) -> str:
    """Format newsletter as HTML."""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{newsletter.get('title', 'AI in Gaming Weekly')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .date {{
            color: #7f8c8d;
            font-style: italic;
        }}
        .source {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        .article {{
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }}
        .topics {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .conclusion {{
            margin-top: 30px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <h1>{newsletter.get('title', 'AI in Gaming Weekly')}</h1>
    <p class="date">{newsletter.get('date', datetime.now().strftime('%Y-%m-%d'))}</p>
    
    <p>{newsletter.get('intro', '')}</p>
"""
    
    # Add trending topics if available
    trending_topics = newsletter.get('trending_topics', [])
    if trending_topics:
        html_content += """    <div class="topics">
        <h2>Trending Topics</h2>
        <ul>
"""
        for topic in trending_topics:
            topic_name = topic.get('topic', '').replace('_', ' ').title()
            html_content += f"            <li>{topic_name}</li>\n"
        
        html_content += """        </ul>
    </div>
"""
    
    # Add articles
    html_content += "    <h2>Top Stories</h2>\n"
    for i, article in enumerate(newsletter.get('articles', []), 1):
        html_content += f"""    <div class="article">
        <h3>{i}. {article.get('title', 'Untitled')}</h3>
        <p class="source">Source: {article.get('source', 'Unknown')} - {article.get('published', 'Unknown date')}</p>
"""
        
        # Use LinkedIn headline if available, otherwise use summary
        if 'linkedin_headline' in article:
            html_content += f"        <p>{article.get('linkedin_headline')}</p>\n"
        else:
            html_content += f"        <p>{article.get('summary', 'No summary available.')}</p>\n"
        
        html_content += f"""        <p><a href="{article.get('url', '#')}">Read more</a></p>
    </div>
"""
    
    html_content += f"""    <div class="conclusion">
        <p>{newsletter.get('conclusion', '')}</p>
    </div>
</body>
</html>"""
    
    return html_content
