"""
Pydantic models for API request/response validation.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, model_validator


class RankingResponse(BaseModel):
    """Player ranking data."""
    model_config = ConfigDict(populate_by_name=True)
    Name: str
    Points: int
    Games: int
    Win_Rate: float = Field(alias="Win Rate")
    Wins: int
    Losses: int
    Avg_Pt_Diff: float = Field(alias="Avg Pt Diff")
    ELO: int


class PartnershipStats(BaseModel):
    """Partnership statistics."""
    model_config = ConfigDict(populate_by_name=True)
    Partner: str
    Games: int
    Wins: int
    Losses: int
    Win_Rate: float = Field(alias="Win Rate")
    Avg_Pt_Diff: float = Field(alias="Avg Pt Diff")


class OpponentStats(BaseModel):
    """Opponent statistics."""
    model_config = ConfigDict(populate_by_name=True)
    Opponent: str
    Games: int
    Wins: int
    Losses: int
    Win_Rate: float = Field(alias="Win Rate")
    Avg_Pt_Diff: float = Field(alias="Avg Pt Diff")


class PlayerStatsResponse(BaseModel):
    """Combined player statistics."""
    overall: dict
    partnerships: List[PartnershipStats]
    opponents: List[OpponentStats]


class MatchResponse(BaseModel):
    """Match result data."""
    model_config = ConfigDict(populate_by_name=True)
    Date: str
    Team_1_Player_1: str = Field(alias="Team 1 Player 1")
    Team_1_Player_2: str = Field(alias="Team 1 Player 2")
    Team_2_Player_1: str = Field(alias="Team 2 Player 1")
    Team_2_Player_2: str = Field(alias="Team 2 Player 2")
    Team_1_Score: int = Field(alias="Team 1 Score")
    Team_2_Score: int = Field(alias="Team 2 Score")
    Winner: str
    Team_1_ELO_Change: float = Field(alias="Team 1 ELO Change")
    Team_2_ELO_Change: float = Field(alias="Team 2 ELO Change")


class PlayerMatchHistoryResponse(BaseModel):
    """Player's match history."""
    model_config = ConfigDict(populate_by_name=True)
    Date: str
    Partner: str
    Opponent_1: str = Field(alias="Opponent 1")
    Opponent_2: str = Field(alias="Opponent 2")
    Result: str
    Score: str
    ELO_Change: float = Field(alias="ELO Change")


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
    password: str
    name: Optional[str] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Request to login with password. Accepts either phone_number or email."""
    phone_number: Optional[str] = None
    email: Optional[str] = None
    password: str
    
    @model_validator(mode='after')
    def validate_phone_or_email(self):
        """Ensure either phone_number or email is provided."""
        if not self.phone_number and not self.email:
            raise ValueError("Either phone_number or email must be provided")
        if self.phone_number and self.email:
            raise ValueError("Provide either phone_number or email, not both")
        return self


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
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    phone_number: str
    is_verified: bool


class RefreshTokenRequest(BaseModel):
    """Request to refresh access token."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response with new access token."""
    access_token: str
    token_type: str = "bearer"


class CheckPhoneResponse(BaseModel):
    """Response for phone number check."""
    exists: bool
    is_verified: bool


class ResetPasswordRequest(BaseModel):
    """Request to initiate password reset."""
    phone_number: str


class ResetPasswordVerifyRequest(BaseModel):
    """Request to verify code and get reset token."""
    phone_number: str
    code: str


class ResetPasswordConfirmRequest(BaseModel):
    """Request to confirm password reset with token and new password."""
    reset_token: str
    new_password: str


class UserResponse(BaseModel):
    """User information response."""
    id: int
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    is_verified: bool
    created_at: str

