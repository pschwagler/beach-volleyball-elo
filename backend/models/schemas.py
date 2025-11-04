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

