"""
Beach Volleyball ELO API Server

FastAPI server that provides REST endpoints for ELO calculations and statistics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import json
import os
from pathlib import Path

# Import from our modules
import match as sheets_loader
from elo_calculator import process_matches, save_results_to_json

# Global variable to store match_list for API access
current_match_list = []

app = FastAPI(
    title="Beach Volleyball ELO API",
    description="API for calculating and retrieving beach volleyball ELO ratings and statistics",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React build files (production) or fallback to API docs
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the React frontend."""
    try:
        # Try to serve React build first
        with open("frontend/dist/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # Fallback to simple HTML
        return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Beach Volleyball ELO</title>
                    <style>
                        body { font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                        h1 { color: #667eea; }
                        a { color: #667eea; }
                    </style>
                </head>
                <body>
                    <h1>🏐 Beach Volleyball ELO API</h1>
                    <p>API is running successfully!</p>
                    <h2>Available Resources:</h2>
                    <ul>
                        <li><a href="/docs">📚 API Documentation</a> - Interactive API docs</li>
                        <li><a href="/api/health">❤️ Health Check</a> - System status</li>
                    </ul>
                    <p><em>Note: Run frontend build to see the web interface.</em></p>
                </body>
            </html>
        """)


# Mount static assets from React build
try:
    # Mount assets directory
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
    # Mount root static files (images, favicon, etc.) 
    # This needs to be added AFTER other routes to not override API endpoints
except:
    # Assets directory might not exist yet (before build)
    pass


@app.post("/api/calculate")
async def calculate_stats():
    """
    Trigger ELO calculation from Google Sheets data.
    Loads matches, computes all statistics, and saves to JSON files.
    
    Returns:
        dict: Status and summary of calculations
    """
    global current_match_list
    
    try:
        # Load matches from Google Sheets
        match_list = sheets_loader.loadMatches(sheets_loader.google_sheets_name)
        current_match_list = match_list
        
        # Process all matches
        tracker = process_matches(match_list)
        
        # Save results to JSON files (now includes matches and player match history)
        result = save_results_to_json(tracker, match_list)
        
        return {
            "status": "success",
            "message": "Statistics calculated and saved successfully",
            "player_count": result['player_count'],
            "match_count": len(match_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")


@app.get("/api/rankings")
async def get_rankings():
    """
    Get current points rankings.
    
    Returns:
        list: Array of player rankings with stats
    """
    try:
        with open("output/rankings.json", "r") as f:
            rankings = json.load(f)
        return rankings
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail="Rankings not found. Please run /api/calculate first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading rankings: {str(e)}")


@app.get("/api/players")
async def list_players():
    """
    Get list of all players.
    
    Returns:
        list: Array of player names
    """
    try:
        with open("output/rankings.json", "r") as f:
            rankings = json.load(f)
        return [{"name": player["Name"]} for player in rankings]
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Player data not found. Please run /api/calculate first."
        )


@app.get("/api/players/{player_name}")
async def get_player_stats(player_name: str):
    """
    Get detailed statistics for a specific player.
    
    Args:
        player_name: Name of the player
        
    Returns:
        list: Array of player stats including partnerships and opponents
    """
    try:
        # Sanitize the player name to match file naming
        safe_name = "".join(c for c in player_name if c.isalnum() or c in (' ', '-', '_'))
        file_path = f"output/players/{safe_name}.json"
        
        with open(file_path, "r") as f:
            player_stats = json.load(f)
        return player_stats
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Player '{player_name}' not found. Please check the name and try again."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading player stats: {str(e)}")


@app.get("/api/elo-timeline")
async def get_elo_timeline():
    """
    Get ELO timeline data for all players.
    Useful for creating charts/graphs of ELO changes over time.
    
    Returns:
        list: Array of date/ELO data points for each player
    """
    try:
        with open("output/elo_timeline.json", "r") as f:
            timeline = json.load(f)
        return timeline
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="ELO timeline not found. Please run /api/calculate first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading ELO timeline: {str(e)}")


@app.get("/api/matches")
async def get_matches():
    """
    Get all matches with results.
    
    Returns:
        list: Array of all matches sorted by date (most recent first)
    """
    try:
        with open("output/matches.json", "r") as f:
            matches = json.load(f)
        return matches
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Matches not found. Please run /api/calculate first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading matches: {str(e)}")


@app.get("/api/players/{player_name}/matches")
async def get_player_match_history(player_name: str):
    """
    Get match history for a specific player.
    
    Args:
        player_name: Name of the player
        
    Returns:
        list: Array of player's matches (most recent first)
    """
    try:
        # Sanitize the player name to match file naming
        safe_name = "".join(c for c in player_name if c.isalnum() or c in (' ', '-', '_'))
        file_path = f"output/players/{safe_name}_matches.json"
        
        with open(file_path, "r") as f:
            match_history = json.load(f)
        return match_history
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Match history for '{player_name}' not found. Please check the name and try again."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading match history: {str(e)}")


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service status
    """
    # Check if output files exist
    files_exist = os.path.exists("output/rankings.json")
    
    return {
        "status": "healthy",
        "data_available": files_exist,
        "message": "API is running" if files_exist else "No data yet. Run /api/calculate to generate statistics."
    }


# Serve static files (images, etc.) from dist - must be after all API routes
@app.get("/{file_path:path}")
async def serve_static_files(file_path: str):
    """Serve static files from frontend/dist directory."""
    # Don't serve API routes through this catch-all
    if file_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Try to serve the requested file
    full_path = Path(f"frontend/dist/{file_path}")
    if full_path.is_file():
        return FileResponse(full_path)
    
    # If file not found, serve index.html (for React Router)
    return FileResponse("frontend/dist/index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

