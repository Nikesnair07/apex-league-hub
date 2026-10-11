# 🏆 Sports League Management System (Apex League Hub)

A comprehensive, full-stack Sports League Management SaaS application featuring a modern glassmorphism web dashboard and its own dedicated **FastAPI RESTful Backend**.

---

## ⚡ Quick Start

### 1. Run the Backend API
```powershell
python backend/run.py
```
- **API Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 2. Run the Frontend App
- Open `index.html` in any web browser, OR visit [http://127.0.0.1:8000/app/](http://127.0.0.1:8000/app/) when the backend is running.
- The web app automatically detects the backend and shows **API Connected 🟢**. If running offline, it gracefully falls back to local data store.

---

## 🏗️ Architecture

```text
sports-league-management-system/
├── backend/                  # Dedicated RESTful API (FastAPI + SQLite + Pydantic)
│   ├── main.py              # Application entrypoint & CORS middleware
│   ├── database.py          # SQLite persistence & automated data seeding
│   ├── models.py            # Pydantic validation schemas
│   ├── run.py               # Server launcher
│   ├── test_api.py          # Automated test suite
│   ├── requirements.txt     # Python dependencies
│   ├── README.md            # Detailed API documentation
│   └── routers/             # Modular REST endpoint controllers
│       ├── teams.py         # /api/teams
│       ├── players.py       # /api/players
│       ├── matches.py       # /api/matches
│       ├── standings.py     # /api/standings
│       ├── tournaments.py   # /api/tournaments
│       ├── coaches.py       # /api/coaches
│       ├── venues.py        # /api/venues
│       ├── referees.py      # /api/referees
│       ├── analytics.py     # /api/analytics
│       └── auth.py          # /api/auth
├── index.html               # SaaS executive web interface
├── script.js                # Frontend controller & backend sync
├── style.css                # Dark mode glassmorphism design system
└── data.js                  # Standalone fallback mock store
```

---

## 📖 Backend Documentation
For the full endpoint reference, parameters, and example payloads, see [`backend/README.md`](backend/README.md).