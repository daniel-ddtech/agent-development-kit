import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.adk.tools.tool_context import ToolContext

def fetch_spreadsheet_articles(spreadsheet_url: str, days: int, tool_context: ToolContext) -> dict:
    """Fetch recent articles from a Google Spreadsheet.
    
    Args:
        spreadsheet_url: URL of the Google Spreadsheet (e.g., "https://docs.google.com/spreadsheets/d/103g1TNDIyp1h0kiiZ43ReJWuUnrz_GGTNsFcrjjMxEE/edit?usp=sharing")
        days: Number of days to look back
        tool_context: Context for accessing and updating session state
        
    Returns:
        A dictionary with fetched articles
    """
    print(f"--- Tool: fetch_spreadsheet_articles called for {spreadsheet_url} (last {days} days) ---")
    
    # Get current articles from state or initialize empty list
    articles = tool_context.state.get("articles", [])
    spreadsheet_articles = tool_context.state.get("spreadsheet_articles", [])
    
    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
    try:
        # Set up credentials
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Check for credentials file
        creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        if not os.path.exists(creds_file):
            return {
                "action": "fetch_spreadsheet_articles",
                "status": "error",
                "message": f"Credentials file '{creds_file}' not found. Set GOOGLE_CREDENTIALS_FILE environment variable to the path of your Google API credentials file."
            }
        
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)
        
        # Extract spreadsheet ID from URL
        # Example URL: https://docs.google.com/spreadsheets/d/103g1TNDIyp1h0kiiZ43ReJWuUnrz_GGTNsFcrjjMxEE/edit?usp=sharing
        spreadsheet_id = spreadsheet_url.split('/d/')[1].split('/')[0]
        
        # Open the spreadsheet
        sheet = client.open_by_key(spreadsheet_id).sheet1
        
        # Get all records
        records = sheet.get_all_records()
        
        # Process each row
        new_articles = []
        for idx, row in enumerate(records):
            # Expected columns: Title, URL, Date, Source, Summary
            # If these don't exist, use fallbacks
            
            # Parse date (assuming format YYYY-MM-DD)
            published_date = datetime.now()  # Default to current date
            date_str = row.get('Date', '')
            if date_str:
                try:
                    published_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    # Try other common date formats
                    try:
                        published_date = datetime.strptime(date_str, '%m/%d/%Y')
                    except ValueError:
                        try:
                            published_date = datetime.strptime(date_str, '%d/%m/%Y')
                        except ValueError:
                            # Keep default current date
                            pass
            
            # Skip if older than cutoff date
            if published_date < cutoff_date:
                continue
            
            # Create article object
            article = {
                "id": f"spreadsheet_{idx}_{row.get('URL', '')}",
                "title": row.get('Title', 'Untitled'),
                "url": row.get('URL', ''),
                "published": published_date.strftime("%Y-%m-%d"),
                "source": row.get('Source', 'Google Spreadsheet'),
                "summary": row.get('Summary', '')[:500] + ('...' if len(row.get('Summary', '')) > 500 else '')
            }
            
            new_articles.append(article)
        
        # Store the fetched articles in state
        spreadsheet_articles = new_articles
        tool_context.state["spreadsheet_articles"] = spreadsheet_articles
        
        # Merge with existing articles (avoiding duplicates by ID)
        existing_ids = {article["id"] for article in articles}
        for article in spreadsheet_articles:
            if article["id"] not in existing_ids:
                articles.append(article)
                existing_ids.add(article["id"])
        
        # Update the combined articles in state
        tool_context.state["articles"] = articles
        
        return {
            "action": "fetch_spreadsheet_articles",
            "articles_found": len(spreadsheet_articles),
            "total_articles": len(articles),
            "message": f"Found {len(spreadsheet_articles)} articles from spreadsheet in the last {days} days."
        }
    
    except Exception as e:
        print(f"Error fetching spreadsheet {spreadsheet_url}: {str(e)}")
        return {
            "action": "fetch_spreadsheet_articles",
            "status": "error",
            "message": f"Error: {str(e)}"
        }
