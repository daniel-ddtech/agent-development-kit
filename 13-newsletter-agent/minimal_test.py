#!/usr/bin/env python3
"""
Minimal test script for newsletter generation
This is a simplified version for testing only
"""

import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set")
genai.configure(api_key=api_key)

def main():
    # Load sample articles from file
    print("\nLoading sample articles...")
    with open("sample_articles.json", "r") as f:
        sample_articles = json.load(f)
    
    print(f"Loaded {len(sample_articles)} sample articles")
    
    # Create a simple state dictionary to mimic the tool context
    state = {"articles": sample_articles}
    
    # Curate articles using LLM directly
    print("\nCurating articles with LLM...")
    
    # Process articles in a single batch
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # Create a simple prompt for curation
    prompt = f"""
    You are an expert curator for an AI & Gaming newsletter. Your task is to evaluate and categorize articles from the list below.

    FOCUS AREAS (in order of priority):
    1. Generative AI in gaming (primary focus)
    2. AI-powered game development tools and assets
    3. AI NPCs and character behavior in games
    4. Procedural generation and content creation for games
    5. Major generative AI model releases and updates
    6. Business and funding in AI gaming
    7. AI ethics and policy in gaming

    ARTICLES TO EVALUATE:
    {json.dumps(sample_articles, indent=2)}

    INSTRUCTIONS:
    1. Evaluate each article's relevance to our focus areas
    2. For each article, assign a relevance score (1-10) and provide a brief justification
    3. Select the top 5 most relevant articles
    4. Return your evaluation as a JSON array with the following format for each selected article:
       {{"id": article_index, "relevance_score": score, "justification": "brief explanation", "categories": ["primary category", "secondary category"]}}
    5. Do not include any other text in your response, only the JSON array

    Be inclusive in your evaluation. We want a good mix of articles about generative AI in gaming, general generative AI news, and related topics.
    """
    
    try:
        response = model.generate_content(prompt)
        print("LLM response received!")
        
        # Parse the response
        response_text = response.text.strip()
        
        # Check if the response starts with ```json and ends with ```
        if response_text.startswith("```json") and response_text.endswith("```"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```") and response_text.endswith("```"):
            response_text = response_text[3:-3].strip()
        
        # Parse the JSON
        curated_results = json.loads(response_text)
        
        # Print the results
        print(f"\nCurated {len(curated_results)} articles:")
        for result in curated_results:
            article_id = result.get("id")
            if article_id is not None and 0 <= article_id < len(sample_articles):
                article = sample_articles[article_id]
                print(f"- {article.get('title', 'No title')} (Score: {result.get('relevance_score', 0)})")
                print(f"  Categories: {', '.join(result.get('categories', []))}")
                print(f"  Justification: {result.get('justification', 'None')}")
                print()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
    
    # Generate a newsletter with the curated articles
    print("\nGenerating newsletter...")
    
    # Prepare the curated articles
    curated_articles = []
    for result in curated_results:
        article_id = result.get("id")
        if article_id is not None and 0 <= article_id < len(sample_articles):
            article = sample_articles[article_id].copy()
            article["relevance_score"] = result.get("relevance_score", 0)
            article["justification"] = result.get("justification", "")
            article["categories"] = result.get("categories", [])
            curated_articles.append(article)
    
    # Generate newsletter with LLM using the bullet-point template
    newsletter_prompt = f"""
    You are an expert newsletter writer specializing in AI and gaming. Create a professional weekly roundup newsletter using the following curated articles.
    
    ARTICLES:
    {json.dumps(curated_articles, indent=2)}
    
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
    3. If there are no relevant articles for a section, include 1-2 bullets with "No major updates this week" or similar.
    4. Keep the emoji headers and section dividers exactly as shown.
    5. Focus on generative AI in gaming and its impact on game development.
    6. DO NOT include the HTML comments in the final output.
    7. Maintain the footer text about thread and subscribe.
    """
    
    try:
        response = model.generate_content(newsletter_prompt)
        print("Newsletter generated!")
        
        # Save the newsletter to a file
        newsletter_content = response.text.strip()
        current_date = datetime.now().strftime("%Y%m%d")
        newsletter_filename = f"newsletter_test_{current_date}.md"
        
        with open(newsletter_filename, "w") as f:
            f.write(newsletter_content)
        
        print(f"\nNewsletter saved to {newsletter_filename}")
        print("\nNewsletter Preview:")
        print("-" * 80)
        print(newsletter_content[:500] + "..." if len(newsletter_content) > 500 else newsletter_content)
        print("-" * 80)
        
    except Exception as e:
        print(f"Error generating newsletter: {str(e)}")
    
    print("\nMinimal test complete!")

if __name__ == "__main__":
    main()
