"""
Authentication & Roles Router - Session management and permission profiles.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from ..database import get_db_connection
from ..models import LoginRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication & Roles"])


ROLES_CONFIG = [
    {
        "role": "Administrator",
        "description": "Full access to create, update, delete teams, players, schedule matches, update live scores and configure tournament brackets.",
        "permissions": ["manage_teams", "manage_players", "schedule_matches", "update_scores", "manage_venues", "manage_referees", "manage_bracket"]
    },
    {
        "role": "Coach",
        "description": "Team management, roster lineup view, player stats tracking, and match analysis.",
        "permissions": ["view_roster", "view_analytics", "submit_lineup"]
    },
    {
        "role": "Referee",
        "description": "Live score recording, disciplinary cards (yellow/red), match duration and official reports.",
        "permissions": ["update_scores", "record_cards", "view_assignments"]
    },
    {
        "role": "Player",
        "description": "Personal stats view, team schedule, player rankings, and league standings.",
        "permissions": ["view_profile", "view_schedule", "view_standings"]
    },
    {
        "role": "Fan",
        "description": "Live match center, tournament brackets, league tables, and team news.",
        "permissions": ["view_live_scores", "view_standings", "view_brackets"]
    }
]


@router.get("/roles", summary="List available user roles and permissions")
def get_roles():
    """Retrieve all available system roles with description and permission capabilities."""
    return ROLES_CONFIG


@router.post("/login", response_model=UserResponse, summary="Authenticate user by role or credentials")
def login(login_req: LoginRequest):
    """
    Simulated token authentication for selected user role.
    Supports role-based login matching the frontend UI switcher.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find matching user by role or username
    cursor.execute("SELECT * FROM users WHERE role = ? OR username = ? LIMIT 1", (login_req.role, login_req.username))
    user = cursor.fetchone()
    conn.close()

    if user:
        u_dict = dict(user)
        token = f"apex_jwt_token_{u_dict['id']}_{u_dict['role'].lower()}"
        return UserResponse(
            id=u_dict["id"],
            username=u_dict["username"],
            name=u_dict["name"],
            role=u_dict["role"],
            email=u_dict["email"],
            token=token
        )

    # Fallback default user for selected role
    token = f"apex_token_{login_req.role.lower()}_session"
    return UserResponse(
        id="U_GUEST",
        username=login_req.username or login_req.role.lower(),
        name=f"Verified {login_req.role}",
        role=login_req.role or "Administrator",
        email=f"{login_req.role.lower()}@apexleague.com",
        token=token
    )
