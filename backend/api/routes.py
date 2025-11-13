"""
API route handlers for the Beach Volleyball ELO system.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from backend.services import data_service, sheets_service, calculation_service
import httpx
import os
from typing import Optional, Dict, Any
from datetime import datetime

router = APIRouter()

# WhatsApp service URL
WHATSAPP_SERVICE_URL = os.getenv("WHATSAPP_SERVICE_URL", "http://localhost:3001")

# Default timeout for WhatsApp service requests (in seconds)
WHATSAPP_REQUEST_TIMEOUT = 30.0


async def proxy_whatsapp_request(
    method: str,
    path: str,
    body: Optional[Dict[Any, Any]] = None,
    timeout: float = WHATSAPP_REQUEST_TIMEOUT
) -> Dict[Any, Any]:
    """
    Proxy helper function for WhatsApp service requests.
    Handles common error cases and timeouts.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API path (e.g., "/api/whatsapp/status")
        body: Optional request body for POST requests
        timeout: Request timeout in seconds
        
    Returns:
        dict: JSON response from WhatsApp service
        
    Raises:
        HTTPException: With appropriate status code and message
    """
    url = f"{WHATSAPP_SERVICE_URL}{path}"
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                response = await client.post(url, json=body)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Raise for 4xx/5xx status codes
            response.raise_for_status()
            
            return response.json()
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="WhatsApp service is not available. Make sure it's running on port 3001."
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"WhatsApp service request timed out after {timeout} seconds."
        )
    except httpx.HTTPStatusError as e:
        # Forward the status code from the WhatsApp service
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"WhatsApp service error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with WhatsApp service: {str(e)}"
        )


@router.post("/api/loadsheets")
async def load_sheets():
    """
    Load matches from Google Sheets into database and calculate statistics.
    Creates one locked-in session per unique date from sheet data.
    
    Returns:
        dict: Status and summary of calculations
    """
    try:
        # Load matches from Google Sheets
        match_list = sheets_service.load_matches_from_sheets()
        
        # Flush and repopulate database, then calculate stats
        result = data_service.flush_and_repopulate(None, match_list)
        
        return {
            "status": "success",
            "message": "Statistics calculated and saved successfully",
            "player_count": result["player_count"],
            "match_count": result["match_count"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading sheets: {str(e)}")


@router.post("/api/calculate")
async def calculate_stats():
    """
    Recalculate statistics from existing database matches (locked-in sessions only).
    Does not load from Google Sheets - use /api/loadsheets for that.
    
    Returns:
        dict: Status and summary of calculations
    """
    try:
        result = data_service.calculate_stats()
        
        return {
            "status": "success",
            "message": "Statistics recalculated successfully",
            "player_count": result["player_count"],
            "match_count": result["match_count"]
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
        # Get all unique player names from database (not just from rankings)
        players = data_service.get_all_player_names()
        return [{"name": name} for name in players]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading players: {str(e)}"
        )


@router.post("/api/players")
async def create_player(request: Request):
    """
    Create a new player.
    
    Request body:
        {
            "name": "Player Name"
        }
    
    Returns:
        dict: Created player info
    """
    try:
        body = await request.json()
        name = body.get('name', '').strip()
        
        if not name:
            raise HTTPException(status_code=400, detail="Player name is required")
        
        player_id = data_service.get_or_create_player(name)
        
        return {
            "status": "success",
            "message": f"Player '{name}' created successfully",
            "player_id": player_id,
            "name": name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating player: {str(e)}")


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


@router.get("/api/matches/export")
async def export_matches():
    """
    Export all matches to CSV format (Google Sheets compatible).
    
    Returns CSV file with headers: DATE, T1P1, T1P2, T2P1, T2P2, T1SCORE, T2SCORE
    """
    try:
        csv_content = data_service.export_matches_to_csv()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=matches_export.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting matches: {str(e)}")


@router.get("/api/players/{player_name}/matches")
async def get_player_match_history(player_name: str):
    """
    Get match history for a specific player.
    
    Args:
        player_name: Name of the player
        
    Returns:
        list: Array of player's matches (most recent first, may be empty)
    """
    try:
        match_history = data_service.get_player_match_history(player_name)
        
        if match_history is None:
            raise HTTPException(
                status_code=404,
                detail=f"Player '{player_name}' not found. Please check the name and try again."
            )
        
        # Return empty array if player exists but has no matches
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


# WhatsApp proxy endpoints (optional - frontend can also call the service directly)

@router.get("/api/whatsapp/qr")
async def whatsapp_qr():
    """
    Proxy endpoint for WhatsApp QR code.
    
    Returns:
        dict: QR code data and authentication status
    """
    return await proxy_whatsapp_request("GET", "/api/whatsapp/qr")


@router.get("/api/whatsapp/status")
async def whatsapp_status():
    """
    Proxy endpoint for WhatsApp authentication status.
    
    Returns:
        dict: Authentication status
    """
    return await proxy_whatsapp_request("GET", "/api/whatsapp/status")


@router.post("/api/whatsapp/initialize")
async def whatsapp_initialize():
    """
    Proxy endpoint for initializing WhatsApp client.
    
    Returns:
        dict: Initialization status
    """
    return await proxy_whatsapp_request("POST", "/api/whatsapp/initialize")


@router.post("/api/whatsapp/logout")
async def whatsapp_logout():
    """
    Proxy endpoint for logging out of WhatsApp.
    
    Returns:
        dict: Logout status
    """
    return await proxy_whatsapp_request("POST", "/api/whatsapp/logout")


@router.get("/api/whatsapp/groups")
async def whatsapp_groups():
    """
    Proxy endpoint for fetching WhatsApp group chats.
    
    Returns:
        dict: List of group chats
    """
    return await proxy_whatsapp_request("GET", "/api/whatsapp/groups")


@router.post("/api/whatsapp/send")
async def whatsapp_send(request: Request):
    """
    Proxy endpoint for sending WhatsApp messages.
    
    Request body:
        {
            "phoneNumber": "15551234567",  // Optional, for individual messages
            "chatId": "123456789@g.us",    // Optional, for group messages
            "message": "Your message"
        }
    
    Returns:
        dict: Send status
    """
    body = await request.json()
    return await proxy_whatsapp_request("POST", "/api/whatsapp/send", body=body)


@router.get("/api/whatsapp/config")
async def get_whatsapp_config():
    """
    Get WhatsApp configuration (selected group for automated messages).
    
    Returns:
        dict: Configuration including group_id
    """
    try:
        group_id = data_service.get_setting('whatsapp_group_id')
        return {
            "success": True,
            "group_id": group_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading WhatsApp config: {str(e)}")


@router.post("/api/whatsapp/config")
async def set_whatsapp_config(request: Request):
    """
    Set WhatsApp configuration (selected group for automated messages).
    
    Request body:
        {
            "group_id": "123456789@g.us"
        }
    
    Returns:
        dict: Success status
    """
    try:
        body = await request.json()
        group_id = body.get('group_id')
        
        if not group_id:
            raise HTTPException(status_code=400, detail="group_id is required")
        
        data_service.set_setting('whatsapp_group_id', group_id)
        
        return {
            "success": True,
            "message": "WhatsApp group configuration saved",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving WhatsApp config: {str(e)}")


# Session management endpoints

@router.get("/api/sessions")
async def get_sessions():
    """
    Get all sessions.
    
    Returns:
        list: Array of all sessions (most recent first)
    """
    try:
        sessions = data_service.get_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading sessions: {str(e)}")


@router.get("/api/sessions/active")
async def get_active_session():
    """
    Get the currently active session, if any.
    
    Returns:
        dict: Active session or null
    """
    try:
        session = data_service.get_active_session()
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading active session: {str(e)}")


@router.post("/api/sessions")
async def create_session(request: Request):
    """
    Create a new session.
    
    Request body:
        {
            "date": "11/7/2025"  // Optional, defaults to current date
        }
    
    Returns:
        dict: Created session info
    """
    try:
        body = await request.json()
        date = body.get('date')
        
        # If no date provided, use current date
        if not date:
            date = datetime.now().strftime('%-m/%-d/%Y')
        
        session = data_service.create_session(date)
        
        return {
            "status": "success",
            "message": "Session created successfully",
            "session": session
        }
    except ValueError as e:
        # Handle duplicate active session error
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.post("/api/sessions/{session_id}/lockin")
async def lock_in_session_endpoint(session_id: int):
    """
    Lock in a session and recalculate all statistics.
    
    When a session is locked in:
    1. Session is marked as complete (is_pending = 0)
    2. All derived stats recalculated from database (locked-in sessions only)
    3. Newly locked matches now included in rankings, partnerships, opponents, ELO history
    
    Args:
        session_id: ID of session to lock in
    
    Returns:
        dict: Status message with calculation summary
    """
    try:
        success = data_service.lock_in_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Auto-recalculate all stats from locked-in sessions
        result = data_service.calculate_stats()
        
        return {
            "status": "success",
            "message": f"Session submitted and stats recalculated",
            "player_count": result["player_count"],
            "match_count": result["match_count"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error locking in session: {str(e)}")


@router.post("/api/sessions/{session_id}/end")
async def end_session(session_id: int):
    """
    Legacy endpoint - calls lockin for backwards compatibility.
    """
    return await lock_in_session_endpoint(session_id)


@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: int):
    """
    Delete an active session and all its matches.
    Only active (pending) sessions can be deleted.
    
    Args:
        session_id: ID of session to delete
    
    Returns:
        dict: Delete status
    """
    try:
        # Delete the session (and all its matches)
        success = data_service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "status": "success",
            "message": "Session deleted successfully",
            "session_id": session_id
        }
    except ValueError as e:
        # Session is not active (already submitted)
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@router.post("/api/matches/create")
async def create_match(request: Request):
    """
    Create a new match in a session.
    
    Request body:
        {
            "session_id": 1,
            "team1_player1": "Alice",
            "team1_player2": "Bob",
            "team2_player1": "Charlie",
            "team2_player2": "Dave",
            "team1_score": 21,
            "team2_score": 19
        }
    
    Returns:
        dict: Created match info
    """
    try:
        body = await request.json()
        
        # Validate required fields
        required_fields = [
            'session_id', 'team1_player1', 'team1_player2',
            'team2_player1', 'team2_player2', 'team1_score', 'team2_score'
        ]
        for field in required_fields:
            if field not in body:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate all players are distinct
        players = [
            body['team1_player1'], body['team1_player2'],
            body['team2_player1'], body['team2_player2']
        ]
        if len(players) != len(set(players)):
            raise HTTPException(status_code=400, detail="All four players must be distinct")
        
        # Get session to verify it exists and is pending
        session = data_service.get_session(body['session_id'])
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {body['session_id']} not found")
        
        if not session['is_active']:  # is_active still used in dict for API compatibility
            raise HTTPException(status_code=400, detail="Cannot add matches to a submitted session")
        
        # Create the match using the session's date
        match_id = data_service.create_match(
            session_id=body['session_id'],
            date=session['date'],
            team1_player1=body['team1_player1'],
            team1_player2=body['team1_player2'],
            team2_player1=body['team2_player1'],
            team2_player2=body['team2_player2'],
            team1_score=body['team1_score'],
            team2_score=body['team2_score']
        )
        
        return {
            "status": "success",
            "message": "Match created successfully",
            "match_id": match_id,
            "session_id": body['session_id']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating match: {str(e)}")


@router.put("/api/matches/{match_id}")
async def update_match(match_id: int, request: Request):
    """
    Update an existing match.
    
    Args:
        match_id: ID of match to update
    
    Request body:
        {
            "team1_player1": "Alice",
            "team1_player2": "Bob",
            "team2_player1": "Charlie",
            "team2_player2": "Dave",
            "team1_score": 21,
            "team2_score": 19
        }
    
    Returns:
        dict: Update status
    """
    try:
        body = await request.json()
        
        # Validate required fields
        required_fields = [
            'team1_player1', 'team1_player2',
            'team2_player1', 'team2_player2', 'team1_score', 'team2_score'
        ]
        for field in required_fields:
            if field not in body:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate all players are distinct
        players = [
            body['team1_player1'], body['team1_player2'],
            body['team2_player1'], body['team2_player2']
        ]
        if len(players) != len(set(players)):
            raise HTTPException(status_code=400, detail="All four players must be distinct")
        
        # Get match to verify it exists and belongs to active session
        match = data_service.get_match(match_id)
        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
        
        if match['session_active'] is False:
            raise HTTPException(status_code=400, detail="Cannot edit matches in a submitted session")
        
        # Update the match
        success = data_service.update_match(
            match_id=match_id,
            team1_player1=body['team1_player1'],
            team1_player2=body['team1_player2'],
            team2_player1=body['team2_player1'],
            team2_player2=body['team2_player2'],
            team1_score=body['team1_score'],
            team2_score=body['team2_score']
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
        
        return {
            "status": "success",
            "message": "Match updated successfully",
            "match_id": match_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating match: {str(e)}")


@router.delete("/api/matches/{match_id}")
async def delete_match(match_id: int):
    """
    Delete a match.
    
    Args:
        match_id: ID of match to delete
    
    Returns:
        dict: Delete status
    """
    try:
        # Get match to verify it exists and belongs to active session
        match = data_service.get_match(match_id)
        if not match:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
        
        if match['session_active'] is False:
            raise HTTPException(status_code=400, detail="Cannot delete matches in a submitted session")
        
        # Delete the match
        success = data_service.delete_match(match_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
        
        return {
            "status": "success",
            "message": "Match deleted successfully",
            "match_id": match_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting match: {str(e)}")

