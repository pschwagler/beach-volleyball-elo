"""
API route handlers for the Beach Volleyball ELO system.
"""

from fastapi import APIRouter, HTTPException
from backend.services import data_service, sheets_service, calculation_service

router = APIRouter()


@router.post("/api/calculate")
async def calculate_stats():
    """
    Trigger ELO calculation from Google Sheets data.
    Loads matches, computes all statistics, flushes DB, and saves to SQLite.
    
    Returns:
        dict: Status and summary of calculations
    """
    try:
        # Load matches from Google Sheets
        match_list = sheets_service.load_matches_from_sheets()
        
        # Process all matches
        tracker = calculation_service.process_matches(match_list)
        
        # Flush and repopulate database
        data_service.flush_and_repopulate(tracker, match_list)
        
        return {
            "status": "success",
            "message": "Statistics calculated and saved successfully",
            "player_count": len(tracker.players),
            "match_count": len(match_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")


@router.get("/api/rankings")
async def get_rankings():
    """
    Get current player rankings.
    
    Returns:
        list: Array of player rankings with stats
    """
    try:
        rankings = data_service.get_rankings()
        if not rankings:
            raise HTTPException(
                status_code=404,
                detail="Rankings not found. Please run /api/calculate first."
            )
        return rankings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading rankings: {str(e)}")


@router.get("/api/players")
async def list_players():
    """
    Get list of all players.
    
    Returns:
        list: Array of player names
    """
    try:
        rankings = data_service.get_rankings()
        return [{"name": player["Name"]} for player in rankings]
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="Player data not found. Please run /api/calculate first."
        )


@router.get("/api/players/{player_name}")
async def get_player_stats(player_name: str):
    """
    Get detailed statistics for a specific player.
    
    Args:
        player_name: Name of the player
        
    Returns:
        list: Array of player stats including partnerships and opponents
    """
    try:
        player_stats = data_service.get_player_stats(player_name)
        
        if player_stats is None:
            raise HTTPException(
                status_code=404,
                detail=f"Player '{player_name}' not found. Please check the name and try again."
            )
        
        return player_stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading player stats: {str(e)}")


@router.get("/api/elo-timeline")
async def get_elo_timeline():
    """
    Get ELO timeline data for all players.
    Useful for creating charts/graphs of ELO changes over time.
    
    Returns:
        list: Array of date/ELO data points for each player
    """
    try:
        timeline = data_service.get_elo_timeline()
        if not timeline:
            raise HTTPException(
                status_code=404,
                detail="ELO timeline not found. Please run /api/calculate first."
            )
        return timeline
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading ELO timeline: {str(e)}")


@router.get("/api/matches")
async def get_matches():
    """
    Get all matches with results.
    
    Returns:
        list: Array of all matches sorted by date (most recent first)
    """
    try:
        matches = data_service.get_matches()
        if not matches:
            raise HTTPException(
                status_code=404,
                detail="Matches not found. Please run /api/calculate first."
            )
        return matches
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading matches: {str(e)}")


@router.get("/api/players/{player_name}/matches")
async def get_player_match_history(player_name: str):
    """
    Get match history for a specific player.
    
    Args:
        player_name: Name of the player
        
    Returns:
        list: Array of player's matches (most recent first)
    """
    try:
        match_history = data_service.get_player_match_history(player_name)
        
        if not match_history:
            raise HTTPException(
                status_code=404,
                detail=f"Match history for '{player_name}' not found. Please check the name and try again."
            )
        
        return match_history
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading match history: {str(e)}")


@router.get("/api/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service status
    """
    try:
        data_available = not data_service.is_database_empty()
        
        return {
            "status": "healthy",
            "data_available": data_available,
            "message": "API is running" if data_available else "No data yet. Run /api/calculate to generate statistics."
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "data_available": False,
            "message": f"Error: {str(e)}"
        }

