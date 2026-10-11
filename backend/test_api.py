"""
Comprehensive Automated Test Suite for Apex Sports League Hub API.
Tests all endpoints: Teams, Players, Matches, Standings, Tournaments,
Venues, Referees, Analytics, and Auth.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_suite():
    print("🚀 Starting comprehensive backend test suite...")
    passed = 0
    total = 0

    def assert_eq(actual, expected, message):
        nonlocal passed, total
        total += 1
        if actual == expected:
            passed += 1
            print(f"  ✅ PASS: {message}")
        else:
            print(f"  ❌ FAIL: {message} -> Expected {expected}, got {actual}")

    # 1. Health check
    res = client.get("/api/health")
    assert_eq(res.status_code, 200, "Health check status 200")
    assert_eq(res.json().get("status"), "healthy", "Health status healthy")

    # 2. API Root Gateway
    res = client.get("/")
    assert_eq(res.status_code, 200, "Root API Gateway status 200")
    assert_eq("docs_url" in res.json(), True, "Root response contains docs_url")

    # 3. Teams API
    res = client.get("/api/teams")
    assert_eq(res.status_code, 200, "GET /api/teams status 200")
    teams = res.json()
    assert_eq(len(teams) >= 8, True, f"Teams count >= 8 (found {len(teams)})")

    # Team detail & roster
    res = client.get("/api/teams/T1")
    assert_eq(res.status_code, 200, "GET /api/teams/T1 status 200")
    assert_eq(res.json().get("name"), "Apex Strikers FC", "Team T1 name is Apex Strikers FC")

    res = client.get("/api/teams/T1/roster")
    assert_eq(res.status_code, 200, "GET /api/teams/T1/roster status 200")
    roster = res.json()
    assert_eq(len(roster) > 0, True, f"Team T1 has {len(roster)} players")

    # Create team
    res = client.post("/api/teams", json={
        "name": "Galactic Force FC",
        "coach": "Zinedine Zidane",
        "city": "Dallas",
        "founded": 2026
    })
    assert_eq(res.status_code, 201, "POST /api/teams status 201")
    new_team = res.json()
    new_team_id = new_team.get("id")
    assert_eq(new_team.get("name"), "Galactic Force FC", "Created team name matches")

    # Update team
    res = client.put(f"/api/teams/{new_team_id}", json={"points": 15, "wins": 5})
    assert_eq(res.status_code, 200, f"PUT /api/teams/{new_team_id} status 200")
    assert_eq(res.json().get("points"), 15, "Team updated points match")

    # 4. Players API
    res = client.get("/api/players")
    assert_eq(res.status_code, 200, "GET /api/players status 200")
    players = res.json()
    assert_eq(len(players) >= 10, True, f"Players count >= 10 (found {len(players)})")

    # Filter players
    res = client.get("/api/players?team_id=T1")
    assert_eq(res.status_code, 200, "GET /api/players?team_id=T1 status 200")
    res = client.get("/api/players?position=Forward")
    assert_eq(res.status_code, 200, "GET /api/players?position=Forward status 200")
    res = client.get("/api/players?search=Lucas")
    assert_eq(res.status_code, 200, "GET /api/players?search=Lucas status 200")
    assert_eq(len(res.json()) >= 1, True, "Search for Lucas found player")

    # Register player
    res = client.post("/api/players", json={
        "name": "Cristiano Silva",
        "position": "Forward",
        "team_id": "T1",
        "jersey_number": 7
    })
    assert_eq(res.status_code, 201, "POST /api/players status 201")
    new_player_id = res.json().get("id")

    # Delete test player
    res = client.delete(f"/api/players/{new_player_id}")
    assert_eq(res.status_code, 200, f"DELETE /api/players/{new_player_id} status 200")

    # Delete test team
    res = client.delete(f"/api/teams/{new_team_id}")
    assert_eq(res.status_code, 200, f"DELETE /api/teams/{new_team_id} status 200")

    # 5. Matches API
    res = client.get("/api/matches")
    assert_eq(res.status_code, 200, "GET /api/matches status 200")
    matches = res.json()
    assert_eq(len(matches) >= 4, True, f"Matches count >= 4 (found {len(matches)})")

    # Filter match status
    res = client.get("/api/matches?match_status=LIVE")
    assert_eq(res.status_code, 200, "GET /api/matches?match_status=LIVE status 200")

    # Schedule match
    res = client.post("/api/matches", json={
        "home_team_id": "T1",
        "away_team_id": "T3",
        "date": "2026-08-15",
        "time": "20:00 EST",
        "venue": "Metropolitan Grand Arena"
    })
    assert_eq(res.status_code, 201, "POST /api/matches status 201")
    new_match_id = res.json().get("id")

    # Update match score
    res = client.put(f"/api/matches/{new_match_id}/score", json={
        "home_score": 3,
        "away_score": 2,
        "status": "COMPLETED"
    })
    assert_eq(res.status_code, 200, f"PUT /api/matches/{new_match_id}/score status 200")
    assert_eq(res.json().get("home_score"), 3, "Updated home score matches")

    # 6. Standings API
    res = client.get("/api/standings")
    assert_eq(res.status_code, 200, "GET /api/standings status 200")
    standings = res.json()
    assert_eq(len(standings) >= 8, True, "Standings table contains all teams")
    assert_eq(standings[0].get("rank"), 1, "First rank is 1")
    assert_eq("zone" in standings[0], True, "Standings entry contains zone classification")

    # 7. Tournaments / Bracket API
    res = client.get("/api/tournaments/bracket")
    assert_eq(res.status_code, 200, "GET /api/tournaments/bracket status 200")
    bracket = res.json()
    assert_eq("quarterFinals" in bracket, True, "Bracket has quarterFinals")
    assert_eq(len(bracket["quarterFinals"]), 4, "Quarter-finals count 4")

    res = client.get("/api/tournaments/group-stage")
    assert_eq(res.status_code, 200, "GET /api/tournaments/group-stage status 200")

    # 8. Coaches API
    res = client.get("/api/coaches")
    assert_eq(res.status_code, 200, "GET /api/coaches status 200")
    assert_eq(len(res.json()) >= 4, True, "Coaches directory populated")

    # 9. Venues API
    res = client.get("/api/venues")
    assert_eq(res.status_code, 200, "GET /api/venues status 200")
    assert_eq(len(res.json()) >= 3, True, "Venues list populated")

    # 10. Referees API
    res = client.get("/api/referees")
    assert_eq(res.status_code, 200, "GET /api/referees status 200")
    assert_eq(len(res.json()) >= 4, True, "Referees list populated")

    # 11. Analytics & KPIs
    res = client.get("/api/analytics/kpis")
    assert_eq(res.status_code, 200, "GET /api/analytics/kpis status 200")
    kpis = res.json()
    assert_eq(kpis.get("total_teams") >= 8, True, "KPI total_teams valid")

    res = client.get("/api/analytics/team-performance")
    assert_eq(res.status_code, 200, "GET /api/analytics/team-performance status 200")

    res = client.get("/api/analytics/tournament-progress")
    assert_eq(res.status_code, 200, "GET /api/analytics/tournament-progress status 200")

    # 12. Auth API
    res = client.get("/api/auth/roles")
    assert_eq(res.status_code, 200, "GET /api/auth/roles status 200")
    assert_eq(len(res.json()), 5, "5 roles supported")

    res = client.post("/api/auth/login", json={"username": "admin", "role": "Administrator"})
    assert_eq(res.status_code, 200, "POST /api/auth/login status 200")
    assert_eq(res.json().get("role"), "Administrator", "Auth role matches")

    # 13. Match Events & Live Commentary
    res = client.get("/api/matches/M101/events")
    assert_eq(res.status_code, 200, "GET /api/matches/M101/events status 200")
    events = res.json()
    assert_eq(len(events) >= 1, True, f"Match M101 has {len(events)} events")

    res = client.post("/api/matches/M101/events", json={
        "minute": 75,
        "event_type": "YELLOW_CARD",
        "team_id": "T1",
        "player_id": "P101",
        "player_name": "Lucas Sterling",
        "detail": "Simulation in penalty box"
    })
    assert_eq(res.status_code, 201, "POST /api/matches/M101/events status 201")

    # 14. Transfers & Contracts
    res = client.get("/api/transfers")
    assert_eq(res.status_code, 200, "GET /api/transfers status 200")
    transfers = res.json()
    assert_eq(len(transfers) >= 1, True, f"Found {len(transfers)} transfers")

    res = client.post("/api/transfers", json={
        "player_id": "P105",
        "player_name": "David Alaba",
        "from_team_id": "T2",
        "from_team_name": "Titanium Titans",
        "to_team_id": "T1",
        "to_team_name": "Apex Strikers FC",
        "transfer_fee": 25000000,
        "wage_weekly": 150000,
        "contract_years": 2,
        "date": "2026-08-10"
    })
    assert_eq(res.status_code, 201, "POST /api/transfers status 201")
    new_tr_id = res.json().get("id")

    res = client.put(f"/api/transfers/{new_tr_id}/status", json={"status": "COMPLETED"})
    assert_eq(res.status_code, 200, f"PUT /api/transfers/{new_tr_id}/status status 200")
    assert_eq(res.json().get("status"), "COMPLETED", "Transfer status updated to COMPLETED")

    # 15. Tickets & Seat Reservations
    res = client.get("/api/tickets")
    assert_eq(res.status_code, 200, "GET /api/tickets status 200")

    res = client.post("/api/tickets/book", json={
        "match_id": "M101",
        "category": "VIP",
        "customer_name": "Alex Hunter",
        "customer_email": "alex.hunter@example.com",
        "section": "VIP Club",
        "seat_number": "V-01"
    })
    assert_eq(res.status_code, 201, "POST /api/tickets/book status 201")
    booking_ref = res.json().get("booking_reference")

    res = client.get(f"/api/tickets/{booking_ref}")
    assert_eq(res.status_code, 200, f"GET /api/tickets/{booking_ref} status 200")
    assert_eq(res.json().get("customer_name"), "Alex Hunter", "Ticket customer name matches")

    # 16. Player Scouting & Performance Radar
    res = client.get("/api/scouting")
    assert_eq(res.status_code, 200, "GET /api/scouting status 200")
    scouting_list = res.json()
    assert_eq(len(scouting_list) >= 1, True, f"Found {len(scouting_list)} scouting reports")

    res = client.get("/api/scouting/P101")
    assert_eq(res.status_code, 200, "GET /api/scouting/P101 status 200")
    assert_eq(res.json().get("overall_rating"), 88, "P101 overall rating is 88")

    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print("=" * 50)


if __name__ == "__main__":
    test_suite()
