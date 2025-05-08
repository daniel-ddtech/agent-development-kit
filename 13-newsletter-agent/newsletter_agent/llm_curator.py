"""
LLM-based Curator for AI & Gaming Newsletter

This module provides functions for using LLMs to curate articles for the newsletter,
with a focus on generative AI in gaming and general generative AI news.
"""

import os
import json
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext
import google.generativeai as genai

# Configure the Google Generative AI API if available
api_key = os.getenv("GOOGLE_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Default model to use
DEFAULT_MODEL = "gemini-1.5-pro"

def curate_with_llm(criteria: Dict[str, Any], tool_context: ToolContext) -> dict:
    """
    Use an LLM to curate articles based on relevance to generative AI in gaming.
    
    Args:
        criteria: Dictionary of criteria for filtering and ranking
            - focus_areas: List of focus areas to prioritize
            - max_articles: Maximum number of articles to include
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with curated articles
    """
    print(f"--- Tool: curate_with_llm called with criteria: {criteria} ---")
    
    # Get articles from state
    all_articles = tool_context.state.get("rss_articles", [])
    
    if not all_articles:
        return {
            "action": "curate_with_llm",
            "status": "error",
            "message": "No articles found to curate. Please fetch articles first."
        }
    
    # Extract criteria
    default_focus_areas = [
        "Generative AI in gaming (primary focus)",
        "AI-powered game development tools",
        "AI-generated game assets (art, music, text, levels)",
        "AI NPCs and character behavior",
        "General generative AI news and advancements",
        "Business and funding in AI gaming",
        "AI ethics and policy in gaming"
    ]
    
    focus_areas = criteria.get("focus_areas", default_focus_areas)
    max_articles = criteria.get("max_articles", 25)
    
    # Prepare articles for LLM evaluation
    article_data = []
    for i, article in enumerate(all_articles):
        # Create a simplified representation for the LLM
        article_data.append({
            "id": i,
            "title": article.get("title", ""),
            "source": article.get("source", "Unknown"),
            "summary": article.get("summary", ""),
            "published": article.get("published", ""),
            "url": article.get("url", "")
        })
    
    # Split articles into batches to avoid context length issues
    batch_size = 20
    batches = [article_data[i:i + batch_size] for i in range(0, len(article_data), batch_size)]
    
    # Process each batch with the LLM
    selected_articles = []
    
    for batch_idx, batch in enumerate(batches):
        print(f"  Processing batch {batch_idx+1}/{len(batches)} ({len(batch)} articles)...")
        
        # Create prompt for LLM
        prompt = f"""
        You are an expert curator for an AI & Gaming newsletter. Your task is to evaluate and categorize articles from the list below.

        FOCUS AREAS (in order of priority):
        {chr(10).join([f"{i+1}. {area}" for i, area in enumerate(focus_areas)])}

        ARTICLES TO EVALUATE:
        {json.dumps(batch, indent=2)}

        INSTRUCTIONS:
        1. Evaluate each article's relevance to our focus areas
        2. For each article, assign a relevance score (1-10) and provide a brief justification
        3. Evaluate ALL articles in the batch - we want to be inclusive
        4. Return your evaluation as a JSON array with the following format for each article:
           {{"id": article_id, "relevance_score": score, "justification": "brief explanation", "categories": ["primary category", "secondary category"]}}
        5. Do not include any other text in your response, only the JSON array

        Be inclusive in your evaluation. We want a good mix of articles about generative AI in gaming, general generative AI news, and related topics. Even if an article is only tangentially related, include it with an appropriate relevance score.
        """
        
        try:
            # Call the Generative AI model
            model = genai.GenerativeModel(DEFAULT_MODEL)
            response = model.generate_content(prompt)
            
            # Parse the response
            try:
                # Extract JSON from response
                response_text = response.text.strip()
                
                # Handle potential formatting issues
                if response_text.startswith("```json"):
                    response_text = response_text.split("```json")[1]
                if response_text.endswith("```"):
                    response_text = response_text.split("```")[0]
                
                # Clean up any remaining non-JSON text
                if not response_text.startswith("["):
                    response_text = response_text[response_text.find("["):]
                if not response_text.endswith("]"):
                    response_text = response_text[:response_text.rfind("]")+1]
                
                # Parse the JSON
                batch_results = json.loads(response_text)
                
                # Add selected articles from this batch - be more inclusive with a lower threshold
                for result in batch_results:
                    article_id = result.get("id")
                    if article_id is not None and 0 <= article_id < len(batch):
                        # Get the original article and add curation metadata
                        article = all_articles[batch_idx * batch_size + article_id]
                        article["relevance_score"] = result.get("relevance_score", 0)
                        article["curation_justification"] = result.get("justification", "")
                        article["categories"] = result.get("categories", [])
                        
                        # Be more inclusive - accept articles with any relevance score
                        selected_articles.append(article)
            except Exception as e:
                print(f"  Error parsing LLM response: {str(e)}")
                print(f"  Response text: {response.text}")
        except Exception as e:
            print(f"  Error calling LLM API: {str(e)}")
    
    # Sort by relevance score (descending)
    selected_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # Limit to max_articles
    selected_articles = selected_articles[:max_articles]
    
    # Update state with curated articles
    tool_context.state["articles"] = selected_articles
    
    # Generate a summary of the curation
    source_counts = {}
    category_counts = {}
    
    for article in selected_articles:
        source = article.get("source", "Unknown")
        source_counts[source] = source_counts.get(source, 0) + 1
        
        for category in article.get("categories", []):
            category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        "message": f"Curated {len(selected_articles)} articles from {len(all_articles)} using LLM",
        "source_counts": source_counts,
        "category_counts": category_counts,
        "curated_articles": selected_articles
    }

def categorize_with_llm(tool_context: ToolContext) -> dict:
    """
    Use an LLM to categorize articles into predefined categories.
    
    Args:
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with categorized articles
    """
    print(f"--- Tool: categorize_with_llm called ---")
    
    # Get articles from state
    articles = tool_context.state.get("articles", [])
    
    if not articles:
        return {
            "action": "categorize_with_llm",
            "status": "error",
            "message": "No articles found to categorize. Please curate articles first."
        }
    
    # Define standard categories
    standard_categories = {
        "🎮 Gaming & AI": "Articles about AI in games, game development tools, engines, and gaming industry news",
        "🧠 Major AI Models & Features": "Articles about new AI models, features, capabilities, and technical innovations",
        "🔬 Breakthrough Tech & Regulation": "Articles about hardware, robotics, policy, ethics, and regulatory developments",
        "💰 Business & Funding News": "Articles about investments, acquisitions, business developments, and market trends"
    }
    
    # Prepare the categorized articles structure
    categorized_articles = {category: [] for category in standard_categories.keys()}
    
    # Create a batch of all articles for the LLM
    article_data = []
    for i, article in enumerate(articles):
        article_data.append({
            "id": i,
            "title": article.get("title", ""),
            "summary": article.get("summary", "")
        })
    
    # Create the prompt for the LLM
    prompt = f"""
    You are a newsletter editor specializing in AI and gaming technology news.
    
    Categorize the following articles into the most appropriate categories:
    
    ARTICLES:
    {json.dumps(article_data, indent=2)}
    
    CATEGORIES:
    {json.dumps(standard_categories, indent=2)}
    
    INSTRUCTIONS:
    1. For each article, determine the most appropriate category
    2. Return a JSON array with the following format for each article:
       {{"id": article_index, "category": "category_name"}}
    3. Only use the category names provided above
    4. Try to distribute articles evenly across all four categories when appropriate
    5. Be flexible in your categorization to ensure all categories have articles
    6. Do not include any other text in your response, only the JSON array
    """
    
    try:
        # Call the Generative AI model
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        
        # Parse the response
        try:
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Handle potential formatting issues
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1]
            if response_text.endswith("```"):
                response_text = response_text.split("```")[0]
            
            # Clean up any remaining non-JSON text
            if not response_text.startswith("["):
                response_text = response_text[response_text.find("["):]
            if not response_text.endswith("]"):
                response_text = response_text[:response_text.rfind("]")+1]
            
            # Parse the JSON
            categorization_results = json.loads(response_text)
            
            # Categorize articles
            for result in categorization_results:
                article_id = result.get("id")
                category = result.get("category")
                
                if article_id is not None and 0 <= article_id < len(articles) and category in standard_categories:
                    categorized_articles[category].append(articles[article_id])
                    # Also add the category to the article
                    articles[article_id]["category"] = category
        except Exception as e:
            print(f"  Error parsing LLM response: {str(e)}")
            print(f"  Response text: {response.text}")
            
            # Fallback: distribute articles across categories
            for i, article in enumerate(articles):
                # Distribute evenly across the four categories
                category_keys = list(standard_categories.keys())
                fallback_category = category_keys[i % len(category_keys)]
                categorized_articles[fallback_category].append(article)
    except Exception as e:
        print(f"  Error calling LLM API: {str(e)}")
        
        # Fallback: distribute articles across categories
        for i, article in enumerate(articles):
            # Distribute evenly across the four categories
            category_keys = list(standard_categories.keys())
            fallback_category = category_keys[i % len(category_keys)]
            categorized_articles[fallback_category].append(article)
    
    # Update state with categorized articles
    tool_context.state["categories"] = categorized_articles
    
    # Also store a flattened list of categorized articles for the LLM formatter
    flattened_articles = []
    for category, articles in categorized_articles.items():
        for article in articles:
            article_copy = article.copy()
            if "categories" not in article_copy:
                article_copy["categories"] = []
            if category not in article_copy["categories"]:
                article_copy["categories"].append(category)
            flattened_articles.append(article_copy)
    
    tool_context.state["categorized_articles"] = flattened_articles
    
    # Count articles in each category
    category_counts = {category: len(articles) for category, articles in categorized_articles.items()}
    
    # Remove empty categories
    for category in list(categorized_articles.keys()):
        if not categorized_articles[category]:
            del categorized_articles[category]
    
    return {
        "action": "categorize_with_llm",
        "status": "success",
        "message": f"Categorized {len(articles)} articles into {len(categorized_articles)} categories",
        "category_counts": category_counts
    }
