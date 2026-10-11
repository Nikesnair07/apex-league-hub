# 🏆 Apex Sports League Hub - Backend & REST API

Production-ready, high-performance RESTful API for the **Sports League Management System**, built with **FastAPI**, **Pydantic**, and **SQLite**.

---

## 🌟 Overview & Key Features

This backend transitions the sports league platform from a static mock frontend into a full-fledged, persistent SaaS architecture:

- **⚡ FastAPI Architecture**: High-speed asynchronous Python ASGI backend with automated request validation, serialization, and CORS.
- **📖 Auto-Generated Interactive API Documentation**:
  - **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
  - **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
  - **OpenAPI Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
- **🗄️ Zero-Config Persistence**: Built-in SQLite database (`sports_league.db`) that auto-initializes tables and seeds initial league data on first startup.
- **🔄 Two-Way Live Frontend Sync**: The web app (`index.html`) automatically detects if the backend is running, displaying an **API Connected 🟢** badge, updating records in real-time, with seamless fallback to offline mock mode if disconnected.
- **📊 Dynamic Analytics & Standings**: Automatic computation of points, goal differential, UEFA/Champions League qualification zones, and executive KPI cards.

---

## 📂 Project Structure

```text
sports-league-management-system/
├── backend/
│   ├── main.py              # FastAPI app initialization, middleware, mounts, and root gateway
│   ├── database.py          # SQLite schema creation & seed data initializer
│   ├── models.py            # Pydantic validation schemas & response models
│   ├── run.py               # One-click Uvicorn server launcher
│   ├── test_api.py          # Automated endpoint test suite
│   ├── requirements.txt     # Python dependency list
│   └── routers/
│       ├── teams.py         # /api/teams (CRUD, roster, standings stats)
│       ├── players.py       # /api/players (CRUD, team/position filters, search)
│       ├── matches.py       # /api/matches (CRUD, status filter, live score submission)
│       ├── standings.py     # /api/standings (Dynamic points table & qualification zones)
│       ├── tournaments.py   # /api/tournaments (Knockout brackets & group stage)
│       ├── coaches.py       # /api/coaches (Coach profiles and credentials)
│       ├── venues.py        # /api/venues (Stadium directories and capacities)
│       ├── referees.py      # /api/referees (Officials roster, FIFA ratings)
│       ├── analytics.py     # /api/analytics (7 KPI stats, goals & win-rate charts)
│       └── auth.py          # /api/auth (Login, session token, roles & permissions)
├── index.html               # Main Web App UI (connected to backend API)
├── script.js                # Frontend controller with auto-sync to backend
├── style.css                # Glassmorphism dark mode design system
└── data.js                  # Initial fallback data store
```

---

## 🚀 How to Run the Backend

### 1. Requirements
Ensure Python 3.9+ is installed:
```powershell
python --version
```

### 2. Install Dependencies
```powershell
pip install -r backend/requirements.txt
```
*(Packages: `fastapi`, `uvicorn`, `pydantic`)*

### 3. Start the Server
Run the convenience runner:
```powershell
python backend/run.py
```
Or run directly via Uvicorn:
```powershell
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Access URLs
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **API Root Gateway**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Full Web Application**: [http://127.0.0.1:8000/app/](http://127.0.0.1:8000/app/) (or double-click `index.html`)

---

## 📡 Complete REST API Endpoint Reference

### 1. Teams API (`/api/teams`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/teams` | List all teams (Query params: `sort_by=points\|wins\|name\|goals_for`, `order=desc\|asc`) |
| `GET` | `/api/teams/{id}` | Get single team details by ID |
| `GET` | `/api/teams/{id}/roster` | Get all players roster belonging to team `{id}` |
| `POST` | `/api/teams` | Create a new franchised team |
| `PUT` | `/api/teams/{id}` | Update team information, coach, or win/loss records |
| `DELETE` | `/api/teams/{id}` | Delete a team |

#### Example: Create Team (`POST /api/teams`)
```json
{
  "name": "Valkyrie United",
  "coach": "Marco Rossi",
  "city": "Seattle",
  "founded": 2026
}
```

---

### 2. Players API (`/api/players`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/players` | Query directory (Params: `team_id`, `position`, `search`, `sort_by`, `order`, `limit`, `offset`) |
| `GET` | `/api/players/{id}` | Get single player profile |
| `POST` | `/api/players` | Register a new player to a team |
| `PUT` | `/api/players/{id}` | Update player profile, jersey number, goals, assists, or cards |
| `DELETE` | `/api/players/{id}` | Remove a player record |

#### Example: Register Player (`POST /api/players`)
```json
{
  "name": "Liam Vance",
  "position": "Forward",
  "team_id": "T1",
  "jersey_number": 9,
  "age": 23
}
```

---

### 3. Matches & Fixtures API (`/api/matches`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/matches` | List matches (Param: `match_status=ALL\|LIVE\|UPCOMING\|COMPLETED`) |
| `GET` | `/api/matches/{id}` | Get fixture details by ID |
| `POST` | `/api/matches` | Schedule a new match between two teams |
| `PUT` | `/api/matches/{id}/score` | Update live/final score & status (auto-updates team standings) |
| `DELETE` | `/api/matches/{id}` | Delete a fixture |

#### Example: Update Score (`PUT /api/matches/{id}/score`)
```json
{
  "home_score": 3,
  "away_score": 1,
  "status": "COMPLETED"
}
```

---

### 4. Standings API (`/api/standings`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/standings` | Returns dynamically calculated points table with goal difference and qualification zones |

**Response Sample:**
```json
[
  {
    "rank": 1,
    "team_id": "T1",
    "team_name": "Apex Strikers FC",
    "played": 19,
    "wins": 14,
    "draws": 3,
    "losses": 2,
    "goals_for": 42,
    "goals_against": 16,
    "goal_difference": 26,
    "points": 45,
    "zone": "zone-champions"
  }
]
```

---

### 5. Tournament & Brackets API (`/api/tournaments`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tournaments/bracket` | Retrieve knockout bracket tree (Quarter-Finals, Semi-Finals, Grand Final) |
| `PUT` | `/api/tournaments/bracket` | Update bracket scores and advancing winners |
| `GET` | `/api/tournaments/group-stage` | Retrieve group stage standings |

---

### 6. Coaches, Venues & Referees APIs

- **Coaches** (`/api/coaches`):
  - `GET /api/coaches` - List all head coaches
  - `GET /api/coaches/{id}` - Get coach by ID
  - `POST /api/coaches` - Add coach profile
  - `DELETE /api/coaches/{id}` - Delete coach
- **Venues** (`/api/venues`):
  - `GET /api/venues` - List stadiums with seat capacity & upcoming fixtures count
  - `GET /api/venues/{id}` - Get venue details
  - `POST /api/venues` - Add stadium
  - `DELETE /api/venues/{id}` - Delete venue
- **Referees** (`/api/referees`):
  - `GET /api/referees` - List certified match officials with star rating
  - `GET /api/referees/{id}` - Get referee details
  - `POST /api/referees` - Add referee
  - `DELETE /api/referees/{id}` - Delete referee

---

### 7. Analytics & Executive KPIs (`/api/analytics`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/analytics/kpis` | 7 aggregate executive KPIs for top dashboard cards |
| `GET` | `/api/analytics/team-performance` | Goals scored vs conceded for top teams (Chart.js dataset) |
| `GET` | `/api/analytics/tournament-progress` | Doughnut chart: Completed vs Remaining vs Live games |
| `GET` | `/api/analytics/points-trend` | Weekly points progression trend dataset |

---

### 8. Authentication & Roles (`/api/auth`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticate role session, returns token & permissions profile |
| `GET` | `/api/auth/roles` | List all 5 roles (`Administrator`, `Coach`, `Referee`, `Player`, `Fan`) and permission matrices |

---

### 9. Match Events & Live Commentary (`/api/matches/{id}/events`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/matches/{id}/events` | Chronological live event feed (Goals, Yellow/Red cards, Substitutions, VAR) |
| `POST` | `/api/matches/{id}/events` | Log live match event (auto-updates player goals/cards and match score) |

#### Example: Log Event (`POST /api/matches/M101/events`)
```json
{
  "minute": 54,
  "event_type": "GOAL",
  "team_id": "T1",
  "player_id": "P101",
  "player_name": "Lucas Sterling",
  "assist_player_name": "Mateo Kovac",
  "detail": "Bottom corner strike from inside the box"
}
```

---

### 10. Transfers & Contract Market (`/api/transfers`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/transfers` | List market deals (filter: `status=ALL|PENDING|ACCEPTED|COMPLETED|REJECTED`) |
| `GET` | `/api/transfers/{id}` | Get transfer bid details |
| `POST` | `/api/transfers` | Submit transfer bid and wage contract offer |
| `PUT` | `/api/transfers/{id}/status` | Accept/Reject/Complete deal (auto-moves player to new club on COMPLETED) |
| `DELETE` | `/api/transfers/{id}` | Withdraw proposal |

---

### 11. Match Ticketing & Reservations (`/api/tickets`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tickets` | Query bookings (optional filter: `match_id`) |
| `GET` | `/api/tickets/{booking_reference}` | Retrieve booking confirmation details |
| `POST` | `/api/tickets/book` | Reserve match tickets across VIP, Category 1/2, General tiers |
| `DELETE` | `/api/tickets/{booking_reference}` | Cancel ticket booking |

---

### 12. Player Scouting & Technical Radar (`/api/scouting`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/scouting` | List player radar metrics (sort by `overall_rating`, `potential`, `market_value_eur`, `pace`) |
| `GET` | `/api/scouting/{player_id}` | Retrieve comprehensive scouting attributes (Pace, Shooting, Passing, Dribbling, Defending, Physical) |
| `POST` | `/api/scouting` | Create or update professional technical scouting profile |

---

## 🧪 Testing the API

Run the automated test suite:
```powershell
python backend/test_api.py
```
This runs 35+ integration checks covering status codes, validation, relations, and computations.
