import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from newsletter_agent.agent import newsletter_agent
from datetime import datetime

# Load environment variables
load_dotenv()

# Database URL for persistent storage
db_url = "sqlite:///./newsletter_test.db"

# Initial state with curated RSS feeds for AI gaming and game development
initial_state = {
    "articles": [],
    "rss_articles": [],
    "google_articles": [],
    "rss_feeds": [
        # Game development news
        "https://www.gamedeveloper.com/rss.xml",
        "https://venturebeat.com/category/games/feed/",
        "https://www.gamesindustry.biz/feed/rss",
        
        # Generative AI news (priority feeds)
        "https://blogs.nvidia.com/blog/category/deep-learning/feed/",  # NVIDIA's AI-focused blog
        "https://aws.amazon.com/blogs/machine-learning/feed/",        # AWS Generative AI Blog
        "https://genai.owasp.org/feed.xml",                          # OWASP GenAI Security
        "https://cloud.google.com/blog/feed/",                       # Google Cloud Blog (includes Vertex AI)
        "https://techcrunch.com/category/artificial-intelligence/feed/", # TechCrunch AI
        
        # AI and technology news
        "https://www.nvidia.com/en-us/about-nvidia/rss/nvidia-ai-news.xml",
        "https://blogs.nvidia.com/feed/",
        "https://machinelearning.apple.com/rss.xml",
        
        # Gaming news
        "https://www.engadget.com/tag/gaming/rss.xml",
        "https://www.polygon.com/rss/index.xml",
        "https://www.rockpapershotgun.com/feed",
        
        # Indie game development
        "https://www.indiedb.com/news/feed/rss.xml",
        "https://blog.unity.com/feed"
    ],
    "last_update": datetime.now().strftime("%Y-%m-%d"),
}

def process_agent_response(response):
    """Process and display the agent's response."""
    if hasattr(response, 'text'):
        return response.text
    elif hasattr(response, 'content') and hasattr(response.content, 'parts'):
        for part in response.content.parts:
            if hasattr(part, 'text'):
                return part.text
    return "No text response found"

async def test_newsletter_generation():
    """Test the complete newsletter generation process."""
    print("\n=== Testing AI in Gaming Newsletter System ===\n")
    
    # Initialize session service
    session_service = DatabaseSessionService(db_url=db_url)
    
    # Create a new session with initial state
    session = session_service.create_session(
        app_name="AI Gaming Newsletter Test",
        user_id="test_user",
        state=initial_state
    )
    
    # Create a runner with our newsletter agent
    runner = Runner(
        agent=newsletter_agent,
        app_name="AI Gaming Newsletter Test",
        session_service=session_service
    )
    
    # Test commands to run through the complete pipeline
    test_commands = [
        "List the RSS feeds we're tracking",
        "Fetch articles from RSS feeds for the last 7 days",
        "Curate the most relevant articles about AI in gaming",
        "Generate summaries with a professional tone",
        "Format the newsletter as markdown"
    ]
    
    # Run each command and display the response
    for i, command in enumerate(test_commands, 1):
        print(f"\nStep {i}: {command}")
        
        # Run the agent with the command
        response = None
        async for event in runner.run("test_user", command):
            if event.is_final_response():
                response = event
        
        # Process and display the response
        if response:
            response_text = process_agent_response(response)
            print(f"\nAgent: {response_text}\n")
        else:
            print("\nNo response received from agent\n")
            
        print("-" * 80)
    
    # Get all sessions for this user
    sessions = session_service.list_sessions(
        app_name="AI Gaming Newsletter Test",
        user_id="test_user"
    )
    
    # Get the most recent session
    if sessions and sessions.sessions:
        final_session = sessions.sessions[0]
    else:
        print("No sessions found!")
        return
    
    # Check if we have a formatted newsletter
    if "formatted_newsletter" in final_session.state:
        print("\n=== Newsletter Generated Successfully ===\n")
        
        # Save the newsletter to a file
        newsletter_format = final_session.state.get("newsletter_format", "markdown")
        file_extension = ".md" if newsletter_format == "markdown" else ".html" if newsletter_format == "html" else ".json"
        
        with open(f"newsletter_{datetime.now().strftime('%Y%m%d')}{file_extension}", "w") as f:
            f.write(final_session.state["formatted_newsletter"])
        
        print(f"Newsletter saved to newsletter_{datetime.now().strftime('%Y%m%d')}{file_extension}")
    else:
        print("\n=== Newsletter Generation Incomplete ===\n")
        print("The newsletter was not fully generated. Check the agent responses for details.")

if __name__ == "__main__":
    asyncio.run(test_newsletter_generation())
