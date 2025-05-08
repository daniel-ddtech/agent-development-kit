#!/usr/bin/env python3
"""
Quick test script for newsletter generation
This is a simplified version for testing only
"""

import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from google.adk.tools.tool_context import ToolContext
from newsletter_agent.llm_curator import curate_with_llm, categorize_with_llm

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
genai.configure(api_key=api_key)

def main():
    # Create context
    context = ToolContext()
    
    # Load sample articles from file
    print("\nLoading sample articles...")
    with open("sample_articles.json", "r") as f:
        sample_articles = json.load(f)
    
    # Limit to 10 articles for quick testing
    sample_articles = sample_articles[:10]
    print(f"Loaded {len(sample_articles)} sample articles")
    
    # Store in context
    context.state["articles"] = sample_articles
    
    # Step 1: Curate articles using LLM
    print("\nStep 1: Curating articles with LLM...")
    curation_criteria = {
        "focus_areas": [
            "Generative AI in gaming (primary focus)",
            "AI-powered game development tools and assets",
            "AI NPCs and character behavior in games",
            "Procedural generation and content creation for games",
            "Major generative AI model releases and updates",
            "Business and funding in AI gaming",
            "AI ethics and policy in gaming"
        ],
        "max_articles": 5  # Small number for quick testing
    }
    result = curate_with_llm(curation_criteria, context)
    print(f"  {result['message']}")
    print("  Sources used:")
    for source, count in result.get('source_counts', {}).items():
        print(f"    - {source}: {count} articles")
    
    # Store curated articles in context
    context.state["curated_articles"] = result.get("curated_articles", [])
    
    # Step 2: Categorize articles with LLM
    print("\nStep 2: Categorizing articles with LLM...")
    result = categorize_with_llm(context)
    print(f"  {result['message']}")
    print("  Categories:")
    for category, count in result.get('category_counts', {}).items():
        if count > 0:
            print(f"    - {category}: {count} articles")
    
    # Print categorized articles
    print("\nCategorized Articles:")
    for i, article in enumerate(context.state.get("categorized_articles", []), 1):
        print(f"{i}. {article.get('title', 'No title')} - {', '.join(article.get('categories', []))}")
    
    print("\nQuick test complete!")

if __name__ == "__main__":
    main()
