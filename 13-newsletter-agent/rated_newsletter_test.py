import os
import json
import argparse
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from google.adk.tools.tool_context import ToolContext
from newsletter_agent.rss_tools import fetch_rss_articles
from newsletter_agent.curator_tools import curate_articles, get_trending_topics
from newsletter_agent.summarizer_tools import summarize_articles
from newsletter_agent.category_tools import categorize_articles
from newsletter_agent.llm_formatter import generate_newsletter_with_llm
from newsletter_agent.rating_system import rate_articles, add_ratings_to_newsletter
from newsletter_agent.source_discovery import discover_sources, evaluate_sources, recommend_sources
from newsletter_agent.llm_curator import curate_with_llm, categorize_with_llm
from newsletter_agent.pure_newsletter import generate_pure_newsletter, add_sources_to_pure_newsletter

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("ERROR: GOOGLE_API_KEY not found in environment variables. LLM formatting will not work.")
    exit(1)

# Simple tool context to mimic the ADK's ToolContext
class SimpleToolContext:
    def __init__(self, initial_state=None):
        self.state = initial_state or {}

# List of RSS feeds for AI in gaming
rss_feeds = [
    # Game development news
    "https://www.gamedeveloper.com/rss.xml",
    "https://venturebeat.com/category/games/feed/",
    
    # Generative AI news
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
    
    # AI and gaming news
    "https://www.engadget.com/tag/gaming/rss.xml",
    "https://www.polygon.com/rss/index.xml",
    
    # Tech and business news
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://cloud.google.com/blog/feed/"
]

# We'll also add a function to scrape FutureTools.io since they don't have an RSS feed
def fetch_futuretools_news(days=7):
    """
    Scrape news from FutureTools.io
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of article dictionaries
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        from datetime import datetime, timedelta
        import re
        from urllib.parse import urlparse, parse_qs
        
        # Get the current date and the date 'days' days ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"  Fetching news from FutureTools.io for the last {days} days...")
        
        # Fetch the FutureTools.io news page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get("https://www.futuretools.io/news", headers=headers)
        if response.status_code != 200:
            print(f"  Error fetching FutureTools.io: {response.status_code}")
            return []
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all news articles - they're typically in card elements
        articles = []
        news_cards = soup.find_all('div', class_=re.compile('card|news-item|post'))
        
        if not news_cards:
            # If we can't find cards, fall back to looking for links
            news_links = soup.find_all('a', href=True)
            
            for link in news_links:
                # Skip navigation links and empty links
                if not link.text or link.text.strip() in ['Terms Of Use', 'Privacy Policy', 'Built by Matt Wolfe', '']:
                    continue
                    
                # Extract article information
                title = link.text.strip()
                url = link['href']
                
                # Only process links that look like news articles
                if not ("utm_source=futuretools.io" in url or "/news/" in url):
                    continue
                
                # Create article object
                article = create_article_object(title, url, end_date)
                if article:
                    articles.append(article)
        else:
            # Process card elements
            for card in news_cards:
                # Find the title and link
                link = card.find('a', href=True)
                if not link:
                    continue
                    
                title = link.text.strip()
                if not title:
                    # Try to find a heading element
                    heading = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if heading:
                        title = heading.text.strip()
                
                url = link['href']
                
                # Create article object
                article = create_article_object(title, url, end_date)
                if article:
                    articles.append(article)
        
        print(f"  Found {len(articles)} articles from FutureTools.io")
        return articles
    except Exception as e:
        print(f"  Error scraping FutureTools.io: {str(e)}")
        return []

def create_article_object(title, url, date):
    """
    Create an article object from extracted information
    
    Args:
        title: Article title
        url: Article URL
        date: Current date
        
    Returns:
        Article dictionary or None if invalid
    """
    if not title or not url:
        return None
        
    # Extract source from URL
    source = "FutureTools.io"
    if "utm_source=futuretools.io" in url:
        # Extract the original source URL
        base_url = url.split("?")[0]
        # Try to extract domain
        try:
            from urllib.parse import urlparse
            domain = urlparse(base_url).netloc
            if domain:
                source = domain
        except:
            pass
    
    # Generate a unique ID for the article
    article_id = f"futuretools_{hash(url)}"
    
    # Create the article object
    article = {
        "id": article_id,
        "title": title,
        "url": url,
        "source": source,
        "published": date.strftime("%Y-%m-%d"),
        "summary": f"From FutureTools.io: {title}",
        "keywords": ["ai", "artificial intelligence", "machine learning", "generative ai"]
    }
    
    return article

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="AI in Gaming Newsletter Generator")
    parser.add_argument(
        "--days", 
        type=int, 
        default=7,
        help="Number of days to look back for articles (default: 7)"
    )
    parser.add_argument(
        "--discover-sources", 
        action="store_true",
        help="Discover and evaluate new content sources before generating the newsletter"
    )
    parser.add_argument(
        "--max-articles", 
        type=int, 
        default=15,
        help="Maximum number of articles to include in the newsletter (default: 15)"
    )
    parser.add_argument(
        "--output-format", 
        choices=["markdown", "html", "json", "all"],
        default="all",
        help="Output format for the newsletter (default: all)"
    )
    args = parser.parse_args()
    
    print("\n=== AI in Gaming Newsletter Generator (With Content Rating) ===\n")
    
    # Initialize tool context with initial state
    context = SimpleToolContext({
        "articles": [],
        "rss_articles": [],
        "rss_feeds": rss_feeds,
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "date": datetime.now().strftime("%Y-%m-%d"),
    })
    
    # Optional: Discover new sources
    if args.discover_sources:
        print("\n=== Source Discovery Agent ===\n")
        print("Step 0.1: Discovering new content sources...")
        discover_result = discover_sources(context)
        print(f"  {discover_result['message']}")
        
        print("\nStep 0.2: Evaluating discovered sources...")
        evaluate_result = evaluate_sources(context)
        if evaluate_result['status'] == "success":
            print(f"  {evaluate_result['message']}")
            print("  Top sources:")
            for i, source in enumerate(evaluate_result.get('sources', [])[:3], 1):
                print(f"    {i}. {source['url']} - Score: {source['overall_score']:.2f}")
        
        print("\nStep 0.3: Recommending high-quality sources...")
        recommend_result = recommend_sources(context)
        if recommend_result['status'] == "success":
            print(f"  {recommend_result['message']}")
            # Update RSS feeds with recommended sources
            if recommend_result.get('recommended_feeds'):
                context.state["rss_feeds"] = list(set(context.state.get("rss_feeds", []) + 
                                              recommend_result.get('recommended_feeds', [])))
                print(f"  Updated RSS feeds list with {len(recommend_result.get('recommended_feeds', []))} new sources")
    
    # Step 1: Fetch articles from RSS feeds and FutureTools.io
    print("\nStep 1: Fetching articles from sources (last {args.days} days)...")
    days_to_fetch = args.days
    
    # Fetch from RSS feeds
    result = fetch_rss_articles(context.state.get("rss_feeds", rss_feeds), days_to_fetch, context)
    rss_article_count = len(context.state.get("rss_articles", []))
    print(f"  {result['message']}")
    
    # Fetch from FutureTools.io
    print("  Fetching from FutureTools.io...")
    futuretools_articles = fetch_futuretools_news(days_to_fetch)
    
    # Add FutureTools articles to the state
    if futuretools_articles:
        # Add to rss_articles
        all_rss_articles = context.state.get("rss_articles", []) + futuretools_articles
        context.state["rss_articles"] = all_rss_articles
        
        # Also add to the main articles list
        existing_ids = {article.get("id", article.get("url", "")) for article in context.state.get("articles", [])}
        for article in futuretools_articles:
            article_id = article.get("id", article.get("url", ""))
            if article_id not in existing_ids:
                context.state.get("articles", []).append(article)
                existing_ids.add(article_id)
        
        print(f"  Added {len(futuretools_articles)} articles from FutureTools.io")
    
    total_articles = len(context.state.get("articles", []))
    print(f"  Total articles fetched: {total_articles}")
    print(f"  Time period: Last {days_to_fetch} days")
    
    # Limit to max_articles for processing
    if total_articles > args.max_articles:
        print(f"  Limiting to {args.max_articles} articles for processing...")
        all_articles = context.state.get("articles", [])
        limited_articles = all_articles[:args.max_articles]
        context.state["articles"] = limited_articles
        print(f"  Limited to {len(limited_articles)} articles for processing")
    
    # Step 2: Curate articles using LLM
    print("\nStep 2: Curating articles with LLM...")
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
        "max_articles": args.max_articles  # Use the command-line parameter
    }
    result = curate_with_llm(curation_criteria, context)
    print(f"  {result['message']}")
    print("  Sources used:")
    for source, count in result.get('source_counts', {}).items():
        print(f"    - {source}: {count} articles")
        
    # Store curated articles in context
    context.state["curated_articles"] = result.get("curated_articles", [])
    
    # Step 3: Identify trending topics
    print("\nStep 3: Identifying trending topics...")
    result = get_trending_topics(context)
    print(f"  {result['message']}")
    if result.get('topics'):
        print("  Trending topics:")
        for topic in result['topics']:
            print(f"    - {topic['topic'].replace('_', ' ').title()}")
    else:
        print("  No trending topics identified.")
    
    # Step 4: Generate summaries
    print("\nStep 4: Generating article summaries...")
    result = summarize_articles("professional", context)
    print(f"  {result['message']}")
    
    # Step 5: Categorize articles with LLM
    print("\nStep 5: Categorizing articles with LLM...")
    result = categorize_with_llm(context)
    print(f"  {result['message']}")
    print("  Categories:")
    for category, count in result['category_counts'].items():
        if count > 0:
            print(f"    - {category}: {count} articles")
    
    # Step 6: Rate articles
    print("\nStep 6: Rating article content...")
    result = rate_articles(context)
    print(f"  {result['message']}")
    
    if result['status'] == 'success' and 'category_ratings' in result:
        print("  Category ratings:")
        for category, rating in result['category_ratings'].items():
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            print(f"    - {category}: {rating}/5 {stars}")
    
    # Step 7: Generate newsletter with LLM
    print("\nStep 7: Generating newsletter with LLM...")
    result = generate_newsletter_with_llm(context)
    print(f"  {result['message']}")
    
    # Step 7.1: Generate pure newsletter without ratings
    print("\nStep 7.1: Generating pure newsletter without ratings...")
    result = generate_pure_newsletter(context)
    print(f"  {result['message']}")
    
    # Step 7.2: Add ratings to the newsletter
    print("\nStep 7.2: Adding ratings to newsletter...")
    result = add_ratings_to_newsletter(context)
    print(f"  {result['message']}")
    
    # Step 7.5: Add sources information to the newsletter
    print("\nStep 7.5: Adding sources information to newsletter...")
    
    # Get all sources used in this newsletter
    used_sources = set()
    for article in context.state.get("articles", []):
        source = article.get("source", "Unknown")
        if source != "Unknown":
            used_sources.add(source)
    
    # Get recommended sources if available
    recommended_sources = context.state.get("recommended_feeds", [])
    
    # Format sources section
    sources_section = "\n\n## 📚 Sources\n\n"
    
    # Add used sources
    if used_sources:
        sources_section += "### Sources Used in This Newsletter\n\n"
        for i, source in enumerate(sorted(used_sources), 1):
            sources_section += f"{i}. **{source}**\n"
    
    # Add recommended sources if available
    if recommended_sources:
        sources_section += "\n### Recommended New Sources\n\n"
        sources_section += "These sources were discovered by our AI and may provide valuable content for future newsletters:\n\n"
        for i, source in enumerate(recommended_sources[:5], 1):  # Limit to top 5
            # Extract domain name for cleaner display
            try:
                from urllib.parse import urlparse
                domain = urlparse(source).netloc
                sources_section += f"{i}. **{domain}** - [Visit]({source})\n"
            except:
                sources_section += f"{i}. {source}\n"
    
    # Add to all newsletter versions
    for version in ["rated_newsletter", "llm_newsletter", "bullet_newsletter", "basic_newsletter"]:
        if version in context.state:
            context.state[version] += sources_section
    
    # Add sources to pure newsletter
    result = add_sources_to_pure_newsletter(context)
    print(f"  {result['message']}")
    
    print(f"  Added information about {len(used_sources)} used sources and {len(recommended_sources)} recommended sources")
    
    # Step 8: Save the newsletter to files based on output format
    print("\nStep 8: Saving newsletter to file...")
    today_date = datetime.now().strftime("%Y%m%d")
    
    # Function to convert markdown to HTML
    def markdown_to_html(markdown_content):
        try:
            import markdown
            html_content = markdown.markdown(markdown_content)
            
            # Add basic HTML structure and styling
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI & Gaming Newsletter</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #1E88E5; border-bottom: 2px solid #1E88E5; padding-bottom: 10px; }}
                    h2 {{ color: #7E57C2; margin-top: 1.5rem; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
                    h3 {{ color: #43A047; }}
                    .star-filled {{ color: #FFD700; }}
                    .star-empty {{ color: #CCCCCC; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Replace star ratings with colored stars
            html = html.replace("★", '<span class="star-filled">★</span>')
            html = html.replace("☆", '<span class="star-empty">☆</span>')
            
            return html
        except ImportError:
            print("  Warning: 'markdown' package not installed. Using basic HTML conversion.")
            # Very basic markdown to HTML conversion
            html = markdown_content
            html = html.replace("\n\n", "</p><p>")
            html = html.replace("# ", "<h1>")
            html = html.replace("## ", "<h2>")
            html = html.replace("### ", "<h3>")
            html = "<p>" + html + "</p>"
            return html
    
    # Save based on output format
    if args.output_format in ["markdown", "all"]:
        # Save the rated newsletter
        rated_filename = f"newsletter_rated_{today_date}.md"
        with open(rated_filename, "w") as f:
            f.write(context.state.get("rated_newsletter", "No newsletter generated"))
        print(f"  Saved rated newsletter to {rated_filename}")
        
        # Save the LLM newsletter
        llm_filename = f"newsletter_llm_{today_date}.md"
        with open(llm_filename, "w") as f:
            f.write(context.state.get("llm_newsletter", "No LLM newsletter generated"))
        print(f"  Saved LLM newsletter to {llm_filename}")
        
        # Save the bullet point newsletter
        bullet_filename = f"newsletter_bullets_{today_date}.md"
        with open(bullet_filename, "w") as f:
            f.write(context.state.get("bullet_newsletter", "No bullet point newsletter generated"))
        print(f"  Saved bullet point newsletter to {bullet_filename}")
        
        # Save the basic newsletter
        basic_filename = f"newsletter_{today_date}.md"
        with open(basic_filename, "w") as f:
            f.write(context.state.get("basic_newsletter", "No basic newsletter generated"))
        print(f"  Saved basic newsletter to {basic_filename}")
    
    if args.output_format in ["html", "all"]:
        # Convert and save as HTML
        rated_html_filename = f"newsletter_rated_{today_date}.html"
        with open(rated_html_filename, "w") as f:
            f.write(markdown_to_html(context.state.get("rated_newsletter", "No newsletter generated")))
        print(f"  Saved rated newsletter HTML to {rated_html_filename}")
    
    if args.output_format in ["json", "all"]:
        # Save as JSON with all versions and metadata
        json_filename = f"newsletter_{today_date}.json"
        newsletter_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "versions": {
                "rated": context.state.get("rated_newsletter", "No newsletter generated"),
                "llm": context.state.get("llm_newsletter", "No LLM newsletter generated"),
                "bullets": context.state.get("bullet_newsletter", "No bullet point newsletter generated"),
                "basic": context.state.get("basic_newsletter", "No basic newsletter generated")
            },
            "metadata": {
                "article_count": len(context.state.get("articles", [])),
                "sources": list(set([a.get("source", "Unknown") for a in context.state.get("articles", [])])),
                "trending_topics": context.state.get("trending_topics", []),
                "categories": context.state.get("categories", {})
            }
        }
        with open(json_filename, "w") as f:
            json.dump(newsletter_data, f, indent=2)
        print(f"  Saved newsletter data to {json_filename}")
    
    print("\nNewsletter generation complete!")
    
    # Print a sample of the newsletter
    print("\nNewsletter Preview:")
    print("-" * 80)
    preview = context.state.get("rated_newsletter", "No newsletter generated")
    print(preview[:800] + "..." if len(preview) > 800 else preview)
    print("-" * 80)

if __name__ == "__main__":
    main()
