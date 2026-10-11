"""
Teams Router - Full CRUD and roster endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
import urllib.parse
from ..database import get_db_connection
from ..models import TeamResponse, TeamCreate, TeamUpdate, PlayerResponse

router = APIRouter(prefix="/api/teams", tags=["Teams"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[TeamResponse], summary="List all teams")
def get_teams(
    sort_by: Optional[str] = Query("points", description="Field to sort by: points, wins, name, goals_for"),
    order: Optional[str] = Query("desc", description="Sort order: asc or desc")
):
    """Retrieve all teams in the league with sorting options."""
    allowed_sorts = {"points": "points", "wins": "wins", "name": "name", "goals_for": "goals_for"}
    sort_column = allowed_sorts.get(sort_by, "points")
    sort_dir = "ASC" if order.lower() == "asc" else "DESC"

    conn = get_db_connection()
    cursor = conn.cursor()
    query = f"SELECT * FROM teams ORDER BY {sort_column} {sort_dir}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{team_id}", response_model=TeamResponse, summary="Get single team details")
def get_team(team_id: str):
    """Retrieve a single team by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Team with ID '{team_id}' not found")
    return row_to_dict(row)


@router.get("/{team_id}/roster", response_model=List[PlayerResponse], summary="Get team player roster")
def get_team_roster(team_id: str):
    """Get all registered players roster for a specific team."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check team exists
    cursor.execute("SELECT id FROM teams WHERE id = ?", (team_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Team with ID '{team_id}' not found")

    cursor.execute("SELECT * FROM players WHERE team_id = ? ORDER BY jersey_number ASC", (team_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED, summary="Create a new team")
def create_team(team_in: TeamCreate):
    """Register and franchise a new team into the league."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM teams")
    count = cursor.fetchone()["count"]
    new_id = f"T{count + 1}"

    logo = team_in.logo or f"https://api.dicebear.com/7.x/identicon/svg?seed={urllib.parse.quote(team_in.name)}"

    cursor.execute("""
        INSERT INTO teams (id, name, logo, coach, wins, losses, draws, goals_for, goals_against, points, city, founded)
        VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, 0, ?, ?)
    """, (new_id, team_in.name, logo, team_in.coach, team_in.city or "City", team_in.founded or 2026))

    conn.commit()

    cursor.execute("SELECT * FROM teams WHERE id = ?", (new_id,))
    created_team = cursor.fetchone()
    conn.close()
    return row_to_dict(created_team)


@router.put("/{team_id}", response_model=TeamResponse, summary="Update team details or record")
def update_team(team_id: str, team_in: TeamUpdate):
    """Update metadata, coach, or win/loss/points record of an existing team."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Team with ID '{team_id}' not found")

    current_dict = row_to_dict(current)
    update_data = team_in.model_dump(exclude_unset=True)

    for field, val in update_data.items():
        current_dict[field] = val

    cursor.execute("""
        UPDATE teams
        SET name = ?, logo = ?, coach = ?, wins = ?, losses = ?, draws = ?,
            goals_for = ?, goals_against = ?, points = ?, city = ?, founded = ?
        WHERE id = ?
    """, (
        current_dict["name"], current_dict["logo"], current_dict["coach"],
        current_dict["wins"], current_dict["losses"], current_dict["draws"],
        current_dict["goals_for"], current_dict["goals_against"], current_dict["points"],
        current_dict["city"], current_dict["founded"], team_id
    ))

    conn.commit()
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    updated = cursor.fetchone()
    conn.close()
    return row_to_dict(updated)


@router.delete("/{team_id}", status_code=status.HTTP_200_OK, summary="Delete a team")
def delete_team(team_id: str):
    """Delete a team from the league."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Team with ID '{team_id}' not found")

    cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    conn.commit()
    conn.close()
    return {"message": f"Team '{team_id}' successfully deleted", "id": team_id}
