"""
Pydantic data models and schemas for request validation and response formatting.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union


# ==========================================
# TEAMS
# ==========================================
class TeamBase(BaseModel):
    name: str = Field(..., description="Team franchise name")
    logo: Optional[str] = Field(None, description="Team logo image URL or SVG")
    coach: str = Field(..., description="Head coach name")
    wins: int = Field(0, description="Total wins")
    losses: int = Field(0, description="Total losses")
    draws: int = Field(0, description="Total draws")
    goals_for: int = Field(0, description="Goals scored")
    goals_against: int = Field(0, description="Goals conceded")
    points: int = Field(0, description="League points")
    city: Optional[str] = Field("City", description="Home city or region")
    founded: Optional[int] = Field(2026, description="Year founded")


class TeamCreate(BaseModel):
    name: str
    coach: str
    city: Optional[str] = "City"
    logo: Optional[str] = None
    founded: Optional[int] = 2026


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    logo: Optional[str] = None
    coach: Optional[str] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    draws: Optional[int] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    points: Optional[int] = None
    city: Optional[str] = None
    founded: Optional[int] = None


class TeamResponse(TeamBase):
    id: str


# ==========================================
# PLAYERS
# ==========================================
class PlayerBase(BaseModel):
    name: str
    age: int = 24
    position: str = Field("Midfielder", description="Position: Forward, Midfielder, Defender, Goalkeeper")
    team_id: Optional[str] = None
    team_name: Optional[str] = "Unassigned"
    jersey_number: int = 10
    goals: int = 0
    assists: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    photo: Optional[str] = None


class PlayerCreate(BaseModel):
    name: str
    age: Optional[int] = 24
    position: str
    team_id: str
    jersey_number: int
    photo: Optional[str] = None


class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    position: Optional[str] = None
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    jersey_number: Optional[int] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    photo: Optional[str] = None


class PlayerResponse(PlayerBase):
    id: str


# ==========================================
# COACHES
# ==========================================
class CoachBase(BaseModel):
    name: str
    team_name: Optional[str] = None
    experience: str = "5 Years"
    nationality: str = "International"
    contact: str = "coach@apexleague.com"
    photo: Optional[str] = None


class CoachCreate(CoachBase):
    pass


class CoachResponse(CoachBase):
    id: str


# ==========================================
# MATCHES
# ==========================================
class MatchBase(BaseModel):
    home_team_id: str
    home_team_name: str
    home_logo: Optional[str] = None
    away_team_id: str
    away_team_name: str
    away_logo: Optional[str] = None
    date: str
    time: str
    venue: str
    referee: Optional[str] = "Michael Oliver"
    status: str = Field("UPCOMING", description="Status: UPCOMING, LIVE, COMPLETED")
    home_score: int = 0
    away_score: int = 0


class MatchCreate(BaseModel):
    home_team_id: str
    away_team_id: str
    date: str
    time: Optional[str] = "19:00 EST"
    venue: str
    referee: Optional[str] = "Michael Oliver"


class MatchScoreUpdate(BaseModel):
    home_score: int
    away_score: int
    status: str = Field("COMPLETED", description="UPCOMING, LIVE, or COMPLETED")


class MatchResponse(MatchBase):
    id: str


# ==========================================
# VENUES & REFEREES
# ==========================================
class VenueBase(BaseModel):
    name: str
    image: Optional[str] = None
    capacity: str
    address: str
    upcoming_matches_count: int = 0


class VenueCreate(VenueBase):
    pass


class VenueResponse(VenueBase):
    id: str


class RefereeBase(BaseModel):
    name: str
    experience: str
    assigned_matches: int = 0
    rating: float = 5.0
    photo: Optional[str] = None


class RefereeCreate(RefereeBase):
    pass


class RefereeResponse(RefereeBase):
    id: str


# ==========================================
# STANDINGS
# ==========================================
class StandingEntry(BaseModel):
    rank: int
    team_id: str
    team_name: str
    logo: Optional[str] = None
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    zone: str  # 'zone-champions', 'zone-europa', 'zone-relegation', or 'standard'


# ==========================================
# TOURNAMENT BRACKET
# ==========================================
class BracketMatch(BaseModel):
    match: str
    team1: str
    score1: Union[int, str]
    team2: str
    score2: Union[int, str]
    winner: str


class BracketData(BaseModel):
    quarterFinals: List[BracketMatch]
    semiFinals: List[BracketMatch]
    final: List[BracketMatch]


class BracketUpdate(BaseModel):
    bracket_data: BracketData


# ==========================================
# ANALYTICS & KPIS
# ==========================================
class KPIStats(BaseModel):
    total_teams: int
    active_players: int
    total_matches: int
    live_matches: int
    completed_matches: int
    upcoming_matches: int
    total_goals_scored: int
    avg_goals_per_match: float
    total_venues: int
    total_referees: int


# ==========================================
# AUTH / USER
# ==========================================
class LoginRequest(BaseModel):
    username: str
    password: Optional[str] = "password"
    role: Optional[str] = "Administrator"


class UserResponse(BaseModel):
    id: str
    username: str
    name: str
    role: str
    email: Optional[str] = None
    token: Optional[str] = None


# ==========================================
# MATCH EVENTS & COMMENTARY
# ==========================================
class MatchEventCreate(BaseModel):
    minute: int = Field(..., ge=1, le=120, description="Match minute when event occurred")
    event_type: str = Field(..., description="GOAL, YELLOW_CARD, RED_CARD, SUBSTITUTION, VAR")
    team_id: Optional[str] = None
    player_id: Optional[str] = None
    player_name: str
    assist_player_name: Optional[str] = None
    detail: Optional[str] = None


class MatchEventResponse(BaseModel):
    id: str
    match_id: str
    minute: int
    event_type: str
    team_id: Optional[str] = None
    player_id: Optional[str] = None
    player_name: str
    assist_player_name: Optional[str] = None
    detail: Optional[str] = None
    created_at: Optional[str] = None


# ==========================================
# TRANSFERS & CONTRACTS
# ==========================================
class TransferCreate(BaseModel):
    player_id: str
    player_name: str
    from_team_id: str
    from_team_name: str
    to_team_id: str
    to_team_name: str
    transfer_fee: float = 0.0
    wage_weekly: float = 0.0
    contract_years: int = 3
    date: str


class TransferUpdate(BaseModel):
    status: str = Field(..., description="PENDING, ACCEPTED, COMPLETED, REJECTED")


class TransferResponse(BaseModel):
    id: str
    player_id: str
    player_name: str
    from_team_id: str
    from_team_name: str
    to_team_id: str
    to_team_name: str
    transfer_fee: float
    wage_weekly: float
    contract_years: int
    status: str
    date: str


# ==========================================
# MATCH TICKETING
# ==========================================
class TicketCreate(BaseModel):
    match_id: str
    category: str = Field("GENERAL", description="VIP, CATEGORY_1, CATEGORY_2, GENERAL")
    customer_name: str
    customer_email: str
    section: Optional[str] = "Section 101"
    seat_number: Optional[str] = "A-1"


class TicketResponse(BaseModel):
    id: str
    match_id: str
    venue_name: str
    section: str
    seat_number: str
    category: str
    price: float
    customer_name: str
    customer_email: str
    booking_reference: str
    status: str


# ==========================================
# PLAYER SCOUTING & PERFORMANCE RADAR
# ==========================================
class PlayerScoutingCreate(BaseModel):
    player_id: str
    player_name: str
    overall_rating: int = Field(..., ge=40, le=99)
    potential: int = Field(..., ge=40, le=99)
    pace: int = Field(..., ge=1, le=99)
    shooting: int = Field(..., ge=1, le=99)
    passing: int = Field(..., ge=1, le=99)
    dribbling: int = Field(..., ge=1, le=99)
    defending: int = Field(..., ge=1, le=99)
    physical: int = Field(..., ge=1, le=99)
    market_value_eur: float = 10000000.0
    preferred_foot: Optional[str] = "Right"
    scout_notes: Optional[str] = None


class PlayerScoutingResponse(BaseModel):
    id: str
    player_id: str
    player_name: str
    overall_rating: int
    potential: int
    pace: int
    shooting: int
    passing: int
    dribbling: int
    defending: int
    physical: int
    market_value_eur: float
    preferred_foot: str
    scout_notes: Optional[str] = None
