"""
Main FastAPI Application Entrypoint.
Apex Sports League Management System Backend & REST API.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from .database import init_db, get_db_connection
from .routers import (
    teams,
    players,
    matches,
    standings,
    coaches,
    venues,
    referees,
    tournaments,
    analytics,
    auth,
    transfers,
    tickets,
    scouting
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database tables are created & seeded
    init_db()
    yield
    # Shutdown logic (if any)


app = FastAPI(
    title="Apex Sports League Hub API",
    description="""
## 🏆 Apex League Hub - Comprehensive Sports Management REST API

The official backend API for the Sports League Management System. Provides robust, validated endpoints for:
* **Teams & Franchises**: Complete franchise records, head coaches, records, and roster queries.
* **Player Directory**: Search, team & position filters, statistics tracking (goals, assists, cards).
* **Matches & Fixtures**: Fixture scheduling, real-time live score updates, automated standings computation.
* **League Standings**: Dynamic points table with goal differential and continental/relegation zones.
* **Tournament Brackets**: Visual knockout bracket progression (Quarter-Finals -> Semi-Finals -> Grand Final).
* **Venues & Stadiums**: Stadium capacities, locations, and scheduled match allocations.
* **Officials & Referees**: FIFA & UEFA certified referee records, ratings, and match assignments.
* **Analytics & KPIs**: 7 executive dashboard KPI metrics and Chart.js reporting datasets.
* **Role Authentication**: Multi-role permission management for Admins, Coaches, Referees, Players, and Fans.
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for browser frontend connectivity from any origin or configured domain
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env.strip() == "*":
    origins = ["*"]
    credentials = False
else:
    origins = [orig.strip() for orig in cors_origins_env.split(",") if orig.strip()]
    credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register All API Routers
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(standings.router)
app.include_router(tournaments.router)
app.include_router(coaches.router)
app.include_router(venues.router)
app.include_router(referees.router)
app.include_router(analytics.router)
app.include_router(auth.router)
app.include_router(transfers.router)
app.include_router(tickets.router)
app.include_router(scouting.router)


@app.get("/api/health", tags=["System"])
def health_check():
    """Health check endpoint to test API responsiveness and database connectivity."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as team_count FROM teams")
        count = cursor.fetchone()["team_count"]
        conn.close()
        return {
            "status": "healthy",
            "service": "Apex Sports League Hub API",
            "version": "1.0.0",
            "database": "connected (SQLite)",
            "teams_loaded": count
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/", tags=["System"])
def api_index(request: Request):
    """API Gateway root - overview of all available endpoints and interactive docs."""
    base_url = str(request.base_url).rstrip("/")
    return {
        "title": "Apex Sports League Management System API",
        "version": "1.0.0",
        "docs_url": f"{base_url}/docs",
        "redoc_url": f"{base_url}/redoc",
        "health_check": f"{base_url}/api/health",
        "endpoints": {
            "teams": f"{base_url}/api/teams",
            "players": f"{base_url}/api/players",
            "matches": f"{base_url}/api/matches",
            "standings": f"{base_url}/api/standings",
            "tournaments": f"{base_url}/api/tournaments/bracket",
            "coaches": f"{base_url}/api/coaches",
            "venues": f"{base_url}/api/venues",
            "referees": f"{base_url}/api/referees",
            "transfers": f"{base_url}/api/transfers",
            "tickets": f"{base_url}/api/tickets",
            "scouting": f"{base_url}/api/scouting",
            "analytics_kpis": f"{base_url}/api/analytics/kpis",
            "auth_roles": f"{base_url}/api/auth/roles"
        },
        "frontend_app": f"{base_url}/app/"
    }


# Mount the frontend directory so the backend can also serve the web UI directly
FRONTEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists(os.path.join(FRONTEND_DIR, "index.html")):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
