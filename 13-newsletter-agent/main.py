import asyncio

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from newsletter_agent.agent import newsletter_agent
from datetime import datetime

load_dotenv()

# ===== PART 1: Initialize Persistent Session Service =====
# Using SQLite database for persistent storage
db_url = "sqlite:///./newsletter_data.db"
session_service = DatabaseSessionService(db_url=db_url)


# ===== PART 2: Define Initial State =====
# This will only be used when creating a new session
initial_state = {
    "articles": [],
    "feedly_articles": [],
    "google_articles": [],
    "newsletter_draft": {},
    "exported_newsletter": "",
    "last_update": datetime.now().strftime("%Y-%m-%d"),
}


async def main_async():
    # Setup constants
    APP_NAME = "AI in Games Newsletter"
    USER_ID = "newsletter_user"

    # ===== PART 3: Session Management - Find or Create =====
    # Check for existing sessions for this user
    existing_sessions = session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    # If there's an existing session, use it, otherwise create a new one
    if existing_sessions and len(existing_sessions.sessions) > 0:
        # Use the most recent session
        SESSION_ID = existing_sessions.sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
    else:
        # Create a new session with initial state
        new_session = session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session: {SESSION_ID}")

    # ===== PART 4: Create Runner with Session =====
    # Create a runner that uses our agent and the session we found/created
    runner = Runner(
        agent=newsletter_agent,
        session_service=session_service,
        session_id=SESSION_ID,
    )

    # ===== PART 5: Run the Agent =====
    print("\n=== AI in Games Newsletter Agent ===")
    print("Type 'exit' to end the conversation.\n")

    # Start the conversation
    user_input = input("You: ")
    
    while user_input.lower() != "exit":
        # Process the user input
        response = await runner.run_text(user_input)
        print(f"\nAgent: {response.text}\n")
        
        # Get the next user input
        user_input = input("You: ")


if __name__ == "__main__":
    asyncio.run(main_async())
