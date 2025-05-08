#!/usr/bin/env python3
"""
Simple test script to check if futuretools.io scraping is working correctly.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import json
from urllib.parse import urlparse

def fetch_futuretools_news(days=7):
    """
    Scrape news from FutureTools.io
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of article dictionaries
    """
    try:
        # Get the current date and the date 'days' days ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        print(f"Fetching news from FutureTools.io for the last {days} days...")
        
        # Fetch the FutureTools.io news page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get("https://www.futuretools.io/news", headers=headers)
        if response.status_code != 200:
            print(f"Error fetching FutureTools.io: {response.status_code}")
            return []
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all news articles - they're typically in card elements
        articles = []
        news_cards = soup.find_all('div', class_=re.compile('card|news-item|post'))
        
        if not news_cards:
            print("No card elements found, falling back to links...")
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
            print(f"Found {len(news_cards)} card elements...")
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
        
        print(f"Found {len(articles)} articles from FutureTools.io")
        return articles
    except Exception as e:
        print(f"Error scraping FutureTools.io: {str(e)}")
        import traceback
        traceback.print_exc()
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

if __name__ == "__main__":
    # Fetch articles from FutureTools.io for the last 7 days
    articles = fetch_futuretools_news(7)
    
    # Print the articles
    print(f"\nFound {len(articles)} articles from FutureTools.io for the last 7 days:\n")
    
    # Save to a JSON file
    with open("futuretools_articles.json", "w") as f:
        json.dump(articles, f, indent=2)
    
    print(f"Saved {len(articles)} articles to futuretools_articles.json")
    
    # Print the first 5 articles
    for i, article in enumerate(articles[:5], 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['url']}")
        print()
