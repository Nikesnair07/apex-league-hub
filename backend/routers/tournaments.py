"""
Tournaments Router - Knockout brackets and tournament stage progression.
"""

from fastapi import APIRouter, HTTPException, status
import json
from typing import Dict, Any, List
from ..database import get_db_connection
from ..models import BracketData, BracketUpdate

router = APIRouter(prefix="/api/tournaments", tags=["Tournaments"])


@router.get("/bracket", response_model=BracketData, summary="Get tournament knockout bracket")
def get_bracket():
    """Retrieve current knockout bracket tree (quarter-finals, semi-finals, grand final)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT bracket_data FROM tournaments LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Tournament bracket data not found")

    bracket_dict = json.loads(row["bracket_data"])
    return bracket_dict


@router.put("/bracket", response_model=BracketData, summary="Update tournament knockout bracket")
def update_bracket(bracket_update: BracketUpdate):
    """Update knockout bracket matchups, scores, and advancing winners."""
    conn = get_db_connection()
    cursor = conn.cursor()

    json_str = json.dumps(bracket_update.bracket_data.model_dump())
    cursor.execute("UPDATE tournaments SET bracket_data = ?", (json_str,))
    conn.commit()

    cursor.execute("SELECT bracket_data FROM tournaments LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return json.loads(row["bracket_data"])


@router.get("/group-stage", summary="Get tournament group stage standings")
def get_group_stage():
    """Retrieve top seeded group stage snapshot for tournament contenders."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams ORDER BY points DESC LIMIT 4")
    teams = [dict(r) for r in cursor.fetchall()]
    conn.close()

    group_rows = []
    for t in teams:
        group_rows.append({
            "team_id": t["id"],
            "team_name": t["name"],
            "played": 3,
            "wins": t["wins"],
            "draws": t["draws"],
            "losses": t["losses"],
            "points": t["points"]
        })
    return {"group": "Group A - Champions", "standings": group_rows}
