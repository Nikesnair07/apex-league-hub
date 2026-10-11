"""
Analytics & Reports Router - Executive KPIs, charts data, and league metrics.
"""

from fastapi import APIRouter
from typing import Dict, Any, List
from ..database import get_db_connection
from ..models import KPIStats

router = APIRouter(prefix="/api/analytics", tags=["Analytics & KPIs"])


@router.get("/kpis", response_model=KPIStats, summary="Get 7 executive KPI dashboard metrics")
def get_kpis():
    """Retrieve aggregate statistics for top dashboard overview cards."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM teams")
    total_teams = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM players")
    active_players = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM matches")
    total_matches = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM matches WHERE status = 'LIVE'")
    live_matches = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM matches WHERE status = 'COMPLETED'")
    completed_matches = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM matches WHERE status = 'UPCOMING'")
    upcoming_matches = cursor.fetchone()["count"]

    cursor.execute("SELECT SUM(goals_for) as total_goals FROM teams")
    res_goals = cursor.fetchone()["total_goals"]
    total_goals = res_goals if res_goals is not None else 0

    cursor.execute("SELECT COUNT(*) as count FROM venues")
    total_venues = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM referees")
    total_referees = cursor.fetchone()["count"]

    conn.close()

    avg_goals = round(total_goals / max(completed_matches, 1), 2)

    return KPIStats(
        total_teams=total_teams,
        active_players=active_players,
        total_matches=total_matches,
        live_matches=live_matches,
        completed_matches=completed_matches,
        upcoming_matches=upcoming_matches,
        total_goals_scored=total_goals,
        avg_goals_per_match=avg_goals,
        total_venues=total_venues,
        total_referees=total_referees
    )


@router.get("/team-performance", summary="Get goals scored vs conceded for top teams")
def get_team_performance():
    """Chart 1 data: offensive vs defensive goal comparison for teams."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, goals_for, goals_against FROM teams ORDER BY points DESC LIMIT 6")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {
        "labels": [r["name"] for r in rows],
        "goalsFor": [r["goals_for"] for r in rows],
        "goalsAgainst": [r["goals_against"] for r in rows]
    }


@router.get("/tournament-progress", summary="Get tournament match distribution status")
def get_tournament_progress():
    """Chart 2 data: doughnut chart breakdown of games completed, remaining, and live."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM matches GROUP BY status")
    rows = dict(cursor.fetchall())
    conn.close()

    completed = rows.get("COMPLETED", 0)
    upcoming = rows.get("UPCOMING", 0)
    live = rows.get("LIVE", 0)

    return {
        "labels": ["Completed Games", "Remaining Games", "Live Games"],
        "counts": [completed, upcoming, live]
    }


@router.get("/points-trend", summary="Get points trajectory trend")
def get_points_trend():
    """Points progression curve for top competing franchises."""
    return {
        "weeks": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
        "series": [
            {"team": "Apex Strikers", "points": [3, 6, 9, 12, 13, 16], "color": "#3b82f6"},
            {"team": "Titanium Titans", "points": [3, 4, 7, 10, 13, 14], "color": "#10b981"},
            {"team": "Vanguard Warriors", "points": [1, 4, 7, 10, 11, 13], "color": "#f59e0b"}
        ]
    }
