"""
Matches Router - Scheduling, live fixtures, score updates, and match results.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..database import get_db_connection
from ..models import MatchResponse, MatchCreate, MatchScoreUpdate, MatchEventResponse, MatchEventCreate

router = APIRouter(prefix="/api/matches", tags=["Matches"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[MatchResponse], summary="List and filter league matches")
def get_matches(
    match_status: Optional[str] = Query("ALL", description="Filter by status: ALL, LIVE, UPCOMING, COMPLETED")
):
    """Retrieve all league matches with optional status filter."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if match_status and match_status.upper() != "ALL":
        cursor.execute("SELECT * FROM matches WHERE status = ? ORDER BY date DESC, time DESC", (match_status.upper(),))
    else:
        cursor.execute("SELECT * FROM matches ORDER BY date DESC, time DESC")

    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{match_id}", response_model=MatchResponse, summary="Get match details by ID")
def get_match(match_id: str):
    """Retrieve details for a single fixture or result."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Match with ID '{match_id}' not found")
    return row_to_dict(row)


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED, summary="Schedule new match fixture")
def schedule_match(match_in: MatchCreate):
    """Schedule a new match fixture between two teams."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Look up home team
    cursor.execute("SELECT * FROM teams WHERE id = ?", (match_in.home_team_id,))
    home_team = cursor.fetchone()
    if not home_team:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Home team ID '{match_in.home_team_id}' does not exist")

    # Look up away team
    cursor.execute("SELECT * FROM teams WHERE id = ?", (match_in.away_team_id,))
    away_team = cursor.fetchone()
    if not away_team:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Away team ID '{match_in.away_team_id}' does not exist")

    cursor.execute("SELECT COUNT(*) as count FROM matches")
    count = cursor.fetchone()["count"]
    new_id = f"M{count + 101}"

    cursor.execute("""
        INSERT INTO matches (
            id, home_team_id, home_team_name, home_logo, away_team_id, away_team_name, away_logo,
            date, time, venue, referee, status, home_score, away_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'UPCOMING', 0, 0)
    """, (
        new_id,
        home_team["id"], home_team["name"], home_team["logo"],
        away_team["id"], away_team["name"], away_team["logo"],
        match_in.date, match_in.time or "19:00 EST",
        match_in.venue, match_in.referee or "Michael Oliver"
    ))

    # Increment upcoming matches on venue if matching
    cursor.execute("""
        UPDATE venues SET upcoming_matches_count = upcoming_matches_count + 1 WHERE name = ?
    """, (match_in.venue,))

    conn.commit()
    cursor.execute("SELECT * FROM matches WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)


@router.put("/{match_id}/score", response_model=MatchResponse, summary="Update live or final match score")
def update_match_score(match_id: str, score_in: MatchScoreUpdate):
    """Update live score, final score, and match status (LIVE, COMPLETED, UPCOMING)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    match = cursor.fetchone()
    if not match:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Match with ID '{match_id}' not found")

    old_status = match["status"]
    new_status = score_in.status.upper()

    cursor.execute("""
        UPDATE matches
        SET home_score = ?, away_score = ?, status = ?
        WHERE id = ?
    """, (score_in.home_score, score_in.away_score, new_status, match_id))

    # If the match transitioned to COMPLETED for the first time, update team records
    if new_status == "COMPLETED" and old_status != "COMPLETED":
        h_id = match["home_team_id"]
        a_id = match["away_team_id"]
        h_score = score_in.home_score
        a_score = score_in.away_score

        if h_score > a_score:
            cursor.execute("""
                UPDATE teams
                SET wins = wins + 1, points = points + 3, goals_for = goals_for + ?, goals_against = goals_against + ?
                WHERE id = ?
            """, (h_score, a_score, h_id))
            cursor.execute("""
                UPDATE teams
                SET losses = losses + 1, goals_for = goals_for + ?, goals_against = goals_against + ?
                WHERE id = ?
            """, (a_score, h_score, a_id))
        elif a_score > h_score:
            cursor.execute("""
                UPDATE teams
                SET wins = wins + 1, points = points + 3, goals_for = goals_for + ?, goals_against = goals_against + ?
                WHERE id = ?
            """, (a_score, h_score, a_id))
            cursor.execute("""
                UPDATE teams
                SET losses = losses + 1, goals_for = goals_for + ?, goals_against = goals_against + ?
                WHERE id = ?
            """, (h_score, a_score, h_id))
        else:
            cursor.execute("""
                UPDATE teams
                SET draws = draws + 1, points = points + 1, goals_for = goals_for + ?, goals_against = goals_against + ?
                WHERE id = ?
            """, (h_score, a_score, h_id))
            cursor.execute("""
                UPDATE teams
                SET draws = draws + 1, points = points + 1, goals_for = goals_for + ?, goals_against = goals_against + ?
                WHERE id = ?
            """, (a_score, h_score, a_id))

    conn.commit()
    cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    updated = cursor.fetchone()
    conn.close()
    return row_to_dict(updated)


@router.delete("/{match_id}", status_code=status.HTTP_200_OK, summary="Delete a match")
def delete_match(match_id: str):
    """Delete a match fixture or record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Match with ID '{match_id}' not found")

    cursor.execute("DELETE FROM matches WHERE id = ?", (match_id,))
    conn.commit()
    conn.close()
    return {"message": f"Match '{match_id}' successfully removed", "id": match_id}


# ==========================================
# MATCH EVENTS & LIVE COMMENTARY
# ==========================================
@router.get("/{match_id}/events", response_model=List[MatchEventResponse], summary="Get live match events & commentary timeline")
def get_match_events(match_id: str):
    """Retrieve chronological event timeline (goals, cards, substitutions) for a match."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM matches WHERE id = ?", (match_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Match with ID '{match_id}' not found")

    cursor.execute("SELECT * FROM match_events WHERE match_id = ? ORDER BY minute ASC", (match_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.post("/{match_id}/events", response_model=MatchEventResponse, status_code=status.HTTP_201_CREATED, summary="Log live match event")
def log_match_event(match_id: str, event_in: MatchEventCreate):
    """Add a live event (Goal, Yellow Card, Red Card, Sub) to the match commentary feed."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
    match = cursor.fetchone()
    if not match:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Match with ID '{match_id}' not found")

    cursor.execute("SELECT COUNT(*) as count FROM match_events")
    count = cursor.fetchone()["count"]
    new_id = f"E{count + 1}"

    cursor.execute("""
        INSERT INTO match_events (id, match_id, minute, event_type, team_id, player_id, player_name, assist_player_name, detail)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        new_id, match_id, event_in.minute, event_in.event_type.upper(),
        event_in.team_id, event_in.player_id, event_in.player_name,
        event_in.assist_player_name, event_in.detail
    ))

    # If event is a GOAL and player belongs to a team, update team score if live
    if event_in.event_type.upper() == "GOAL" and event_in.team_id:
        if event_in.team_id == match["home_team_id"]:
            cursor.execute("UPDATE matches SET home_score = home_score + 1 WHERE id = ?", (match_id,))
        elif event_in.team_id == match["away_team_id"]:
            cursor.execute("UPDATE matches SET away_score = away_score + 1 WHERE id = ?", (match_id,))

    # If player_id is provided, update player stats
    if event_in.player_id:
        if event_in.event_type.upper() == "GOAL":
            cursor.execute("UPDATE players SET goals = goals + 1 WHERE id = ?", (event_in.player_id,))
        elif event_in.event_type.upper() == "YELLOW_CARD":
            cursor.execute("UPDATE players SET yellow_cards = yellow_cards + 1 WHERE id = ?", (event_in.player_id,))
        elif event_in.event_type.upper() == "RED_CARD":
            cursor.execute("UPDATE players SET red_cards = red_cards + 1 WHERE id = ?", (event_in.player_id,))

    conn.commit()
    cursor.execute("SELECT * FROM match_events WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)
