"""
Players Router - Full CRUD, filtering, searching and statistical updates.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..database import get_db_connection
from ..models import PlayerResponse, PlayerCreate, PlayerUpdate

router = APIRouter(prefix="/api/players", tags=["Players"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[PlayerResponse], summary="List and filter players")
def get_players(
    team_id: Optional[str] = Query(None, description="Filter by team ID (e.g. T1)"),
    position: Optional[str] = Query(None, description="Filter by position (e.g. Forward, Midfielder)"),
    search: Optional[str] = Query(None, description="Search by player name or jersey number"),
    sort_by: Optional[str] = Query("goals", description="Sort by: goals, assists, name, jersey_number, age"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    limit: Optional[int] = Query(100, ge=1, le=500),
    offset: Optional[int] = Query(0, ge=0)
):
    """Retrieve player directory with flexible filters for team, position, and search text."""
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if team_id and team_id.upper() != "ALL":
        conditions.append("team_id = ?")
        params.append(team_id)

    if position and position.upper() != "ALL":
        conditions.append("position = ?")
        params.append(position)

    if search:
        s = f"%{search.strip()}%"
        conditions.append("(LOWER(name) LIKE LOWER(?) OR CAST(jersey_number AS TEXT) = ?)")
        params.extend([s, search.strip()])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    allowed_sorts = {"goals": "goals", "assists": "assists", "name": "name", "jersey_number": "jersey_number", "age": "age"}
    sort_col = allowed_sorts.get(sort_by, "goals")
    sort_dir = "ASC" if order.lower() == "asc" else "DESC"

    query = f"SELECT * FROM players {where_clause} ORDER BY {sort_col} {sort_dir} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{player_id}", response_model=PlayerResponse, summary="Get single player details")
def get_player(player_id: str):
    """Retrieve a single player by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Player with ID '{player_id}' not found")
    return row_to_dict(row)


@router.post("", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED, summary="Register a new player")
def create_player(player_in: PlayerCreate):
    """Register a new player to an existing team."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Look up team name
    team_name = "Unassigned"
    if player_in.team_id:
        cursor.execute("SELECT name FROM teams WHERE id = ?", (player_in.team_id,))
        team_row = cursor.fetchone()
        if team_row:
            team_name = team_row["name"]

    cursor.execute("SELECT COUNT(*) as count FROM players")
    count = cursor.fetchone()["count"]
    new_id = f"P{count + 101}"

    photo = player_in.photo or "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80"

    cursor.execute("""
        INSERT INTO players (id, name, age, position, team_id, team_name, jersey_number, goals, assists, yellow_cards, red_cards, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, 0, 0, ?)
    """, (
        new_id, player_in.name, player_in.age or 24, player_in.position,
        player_in.team_id, team_name, player_in.jersey_number, photo
    ))

    conn.commit()
    cursor.execute("SELECT * FROM players WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)


@router.put("/{player_id}", response_model=PlayerResponse, summary="Update player profile or stats")
def update_player(player_id: str, player_in: PlayerUpdate):
    """Update profile attributes or statistical counters for a player."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    current = cursor.fetchone()
    if not current:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Player with ID '{player_id}' not found")

    current_dict = row_to_dict(current)
    update_data = player_in.model_dump(exclude_unset=True)

    # If team_id changed and team_name not explicitly provided, update team_name
    if "team_id" in update_data and "team_name" not in update_data:
        cursor.execute("SELECT name FROM teams WHERE id = ?", (update_data["team_id"],))
        t_row = cursor.fetchone()
        if t_row:
            update_data["team_name"] = t_row["name"]

    for field, val in update_data.items():
        current_dict[field] = val

    cursor.execute("""
        UPDATE players
        SET name = ?, age = ?, position = ?, team_id = ?, team_name = ?,
            jersey_number = ?, goals = ?, assists = ?, yellow_cards = ?, red_cards = ?, photo = ?
        WHERE id = ?
    """, (
        current_dict["name"], current_dict["age"], current_dict["position"],
        current_dict["team_id"], current_dict["team_name"], current_dict["jersey_number"],
        current_dict["goals"], current_dict["assists"], current_dict["yellow_cards"],
        current_dict["red_cards"], current_dict["photo"], player_id
    ))

    conn.commit()
    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    updated = cursor.fetchone()
    conn.close()
    return row_to_dict(updated)


@router.delete("/{player_id}", status_code=status.HTTP_200_OK, summary="Delete player record")
def delete_player(player_id: str):
    """Remove a player from the directory."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Player with ID '{player_id}' not found")

    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    return {"message": f"Player '{player_id}' removed successfully", "id": player_id}
