"""
Pure newsletter generator without ratings.
"""

import os
import json
from datetime import datetime
from google.adk.tools.tool_context import ToolContext

def generate_pure_newsletter(tool_context: ToolContext) -> dict:
    """
    Generate a clean newsletter without ratings, just the bullet points.
    
    Args:
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with the result of the operation
    """
    print(f"--- Tool: generate_pure_newsletter called ---")
    
    # Get the LLM newsletter content
    llm_newsletter = tool_context.state.get("llm_newsletter", "")
    
    if not llm_newsletter:
        return {
            "action": "generate_pure_newsletter",
            "status": "error",
            "message": "No LLM newsletter found to process."
        }
    
    # Extract just the bullet points part (before the ratings section)
    pure_content = ""
    lines = llm_newsletter.split("\n")
    footer_added = False
    
    for line in lines:
        # Stop when we reach the ratings section
        if "## 🌟 Content Quality Ratings" in line:
            break
        
        # Check if this is the footer line
        if "*→ Thread and long-form summary coming later this week." in line:
            footer_added = True
        
        pure_content += line + "\n"
    
    # Add the footer if it wasn't already there
    if not footer_added:
        pure_content += "\n---\n\n*→ Thread and long-form summary coming later this week.\n→ Subscribe to get weekly dev-focused signals.*\n"
    
    # Store the pure newsletter in the context
    tool_context.state["pure_newsletter"] = pure_content
    
    # Get current date for filename
    today = datetime.now().strftime("%Y%m%d")
    
    # Save to file
    filename = f"newsletter_pure_{today}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pure_content)
    
    return {
        "action": "generate_pure_newsletter",
        "status": "success",
        "message": f"Generated pure newsletter without ratings and saved to {filename}",
        "filename": filename
    }

def add_sources_to_pure_newsletter(tool_context: ToolContext) -> dict:
    """
    Add sources information to the pure newsletter.
    
    Args:
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with the result of the operation
    """
    print(f"--- Tool: add_sources_to_pure_newsletter called ---")
    
    # Get the pure newsletter content
    pure_newsletter = tool_context.state.get("pure_newsletter", "")
    
    if not pure_newsletter:
        return {
            "action": "add_sources_to_pure_newsletter",
            "status": "error",
            "message": "No pure newsletter found to add sources to."
        }
    
    # Get all sources used in this newsletter
    used_sources = set()
    for article in tool_context.state.get("articles", []):
        source = article.get("source", "Unknown")
        if source != "Unknown":
            used_sources.add(source)
    
    # Format sources section
    sources_section = "\n\n## 📚 Sources\n\n"
    
    # Add used sources
    if used_sources:
        sources_section += "### Sources Used in This Newsletter\n\n"
        for i, source in enumerate(sorted(used_sources), 1):
            sources_section += f"{i}. **{source}**\n"
    
    # Add to pure newsletter
    pure_newsletter_with_sources = pure_newsletter + sources_section
    
    # Update the context
    tool_context.state["pure_newsletter"] = pure_newsletter_with_sources
    
    # Get current date for filename
    today = datetime.now().strftime("%Y%m%d")
    
    # Save to file
    filename = f"newsletter_pure_{today}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(pure_newsletter_with_sources)
    
    return {
        "action": "add_sources_to_pure_newsletter",
        "status": "success",
        "message": f"Added sources to pure newsletter and saved to {filename}",
        "filename": filename
    }
