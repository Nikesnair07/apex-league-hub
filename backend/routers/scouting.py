"""
Player Scouting & Performance Radar Router.
Detailed player attributes (Pace, Shooting, Passing, Dribbling, Defending, Physical),
overall ratings, market valuations, and technical scout notes.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..database import get_db_connection
from ..models import PlayerScoutingResponse, PlayerScoutingCreate

router = APIRouter(prefix="/api/scouting", tags=["Player Scouting & Performance Radar"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[PlayerScoutingResponse], summary="List player scouting radar reports")
def get_all_scouting(
    sort_by: Optional[str] = Query("overall_rating", description="overall_rating, market_value_eur, potential, pace"),
    order: Optional[str] = Query("desc", description="asc or desc")
):
    """Retrieve player scouting radar stats, market values, and attribute breakdown."""
    allowed = {"overall_rating": "overall_rating", "market_value_eur": "market_value_eur", "potential": "potential", "pace": "pace"}
    col = allowed.get(sort_by, "overall_rating")
    dir_str = "ASC" if order.lower() == "asc" else "DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM player_scouting ORDER BY {col} {dir_str}")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{player_id}", response_model=PlayerScoutingResponse, summary="Get scouting report for player")
def get_player_scouting(player_id: str):
    """Retrieve in-depth scouting radar metrics for a specific player ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM player_scouting WHERE player_id = ?", (player_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Scouting data for player '{player_id}' not found")
    return row_to_dict(row)


@router.post("", response_model=PlayerScoutingResponse, status_code=status.HTTP_201_CREATED, summary="Create or update scouting report")
def create_or_update_scouting(report_in: PlayerScoutingCreate):
    """Submit a professional technical scouting report for a player."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM player_scouting WHERE player_id = ?", (report_in.player_id,))
    existing = cursor.fetchone()

    if existing:
        scout_id = existing["id"]
        cursor.execute("""
            UPDATE player_scouting
            SET overall_rating = ?, potential = ?, pace = ?, shooting = ?, passing = ?,
                dribbling = ?, defending = ?, physical = ?, market_value_eur = ?, preferred_foot = ?, scout_notes = ?
            WHERE id = ?
        """, (
            report_in.overall_rating, report_in.potential, report_in.pace,
            report_in.shooting, report_in.passing, report_in.dribbling,
            report_in.defending, report_in.physical, report_in.market_value_eur,
            report_in.preferred_foot or "Right", report_in.scout_notes, scout_id
        ))
    else:
        cursor.execute("SELECT COUNT(*) as count FROM player_scouting")
        count = cursor.fetchone()["count"]
        scout_id = f"SC{count + 1}"

        cursor.execute("""
            INSERT INTO player_scouting (
                id, player_id, player_name, overall_rating, potential, pace, shooting, passing,
                dribbling, defending, physical, market_value_eur, preferred_foot, scout_notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scout_id, report_in.player_id, report_in.player_name,
            report_in.overall_rating, report_in.potential, report_in.pace,
            report_in.shooting, report_in.passing, report_in.dribbling,
            report_in.defending, report_in.physical, report_in.market_value_eur,
            report_in.preferred_foot or "Right", report_in.scout_notes
        ))

    conn.commit()
    cursor.execute("SELECT * FROM player_scouting WHERE id = ?", (scout_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_dict(row)
