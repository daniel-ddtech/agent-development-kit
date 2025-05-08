import os
import json
import requests
import feedparser
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse
import google.generativeai as genai
from bs4 import BeautifulSoup
import time

# Simple tool context class for compatibility
class SimpleToolContext:
    def __init__(self, initial_state=None):
        self.state = initial_state or {}

# Configure the Google Generative AI API if available
api_key = os.getenv("GOOGLE_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Default model to use
DEFAULT_MODEL = "gemini-1.5-pro"

# List of seed sources to start with
SEED_SOURCES = [
    # Gaming industry news
    "https://www.gamasutra.com",
    "https://www.polygon.com",
    "https://kotaku.com",
    "https://www.rockpapershotgun.com",
    "https://www.pcgamer.com",
    
    # AI news
    "https://www.artificialintelligence-news.com",
    "https://venturebeat.com/category/ai",
    "https://www.technologyreview.com/topic/artificial-intelligence",
    "https://www.deeplearning.ai",
    "https://www.fast.ai",
    
    # AI research
    "https://arxiv.org/list/cs.AI/recent",
    "https://distill.pub",
    "https://openai.com/blog",
    "https://ai.googleblog.com",
    "https://research.facebook.com/blog/ai",
    
    # Gaming and AI intersection
    "https://unity.com/solutions/ai-in-games",
    "https://blogs.nvidia.com/blog/category/gaming",
    "https://blogs.nvidia.com/blog/category/deep-learning",
    "https://www.unrealengine.com/en-US/blog"
]

# Keywords to look for when evaluating sources with focus on generative AI in gaming
RELEVANT_KEYWORDS = [
    # Generative AI terms
    "generative ai", "gen ai", "text-to-image", "text-to-video", "text-to-audio", "text-to-3d",
    "diffusion model", "stable diffusion", "midjourney", "dall-e", "imagen",
    "large language model", "llm", "gpt", "claude", "gemini", "llama", "mistral",
    "ai image generation", "ai video generation", "ai audio generation", "ai content creation",
    "generative adversarial network", "gan", "transformer", "foundation model",
    
    # Gaming and generative AI intersection
    "ai in games", "ai-powered games", "procedural generation", "procedural content",
    "ai game assets", "ai level design", "ai character creation", "ai animation",
    "npc behavior", "npc ai", "intelligent npc", "character ai", "dynamic characters",
    "ai storytelling", "narrative generation", "dynamic narrative", "emergent gameplay",
    "ai game testing", "ai playtesting", "ai difficulty scaling", "adaptive gameplay",
    
    # Game development with AI
    "ai game development", "ai game tools", "ai assisted development", "ai asset creation",
    "unity ai", "unreal ai", "godot ai", "game engine ai", "ai plugins",
    "ai voice acting", "ai dialogue", "ai sound design", "ai music generation",
    "ai character design", "ai environment design", "ai texture generation",
    
    # Industry and business
    "ai gaming startup", "ai game studio", "ai gaming investment", "ai gaming funding",
    "ai gaming acquisition", "ai gaming partnership", "ai gaming collaboration",
    "ai gaming technology", "ai gaming platform", "ai gaming infrastructure",
    "ai gaming ethics", "ai gaming regulation", "ai gaming policy"
]

def discover_sources(tool_context: SimpleToolContext) -> dict:
    """
    Discover new potential sources for AI and gaming content.
    
    Args:
        tool_context: Context for accessing state
        
    Returns:
        Dictionary with discovered sources
    """
    print("--- Tool: discover_sources called ---")
    
    # Get existing sources
    existing_sources = tool_context.state.get("rss_feeds", [])
    
    # Initialize discovered sources
    discovered_sources = []
    
    # Start with seed sources if no existing sources
    sources_to_check = existing_sources if existing_sources else SEED_SOURCES
    
    # Discover new sources
    for source in sources_to_check[:5]:  # Limit to 5 to avoid too many requests
        try:
            # Extract domain
            domain = urlparse(source).netloc if urlparse(source).netloc else source
            
            # Search for related sources
            new_sources = _search_related_sources(domain)
            discovered_sources.extend(new_sources)
            
            # Avoid rate limiting
            time.sleep(1)
        except Exception as e:
            print(f"Error discovering sources from {source}: {str(e)}")
    
    # Remove duplicates
    discovered_sources = list(set(discovered_sources))
    
    # Store discovered sources in state
    tool_context.state["discovered_sources"] = discovered_sources
    
    return {
        "action": "discover_sources",
        "status": "success",
        "message": f"Discovered {len(discovered_sources)} potential new sources",
        "sources": discovered_sources[:10]  # Return top 10 for preview
    }

def _search_related_sources(domain: str) -> List[str]:
    """
    Search for sources related to a given domain.
    
    Args:
        domain: Domain to find related sources for
        
    Returns:
        List of related source URLs
    """
    # Curated list of high-quality sources focused on generative AI and generative AI in gaming
    ai_gaming_sources = [
        # Generative AI News & Research
        "https://venturebeat.com/category/ai/feed/",
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.artificialintelligence-news.com/feed/",
        "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "https://ai.googleblog.com/feeds/posts/default",
        "https://openai.com/blog/rss/",
        "https://stability.ai/blog?format=rss",
        "https://huggingface.co/blog/feed.xml",
        "https://www.anthropic.com/blog/rss",
        "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
        "https://aws.amazon.com/blogs/machine-learning/feed/",
        "https://blogs.microsoft.com/ai/feed/",
        "https://www.marktechpost.com/category/artificial-intelligence/feed/",
        "https://aibusiness.com/feed",
        "https://www.unite.ai/feed/",
        
        # Generative AI in Gaming
        "https://www.gamedeveloper.com/rss.xml",
        "https://www.gamesindustry.biz/feed/rss",
        "https://venturebeat.com/category/games/feed/",
        "https://blog.unity.com/topic/ai/rss",
        "https://www.unrealengine.com/en-US/feed/blog/tag/artificial-intelligence",
        "https://www.polygon.com/ai-artificial-intelligence/rss/index.xml",
        "https://www.rockpapershotgun.com/topics/ai/feed",
        "https://www.gameinformer.com/ai/rss.xml",
        "https://www.pcgamer.com/ai/rss",
        "https://www.ign.com/ai/rss",
        "https://www.eurogamer.net/topics/ai/rss",
        "https://www.gamesradar.com/ai/rss",
        "https://www.gamingonlinux.com/article_rss.php?tags=AI",
        
        # AI-Generated Content & Tools
        "https://midjourney.com/blog/rss/",
        "https://runwayml.com/blog/rss/",
        "https://www.artbreeder.com/blog?format=rss",
        "https://www.synthesia.io/blog/rss",
        "https://www.descript.com/blog/rss",
        "https://elevenlabs.io/blog/rss/",
        "https://www.scenario.com/blog/rss",
        
        # Generative AI for NPCs & Game Characters
        "https://convai.com/blog?format=rss",
        "https://inworld.ai/blog?format=rss",
        "https://blog.charisma.ai/rss/",
        "https://www.character.ai/blog?format=rss",
        "https://blog.altera.ai/rss/",
        
        # Generative AI Game Development
        "https://www.gamasutra.com/blogs/rss-generative-ai/",
        "https://towardsdatascience.com/feed/tagged/game-development",
        "https://aiartificial.org/category/gaming/feed/",
        "https://www.kdnuggets.com/tag/game-development/feed",
        "https://www.gamedev.net/rss/forums/topic/26-artificial-intelligence/"
    ]
    
    # Return a subset of these sources (randomized to provide variety)
    import random
    random.shuffle(ai_gaming_sources)
    return ai_gaming_sources[:10]  # Return 10 quality sources

def evaluate_sources(tool_context: SimpleToolContext) -> dict:
    """
    Evaluate discovered sources for quality and relevance.
    
    Args:
        tool_context: Context for accessing state
        
    Returns:
        Dictionary with evaluated sources
    """
    print("--- Tool: evaluate_sources called ---")
    
    # Get discovered sources
    discovered_sources = tool_context.state.get("discovered_sources", [])
    
    if not discovered_sources:
        return {
            "action": "evaluate_sources",
            "status": "error",
            "message": "No discovered sources to evaluate. Run discover_sources first."
        }
    
    # Evaluate each source
    evaluated_sources = []
    
    for source in discovered_sources[:10]:  # Limit to 10 to avoid too many requests
        try:
            # Check if it's an RSS feed
            is_rss, feed_url = _check_if_rss(source)
            
            if is_rss:
                # If it's an RSS feed, evaluate its content
                quality_score, relevance_score, frequency_score = _evaluate_rss_feed(feed_url)
            else:
                # If it's not an RSS feed, try to find RSS feed for the site
                feed_url = _find_rss_feed(source)
                if feed_url:
                    quality_score, relevance_score, frequency_score = _evaluate_rss_feed(feed_url)
                else:
                    # If no RSS feed found, evaluate the website content
                    quality_score, relevance_score, frequency_score = _evaluate_website(source)
            
            # Calculate overall score
            overall_score = (quality_score + relevance_score + frequency_score) / 3
            
            # Add to evaluated sources
            evaluated_sources.append({
                "url": source,
                "feed_url": feed_url if feed_url else None,
                "is_rss": is_rss,
                "quality_score": quality_score,
                "relevance_score": relevance_score,
                "frequency_score": frequency_score,
                "overall_score": overall_score
            })
            
            # Avoid rate limiting
            time.sleep(1)
        except Exception as e:
            print(f"Error evaluating source {source}: {str(e)}")
    
    # Sort by overall score
    evaluated_sources.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
    
    # Store evaluated sources in state
    tool_context.state["evaluated_sources"] = evaluated_sources
    
    return {
        "action": "evaluate_sources",
        "status": "success",
        "message": f"Evaluated {len(evaluated_sources)} sources",
        "sources": evaluated_sources[:5]  # Return top 5 for preview
    }

def _check_if_rss(url: str) -> Tuple[bool, str]:
    """
    Check if a URL is an RSS feed.
    
    Args:
        url: URL to check
        
    Returns:
        Tuple of (is_rss, feed_url)
    """
    try:
        feed = feedparser.parse(url)
        
        # Check if it's a valid feed
        if feed.get('feed') and feed.get('entries'):
            return True, url
        
        return False, ""
    except Exception:
        return False, ""

def _find_rss_feed(url: str) -> str:
    """
    Find RSS feed for a website.
    
    Args:
        url: Website URL
        
    Returns:
        RSS feed URL if found, empty string otherwise
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for RSS link
        for link in soup.find_all('link'):
            if link.get('type') in ['application/rss+xml', 'application/atom+xml']:
                feed_url = link.get('href', '')
                
                # Handle relative URLs
                if feed_url.startswith('/'):
                    parsed_url = urlparse(url)
                    feed_url = f"{parsed_url.scheme}://{parsed_url.netloc}{feed_url}"
                
                return feed_url
        
        # Common RSS feed paths
        common_paths = ['/feed', '/rss', '/rss.xml', '/atom.xml', '/feed.xml']
        
        for path in common_paths:
            parsed_url = urlparse(url)
            feed_url = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"
            
            try:
                feed = feedparser.parse(feed_url)
                if feed.get('feed') and feed.get('entries'):
                    return feed_url
            except Exception:
                pass
        
        return ""
    except Exception as e:
        print(f"Error in _find_rss_feed: {str(e)}")
        return ""

def _evaluate_rss_feed(feed_url: str) -> Tuple[float, float, float]:
    """
    Evaluate an RSS feed for quality, relevance, and frequency.
    
    Args:
        feed_url: RSS feed URL
        
    Returns:
        Tuple of (quality_score, relevance_score, frequency_score)
    """
    try:
        feed = feedparser.parse(feed_url)
        
        # Check quality (based on entry length and content)
        entries = feed.get('entries', [])
        
        if not entries:
            return 0.0, 0.0, 0.0
        
        # Calculate average entry length
        avg_length = sum(len(entry.get('summary', '')) for entry in entries) / len(entries)
        quality_score = min(5.0, avg_length / 200)  # Normalize to 0-5 scale
        
        # Check relevance (based on keywords)
        relevance_count = 0
        for entry in entries:
            title = entry.get('title', '').lower()
            summary = entry.get('summary', '').lower()
            content = title + " " + summary
            
            for keyword in RELEVANT_KEYWORDS:
                if keyword in content:
                    relevance_count += 1
        
        relevance_score = min(5.0, relevance_count / (len(entries) * 2))  # Normalize to 0-5 scale
        
        # Check frequency (based on publication dates)
        if len(entries) >= 2:
            try:
                latest_date = entries[0].get('published_parsed')
                oldest_date = entries[-1].get('published_parsed')
                
                if latest_date and oldest_date:
                    import time
                    latest_timestamp = time.mktime(latest_date)
                    oldest_timestamp = time.mktime(oldest_date)
                    
                    time_diff = latest_timestamp - oldest_timestamp
                    days_diff = time_diff / (60 * 60 * 24)
                    
                    if days_diff > 0:
                        posts_per_week = (len(entries) / days_diff) * 7
                        frequency_score = min(5.0, posts_per_week)  # Normalize to 0-5 scale
                    else:
                        frequency_score = 2.5  # Default if dates are the same
                else:
                    frequency_score = 2.5  # Default if dates not available
            except Exception:
                frequency_score = 2.5  # Default on error
        else:
            frequency_score = 1.0  # Low score if not enough entries
        
        return quality_score, relevance_score, frequency_score
    except Exception as e:
        print(f"Error in _evaluate_rss_feed: {str(e)}")
        return 1.0, 1.0, 1.0  # Default low scores on error

def _evaluate_website(url: str) -> Tuple[float, float, float]:
    """
    Evaluate a website for quality, relevance, and frequency.
    
    Args:
        url: Website URL
        
    Returns:
        Tuple of (quality_score, relevance_score, frequency_score)
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        text_content = soup.get_text()
        
        # Check quality (based on content length)
        quality_score = min(5.0, len(text_content) / 5000)  # Normalize to 0-5 scale
        
        # Check relevance (based on keywords)
        relevance_count = 0
        text_content_lower = text_content.lower()
        
        for keyword in RELEVANT_KEYWORDS:
            if keyword in text_content_lower:
                relevance_count += 1
        
        relevance_score = min(5.0, relevance_count / 5)  # Normalize to 0-5 scale
        
        # Check frequency (based on date elements)
        date_elements = soup.find_all(['time', 'span', 'div'], class_=lambda c: c and ('date' in c.lower() or 'time' in c.lower()))
        frequency_score = min(5.0, len(date_elements) / 2)  # Normalize to 0-5 scale
        
        return quality_score, relevance_score, frequency_score
    except Exception as e:
        print(f"Error in _evaluate_website: {str(e)}")
        return 1.0, 1.0, 1.0  # Default low scores on error

def recommend_sources(tool_context: SimpleToolContext) -> dict:
    """
    Recommend the best sources based on evaluation.
    
    Args:
        tool_context: Context for accessing state
        
    Returns:
        Dictionary with recommended sources
    """
    print("--- Tool: recommend_sources called ---")
    
    # Get evaluated sources
    evaluated_sources = tool_context.state.get("evaluated_sources", [])
    
    if not evaluated_sources:
        return {
            "action": "recommend_sources",
            "status": "error",
            "message": "No evaluated sources to recommend. Run evaluate_sources first."
        }
    
    # Filter for high-quality sources
    recommended_sources = [s for s in evaluated_sources if s.get("overall_score", 0) >= 3.0]
    
    # Get RSS feed URLs for recommended sources
    recommended_feeds = []
    
    for source in recommended_sources:
        if source.get("is_rss") and source.get("url"):
            recommended_feeds.append(source.get("url"))
        elif source.get("feed_url"):
            recommended_feeds.append(source.get("feed_url"))
    
    # Store recommended feeds in state
    tool_context.state["recommended_feeds"] = recommended_feeds
    
    # Update the main RSS feeds list with new recommendations
    existing_feeds = tool_context.state.get("rss_feeds", [])
    updated_feeds = list(set(existing_feeds + recommended_feeds))
    tool_context.state["rss_feeds"] = updated_feeds
    
    return {
        "action": "recommend_sources",
        "status": "success",
        "message": f"Recommended {len(recommended_feeds)} new sources",
        "recommended_feeds": recommended_feeds,
        "total_feeds": len(updated_feeds)
    }

def analyze_source_with_llm(url: str) -> Dict[str, Any]:
    """
    Use LLM to analyze a source for quality and relevance.
    
    Args:
        url: URL to analyze
        
    Returns:
        Dictionary with analysis results
    """
    if not os.getenv("GOOGLE_API_KEY"):
        return {
            "quality": 3.0,
            "relevance": 3.0,
            "analysis": "LLM analysis not available (no API key)"
        }
    
    try:
        # Fetch content
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title and description
        title = soup.title.string if soup.title else "Unknown Title"
        
        # Extract meta description
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")
        
        # Extract some content
        paragraphs = soup.find_all("p")
        content_sample = "\n".join([p.get_text() for p in paragraphs[:5]])
        
        # Create prompt for LLM
        prompt = f"""
        Analyze this website as a potential source for an AI and gaming newsletter:
        
        URL: {url}
        Title: {title}
        Description: {description}
        
        Content sample:
        {content_sample[:500]}...
        
        Please rate and analyze this source on:
        1. Quality (1-5): How well-written and informative is the content?
        2. Relevance (1-5): How relevant is it to AI and gaming topics?
        3. Authority (1-5): How authoritative is this source in the field?
        
        Provide a brief analysis explaining your ratings.
        
        Return ONLY a JSON object with these ratings and analysis.
        Format: {{
            "quality": <number>,
            "relevance": <number>,
            "authority": <number>,
            "analysis": "<brief explanation>"
        }}
        """
        
        # Call the Generative AI model
        model = genai.GenerativeModel(DEFAULT_MODEL)
        response = model.generate_content(prompt)
        
        # Parse the response
        import json
        import re
        
        # Look for JSON content in the response
        json_match = re.search(r'\{[\s\S]*\}', response.text)
        if json_match:
            json_str = json_match.group(0)
            try:
                analysis = json.loads(json_str)
                return analysis
            except json.JSONDecodeError:
                print(f"Could not parse JSON from: {json_str}")
        
        # Default response if parsing fails
        return {
            "quality": 3.0,
            "relevance": 3.0,
            "authority": 3.0,
            "analysis": "Could not parse LLM response"
        }
        
    except Exception as e:
        print(f"Error in analyze_source_with_llm: {str(e)}")
        return {
            "quality": 3.0,
            "relevance": 3.0,
            "authority": 3.0,
            "analysis": f"Error analyzing source: {str(e)}"
        }
