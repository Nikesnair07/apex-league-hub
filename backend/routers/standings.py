"""
Standings Router - Dynamically calculated league table with rankings and qualification zones.
"""

from fastapi import APIRouter
from typing import List
from ..database import get_db_connection
from ..models import StandingEntry

router = APIRouter(prefix="/api/standings", tags=["Standings"])


@router.get("", response_model=List[StandingEntry], summary="Get live league standings table")
def get_standings():
    """
    Retrieve dynamically sorted standings table with points, goal differential,
    and continental/relegation zone classifications.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams")
    teams = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Sort teams by points desc, then goal difference desc, then goals for desc
    def sort_key(t):
        gd = t["goals_for"] - t["goals_against"]
        return (t["points"], gd, t["goals_for"])

    sorted_teams = sorted(teams, key=sort_key, reverse=True)

    standings = []
    total = len(sorted_teams)

    for idx, t in enumerate(sorted_teams):
        rank = idx + 1
        mp = t["wins"] + t["losses"] + t["draws"]
        gd = t["goals_for"] - t["goals_against"]

        if rank <= 4:
            zone = "zone-champions"
        elif rank == 5:
            zone = "zone-europa"
        elif rank >= max(6, total - 1):
            zone = "zone-relegation"
        else:
            zone = "standard"

        standings.append(StandingEntry(
            rank=rank,
            team_id=t["id"],
            team_name=t["name"],
            logo=t["logo"],
            played=mp,
            wins=t["wins"],
            draws=t["draws"],
            losses=t["losses"],
            goals_for=t["goals_for"],
            goals_against=t["goals_against"],
            goal_difference=gd,
            points=t["points"],
            zone=zone
        ))

    return standings
