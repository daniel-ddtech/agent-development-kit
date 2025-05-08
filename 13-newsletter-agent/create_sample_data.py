#!/usr/bin/env python3
"""
Create sample articles file for quick testing
"""

import json
import os
from datetime import datetime, timedelta

# Create sample articles manually
sample_articles = [
    {
        "title": "AI-Powered NPCs Are Revolutionizing Game Development",
        "link": "https://example.com/article1",
        "published": (datetime.now() - timedelta(days=2)).isoformat(),
        "summary": "Game developers are using generative AI to create more realistic and responsive NPCs.",
        "source": "gamedeveloper",
        "source_title": "Game Developer"
    },
    {
        "title": "Unity Announces New AI Tools for Game Developers",
        "link": "https://example.com/article2",
        "published": (datetime.now() - timedelta(days=3)).isoformat(),
        "summary": "Unity has released a new suite of AI tools to help game developers create more immersive experiences.",
        "source": "gamedeveloper",
        "source_title": "Game Developer"
    },
    {
        "title": "Procedural Generation Gets a Boost from New AI Models",
        "link": "https://example.com/article3",
        "published": (datetime.now() - timedelta(days=1)).isoformat(),
        "summary": "New AI models are making procedural generation more powerful and accessible for game developers.",
        "source": "gamedeveloper",
        "source_title": "Game Developer"
    },
    {
        "title": "The Ethics of AI in Gaming: A Deep Dive",
        "link": "https://example.com/article4",
        "published": (datetime.now() - timedelta(days=4)).isoformat(),
        "summary": "Exploring the ethical considerations of using AI in gaming, from player privacy to algorithmic bias.",
        "source": "gamedeveloper",
        "source_title": "Game Developer"
    },
    {
        "title": "How AI is Changing Game Testing and QA",
        "link": "https://example.com/article5",
        "published": (datetime.now() - timedelta(days=2)).isoformat(),
        "summary": "AI-powered testing tools are revolutionizing how games are tested and debugged.",
        "source": "gamedeveloper",
        "source_title": "Game Developer"
    },
    {
        "title": "Google Announces New Generative AI Features",
        "link": "https://example.com/article6",
        "published": (datetime.now() - timedelta(days=5)).isoformat(),
        "summary": "Google has unveiled new generative AI features for developers and consumers.",
        "source": "techcrunch",
        "source_title": "TechCrunch"
    },
    {
        "title": "The Rise of AI Voice Actors in Games",
        "link": "https://example.com/article7",
        "published": (datetime.now() - timedelta(days=3)).isoformat(),
        "summary": "Game studios are increasingly using AI-generated voices for characters in their games.",
        "source": "GamesBeat News | VentureBeat",
        "source_title": "GamesBeat"
    },
    {
        "title": "AI Art Tools Finding Their Way Into Game Asset Creation",
        "link": "https://example.com/article8",
        "published": (datetime.now() - timedelta(days=2)).isoformat(),
        "summary": "Game artists are incorporating AI art generation tools into their workflows.",
        "source": "GamesBeat News | VentureBeat",
        "source_title": "GamesBeat"
    },
    {
        "title": "Funding Round: AI Gaming Startup Raises $50M",
        "link": "https://example.com/article9",
        "published": (datetime.now() - timedelta(days=1)).isoformat(),
        "summary": "A startup focused on AI for gaming has raised $50 million in Series B funding.",
        "source": "GamesBeat News | VentureBeat",
        "source_title": "GamesBeat"
    },
    {
        "title": "OpenAI's Latest Model Shows Promise for Game Dialogue",
        "link": "https://example.com/article10",
        "published": (datetime.now() - timedelta(days=4)).isoformat(),
        "summary": "OpenAI's newest model is being tested for creating dynamic game dialogue systems.",
        "source": "gamedeveloper",
        "source_title": "Game Developer"
    }
]

# Save to file
with open('sample_articles.json', 'w') as f:
    json.dump(sample_articles, f, indent=2)

print(f"Saved {len(sample_articles)} sample articles to sample_articles.json")
