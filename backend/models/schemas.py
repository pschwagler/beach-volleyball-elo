"""
Pydantic models for API request/response validation.
"""

from typing import Optional, List
from pydantic import BaseModel


class RankingResponse(BaseModel):
    """Player ranking data."""
    Name: str
    Points: int
    Games: int
    "Win Rate": float
    Wins: int
    Losses: int
    "Avg Pt Diff": float
    ELO: int


class PartnershipStats(BaseModel):
    """Partnership statistics."""
    Partner: str
    Games: int
    Wins: int
    Losses: int
    "Win Rate": float
    "Avg Pt Diff": float


class OpponentStats(BaseModel):
    """Opponent statistics."""
    Opponent: str
    Games: int
    Wins: int
    Losses: int
    "Win Rate": float
    "Avg Pt Diff": float


class PlayerStatsResponse(BaseModel):
    """Combined player statistics."""
    overall: dict
    partnerships: List[PartnershipStats]
    opponents: List[OpponentStats]


class MatchResponse(BaseModel):
    """Match result data."""
    Date: str
    "Team 1 Player 1": str
    "Team 1 Player 2": str
    "Team 2 Player 1": str
    "Team 2 Player 2": str
    "Team 1 Score": int
    "Team 2 Score": int
    Winner: str
    "Team 1 ELO Change": float
    "Team 2 ELO Change": float


class PlayerMatchHistoryResponse(BaseModel):
    """Player's match history."""
    Date: str
    Partner: str
    "Opponent 1": str
    "Opponent 2": str
    Result: str
    Score: str
    "ELO Change": float


class EloTimelineResponse(BaseModel):
    """ELO timeline data for charting."""
    Date: str
    # Additional fields will be player names with their ELO values


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    data_available: bool
    message: str


class CalculateResponse(BaseModel):
    """Response from calculate endpoint."""
    status: str
    message: str
    player_count: int
    match_count: int


class SessionResponse(BaseModel):
    """Session data."""
    id: int
    date: str
    name: str
    is_pending: bool
    created_at: str


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    date: Optional[str] = None  # If not provided, use current date


class EndSessionRequest(BaseModel):
    """Request to end a session."""
    session_id: int


class CreateMatchRequest(BaseModel):
    """Request to create a new match."""
    session_id: int
    team1_player1: str
    team1_player2: str
    team2_player1: str
    team2_player2: str
    team1_score: int
    team2_score: int


class CreateMatchResponse(BaseModel):
    """Response from creating a match."""
    status: str
    message: str
    match_id: int
    session_id: int


# Authentication schemas

class SignupRequest(BaseModel):
    """Request to sign up a new user."""
    phone_number: str
    password: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Request to login with password."""
    phone_number: str
    password: str


class SMSLoginRequest(BaseModel):
    """Request to login with SMS verification code."""
    phone_number: str
    code: str


class VerifyPhoneRequest(BaseModel):
    """Request to verify phone number with code."""
    phone_number: str
    code: str


class CheckPhoneRequest(BaseModel):
    """Request to check if phone number exists."""
    phone_number: str


class AuthResponse(BaseModel):
    """Authentication response with JWT token."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    phone_number: str
    is_verified: bool


class CheckPhoneResponse(BaseModel):
    """Response for phone number check."""
    exists: bool
    is_verified: bool


class UserResponse(BaseModel):
    """User information response."""
    id: int
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    is_verified: bool
    created_at: str

