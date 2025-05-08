#!/usr/bin/env python3
"""
Source Discovery Agent for AI & Gaming Newsletter

This script demonstrates the use of the source discovery agent to find,
evaluate, and recommend high-quality content sources for the newsletter.
"""

import os
import json
import argparse
from dotenv import load_dotenv

# Simple tool context to mimic the ADK's ToolContext
class SimpleToolContext:
    def __init__(self, initial_state=None):
        self.state = initial_state or {}

from newsletter_agent.source_discovery import (
    discover_sources,
    evaluate_sources,
    recommend_sources
)

# Load environment variables
load_dotenv()

def main():
    """Main function to run the source discovery process."""
    parser = argparse.ArgumentParser(description="Discover sources for AI & Gaming Newsletter")
    parser.add_argument(
        "--action", 
        choices=["discover", "evaluate", "recommend", "all"],
        default="all",
        help="Action to perform (default: all)"
    )
    parser.add_argument(
        "--output", 
        default="sources.json",
        help="Output file for discovered sources (default: sources.json)"
    )
    args = parser.parse_args()
    
    # Initialize tool context
    tool_context = SimpleToolContext()
    
    # Load existing RSS feeds if available
    try:
        with open("rss_feeds.json", "r") as f:
            tool_context.state["rss_feeds"] = json.load(f)
        print(f"Loaded {len(tool_context.state['rss_feeds'])} existing RSS feeds")
    except FileNotFoundError:
        tool_context.state["rss_feeds"] = []
        print("No existing RSS feeds found, starting fresh")
    
    results = {}
    
    # Run the requested actions
    if args.action in ["discover", "all"]:
        print("\n=== DISCOVERING SOURCES ===")
        discover_result = discover_sources(tool_context)
        results["discover"] = discover_result
        print(f"Discovered {len(discover_result.get('sources', []))} potential new sources")
        for i, source in enumerate(discover_result.get('sources', []), 1):
            print(f"{i}. {source}")
    
    if args.action in ["evaluate", "all"]:
        print("\n=== EVALUATING SOURCES ===")
        evaluate_result = evaluate_sources(tool_context)
        results["evaluate"] = evaluate_result
        
        if evaluate_result.get("status") == "success":
            print(f"Evaluated {len(evaluate_result.get('sources', []))} sources")
            print("\nTop sources by overall score:")
            for i, source in enumerate(evaluate_result.get('sources', []), 1):
                print(f"{i}. {source['url']} - Score: {source['overall_score']:.2f}")
                print(f"   Quality: {source['quality_score']:.2f}, Relevance: {source['relevance_score']:.2f}, Frequency: {source['frequency_score']:.2f}")
                print(f"   RSS Feed: {source['feed_url'] if source['feed_url'] else 'Not found'}")
                print()
        else:
            print(f"Error: {evaluate_result.get('message')}")
    
    if args.action in ["recommend", "all"]:
        print("\n=== RECOMMENDING SOURCES ===")
        recommend_result = recommend_sources(tool_context)
        results["recommend"] = recommend_result
        
        if recommend_result.get("status") == "success":
            print(f"Recommended {len(recommend_result.get('recommended_feeds', []))} new sources")
            for i, feed in enumerate(recommend_result.get('recommended_feeds', []), 1):
                print(f"{i}. {feed}")
            
            # Save updated RSS feeds
            with open("rss_feeds.json", "w") as f:
                json.dump(tool_context.state.get("rss_feeds", []), f, indent=2)
            print(f"\nTotal feeds after recommendations: {recommend_result.get('total_feeds', 0)}")
            print("Updated feeds saved to rss_feeds.json")
        else:
            print(f"Error: {recommend_result.get('message')}")
    
    # Save all results
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll results saved to {args.output}")

if __name__ == "__main__":
    main()
