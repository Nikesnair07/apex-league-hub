"""
Database layer for Sports League Management System.
Uses SQLite for zero-setup, self-contained persistence.
Initializes tables and seeds initial mock data matching data.js.
"""

import sqlite3
import json
import os
from typing import Dict, Any, List, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "sports_league.db")


def get_db_connection():
    """Create and return a database connection with dict-like row access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create database tables and seed with initial data if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Teams Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            logo TEXT,
            coach TEXT NOT NULL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            city TEXT,
            founded INTEGER
        );
    """)

    # 2. Players Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            position TEXT NOT NULL,
            team_id TEXT,
            team_name TEXT,
            jersey_number INTEGER NOT NULL,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            photo TEXT,
            FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE SET NULL
        );
    """)

    # 3. Coaches Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coaches (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            team_name TEXT,
            experience TEXT,
            nationality TEXT,
            contact TEXT,
            photo TEXT
        );
    """)

    # 4. Matches Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id TEXT PRIMARY KEY,
            home_team_id TEXT,
            home_team_name TEXT NOT NULL,
            home_logo TEXT,
            away_team_id TEXT,
            away_team_name TEXT NOT NULL,
            away_logo TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            venue TEXT NOT NULL,
            referee TEXT,
            status TEXT NOT NULL DEFAULT 'UPCOMING',
            home_score INTEGER DEFAULT 0,
            away_score INTEGER DEFAULT 0,
            FOREIGN KEY (home_team_id) REFERENCES teams (id) ON DELETE SET NULL,
            FOREIGN KEY (away_team_id) REFERENCES teams (id) ON DELETE SET NULL
        );
    """)

    # 5. Venues Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            image TEXT,
            capacity TEXT NOT NULL,
            address TEXT NOT NULL,
            upcoming_matches_count INTEGER DEFAULT 0
        );
    """)

    # 6. Referees Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referees (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            experience TEXT NOT NULL,
            assigned_matches INTEGER DEFAULT 0,
            rating REAL DEFAULT 5.0,
            photo TEXT
        );
    """)

    # 7. Tournaments / Bracket Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            bracket_data TEXT NOT NULL,
            group_stage_data TEXT
        );
    """)

    # 8. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT
        );
    """)

    # 9. Match Events / Live Commentary Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_events (
            id TEXT PRIMARY KEY,
            match_id TEXT NOT NULL,
            minute INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            team_id TEXT,
            player_id TEXT,
            player_name TEXT NOT NULL,
            assist_player_name TEXT,
            detail TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE
        );
    """)

    # 10. Transfers & Contracts Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
            id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            from_team_id TEXT NOT NULL,
            from_team_name TEXT NOT NULL,
            to_team_id TEXT NOT NULL,
            to_team_name TEXT NOT NULL,
            transfer_fee REAL DEFAULT 0,
            wage_weekly REAL DEFAULT 0,
            contract_years INTEGER DEFAULT 3,
            status TEXT NOT NULL DEFAULT 'PENDING',
            date TEXT NOT NULL
        );
    """)

    # 11. Match Ticketing & Seats Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            match_id TEXT NOT NULL,
            venue_name TEXT NOT NULL,
            section TEXT NOT NULL,
            seat_number TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'GENERAL',
            price REAL NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            booking_reference TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'CONFIRMED',
            FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE
        );
    """)

    # 12. Player Scouting & Performance Radar Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_scouting (
            id TEXT PRIMARY KEY,
            player_id TEXT UNIQUE NOT NULL,
            player_name TEXT NOT NULL,
            overall_rating INTEGER NOT NULL,
            potential INTEGER NOT NULL,
            pace INTEGER NOT NULL,
            shooting INTEGER NOT NULL,
            passing INTEGER NOT NULL,
            dribbling INTEGER NOT NULL,
            defending INTEGER NOT NULL,
            physical INTEGER NOT NULL,
            market_value_eur REAL NOT NULL,
            preferred_foot TEXT DEFAULT 'Right',
            scout_notes TEXT,
            FOREIGN KEY (player_id) REFERENCES players (id) ON DELETE CASCADE
        );
    """)

    conn.commit()

    # Check if seed data is needed
    cursor.execute("SELECT COUNT(*) as count FROM teams")
    count = cursor.fetchone()["count"]

    if count == 0:
        seed_initial_data(conn)

    conn.close()


def seed_initial_data(conn):
    """Seed the database with rich initial data from ApexData store."""
    cursor = conn.cursor()

    # Initial Teams
    teams = [
        ("T1", "Apex Strikers FC", "https://api.dicebear.com/7.x/identicon/svg?seed=ApexStrikers", "Julian Alvarez", 14, 2, 3, 42, 16, 45, "New York", 2012),
        ("T2", "Titanium Titans", "https://api.dicebear.com/7.x/identicon/svg?seed=TitaniumTitans", "Marcus Vance", 13, 3, 3, 38, 18, 42, "Chicago", 2010),
        ("T3", "Vanguard Warriors", "https://api.dicebear.com/7.x/identicon/svg?seed=VanguardWarriors", "Elena Rostova", 11, 4, 4, 34, 20, 37, "Los Angeles", 2015),
        ("T4", "Solaris Dragons", "https://api.dicebear.com/7.x/identicon/svg?seed=SolarisDragons", "Diego Mendoza", 10, 5, 4, 31, 22, 34, "Miami", 2014),
        ("T5", "Cyber Pulse FC", "https://api.dicebear.com/7.x/identicon/svg?seed=CyberPulse", "Liam O'Connor", 9, 7, 3, 29, 27, 30, "Seattle", 2018),
        ("T6", "Phoenix Rising", "https://api.dicebear.com/7.x/identicon/svg?seed=PhoenixRising", "Sophia Chen", 8, 8, 3, 27, 30, 27, "Phoenix", 2017),
        ("T7", "Thunderbolt SC", "https://api.dicebear.com/7.x/identicon/svg?seed=ThunderboltSC", "Gabriel Silva", 7, 9, 3, 24, 32, 24, "Dallas", 2016),
        ("T8", "Neon Shadows", "https://api.dicebear.com/7.x/identicon/svg?seed=NeonShadows", "Kaito Tanaka", 5, 11, 3, 20, 36, 18, "San Francisco", 2019)
    ]
    cursor.executemany("""
        INSERT INTO teams (id, name, logo, coach, wins, losses, draws, goals_for, goals_against, points, city, founded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, teams)

    # Initial Players
    players = [
        ("P101", "Lucas Sterling", 26, "Forward", "T1", "Apex Strikers FC", 9, 18, 7, 2, 0, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80"),
        ("P102", "Mateo Kovac", 24, "Midfielder", "T1", "Apex Strikers FC", 10, 9, 14, 3, 0, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"),
        ("P103", "Viktor Petrov", 29, "Defender", "T1", "Apex Strikers FC", 4, 3, 2, 5, 1, "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=150&q=80"),
        ("P104", "Gabriel Jesus", 27, "Forward", "T2", "Titanium Titans", 11, 15, 5, 1, 0, "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=150&q=80"),
        ("P105", "David Alaba", 31, "Defender", "T2", "Titanium Titans", 3, 2, 6, 4, 0, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80"),
        ("P106", "Antoine Griezmann", 28, "Midfielder", "T3", "Vanguard Warriors", 7, 12, 11, 2, 0, "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=150&q=80"),
        ("P107", "Manuel Neuer", 33, "Goalkeeper", "T1", "Apex Strikers FC", 1, 0, 1, 1, 0, "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=150&q=80"),
        ("P108", "Rodri Hernandez", 25, "Midfielder", "T4", "Solaris Dragons", 16, 8, 9, 6, 0, "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80"),
        ("P109", "Achraf Hakimi", 23, "Defender", "T5", "Cyber Pulse FC", 2, 4, 8, 3, 0, "https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?auto=format&fit=crop&w=150&q=80"),
        ("P110", "Son Heung-min", 30, "Forward", "T6", "Phoenix Rising", 7, 14, 6, 1, 0, "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80")
    ]
    cursor.executemany("""
        INSERT INTO players (id, name, age, position, team_id, team_name, jersey_number, goals, assists, yellow_cards, red_cards, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, players)

    # Initial Coaches
    coaches = [
        ("C1", "Julian Alvarez", "Apex Strikers FC", "12 Years", "Argentina", "julian@apexstrikers.com", "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=150&q=80"),
        ("C2", "Marcus Vance", "Titanium Titans", "15 Years", "United States", "vance@titansfc.com", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&q=80"),
        ("C3", "Elena Rostova", "Vanguard Warriors", "9 Years", "Spain", "elena@vanguardw.com", "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=150&q=80"),
        ("C4", "Diego Mendoza", "Solaris Dragons", "11 Years", "Brazil", "diego@solaris.com", "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80")
    ]
    cursor.executemany("""
        INSERT INTO coaches (id, name, team_name, experience, nationality, contact, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, coaches)

    # Initial Matches
    matches = [
        ("M101", "T1", "Apex Strikers FC", "https://api.dicebear.com/7.x/identicon/svg?seed=ApexStrikers",
         "T2", "Titanium Titans", "https://api.dicebear.com/7.x/identicon/svg?seed=TitaniumTitans",
         "2026-08-01", "20:00 EST", "Metropolitan Grand Arena", "Michael Oliver", "LIVE", 2, 1),
        ("M102", "T3", "Vanguard Warriors", "https://api.dicebear.com/7.x/identicon/svg?seed=VanguardWarriors",
         "T4", "Solaris Dragons", "https://api.dicebear.com/7.x/identicon/svg?seed=SolarisDragons",
         "2026-08-03", "18:30 EST", "Pacific Olympic Stadium", "Szymon Marciniak", "UPCOMING", 0, 0),
        ("M103", "T5", "Cyber Pulse FC", "https://api.dicebear.com/7.x/identicon/svg?seed=CyberPulse",
         "T6", "Phoenix Rising", "https://api.dicebear.com/7.x/identicon/svg?seed=PhoenixRising",
         "2026-07-29", "19:00 EST", "Emerald Tech Arena", "Anthony Taylor", "COMPLETED", 3, 1),
        ("M104", "T7", "Thunderbolt SC", "https://api.dicebear.com/7.x/identicon/svg?seed=ThunderboltSC",
         "T8", "Neon Shadows", "https://api.dicebear.com/7.x/identicon/svg?seed=NeonShadows",
         "2026-07-28", "21:00 EST", "Lone Star Coliseum", "Clement Turpin", "COMPLETED", 2, 0)
    ]
    cursor.executemany("""
        INSERT INTO matches (id, home_team_id, home_team_name, home_logo, away_team_id, away_team_name, away_logo,
                             date, time, venue, referee, status, home_score, away_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, matches)

    # Initial Venues
    venues = [
        ("V1", "Metropolitan Grand Arena", "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=600&q=80", "65,000 Seats", "100 Championship Blvd, New York, NY", 4),
        ("V2", "Pacific Olympic Stadium", "https://images.unsplash.com/photo-1522778119026-d647f0596c20?auto=format&fit=crop&w=600&q=80", "54,200 Seats", "777 Victory Drive, Los Angeles, CA", 3),
        ("V3", "Emerald Tech Arena", "https://images.unsplash.com/photo-1487466365202-1afab86c743e?auto=format&fit=crop&w=600&q=80", "42,000 Seats", "500 Innovation Way, Seattle, WA", 2)
    ]
    cursor.executemany("""
        INSERT INTO venues (id, name, image, capacity, address, upcoming_matches_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, venues)

    # Initial Referees
    referees = [
        ("R1", "Michael Oliver", "14 Years FIFA Certified", 18, 4.9, "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80"),
        ("R2", "Szymon Marciniak", "16 Years World Cup Ref", 22, 4.95, "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=150&q=80"),
        ("R3", "Anthony Taylor", "11 Years Premier Panel", 15, 4.8, "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=150&q=80"),
        ("R4", "Clement Turpin", "13 Years UEFA Elite", 16, 4.85, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80")
    ]
    cursor.executemany("""
        INSERT INTO referees (id, name, experience, assigned_matches, rating, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, referees)

    # Initial Tournament Bracket Data
    bracket_data = {
        "quarterFinals": [
            {"match": "QF1", "team1": "Apex Strikers", "score1": 3, "team2": "Neon Shadows", "score2": 0, "winner": "Apex Strikers"},
            {"match": "QF2", "team1": "Titanium Titans", "score1": 2, "team2": "Thunderbolt SC", "score2": 1, "winner": "Titanium Titans"},
            {"match": "QF3", "team1": "Vanguard Warriors", "score1": 4, "team2": "Phoenix Rising", "score2": 2, "winner": "Vanguard Warriors"},
            {"match": "QF4", "team1": "Solaris Dragons", "score1": 1, "team2": "Cyber Pulse FC", "score2": 0, "winner": "Solaris Dragons"}
        ],
        "semiFinals": [
            {"match": "SF1", "team1": "Apex Strikers", "score1": 2, "team2": "Titanium Titans", "score2": 1, "winner": "Apex Strikers"},
            {"match": "SF2", "team1": "Vanguard Warriors", "score1": 1, "team2": "Solaris Dragons", "score2": 0, "winner": "Vanguard Warriors"}
        ],
        "final": [
            {"match": "FINAL", "team1": "Apex Strikers", "score1": "-", "team2": "Vanguard Warriors", "score2": "-", "winner": "TBD"}
        ]
    }
    cursor.execute("""
        INSERT INTO tournaments (id, name, bracket_data)
        VALUES (?, ?, ?)
    """, ("T-CHAMP-2026", "Apex Champions Trophy 2026", json.dumps(bracket_data)))

    # Initial Users / Roles
    users = [
        ("U1", "admin", "admin123", "Alex Morgan", "Administrator", "admin@apexleague.com"),
        ("U2", "coach", "coach123", "Julian Alvarez", "Coach", "coach@apexleague.com"),
        ("U3", "referee", "ref123", "Michael Oliver", "Referee", "referee@apexleague.com"),
        ("U4", "player", "player123", "Lucas Sterling", "Player", "player@apexleague.com"),
        ("U5", "fan", "fan123", "Jordan Fan", "Fan", "fan@apexleague.com")
    ]
    cursor.executemany("""
        INSERT INTO users (id, username, password, name, role, email)
        VALUES (?, ?, ?, ?, ?, ?)
    """, users)

    # Initial Match Events / Commentary for Match M101
    events = [
        ("E1", "M101", 12, "GOAL", "T1", "P101", "Lucas Sterling", "Mateo Kovac", "Curling shot into top-right corner"),
        ("E2", "M101", 34, "YELLOW_CARD", "T2", "P105", "David Alaba", None, "Tactical foul breaking counter attack"),
        ("E3", "M101", 45, "GOAL", "T2", "P104", "Gabriel Jesus", None, "Clinical header from set-piece corner"),
        ("E4", "M101", 68, "GOAL", "T1", "P102", "Mateo Kovac", "Lucas Sterling", "Left-footed volley from edge of the box")
    ]
    cursor.executemany("""
        INSERT INTO match_events (id, match_id, minute, event_type, team_id, player_id, player_name, assist_player_name, detail)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, events)

    # Initial Transfers
    transfers = [
        ("TR1", "P110", "Son Heung-min", "T6", "Phoenix Rising", "T1", "Apex Strikers FC", 45000000, 180000, 3, "COMPLETED", "2026-07-15"),
        ("TR2", "P108", "Rodri Hernandez", "T4", "Solaris Dragons", "T2", "Titanium Titans", 60000000, 220000, 4, "PENDING", "2026-08-02"),
        ("TR3", "P106", "Antoine Griezmann", "T3", "Vanguard Warriors", "T5", "Cyber Pulse FC", 30000000, 140000, 2, "ACCEPTED", "2026-08-05")
    ]
    cursor.executemany("""
        INSERT INTO transfers (id, player_id, player_name, from_team_id, from_team_name, to_team_id, to_team_name, transfer_fee, wage_weekly, contract_years, status, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, transfers)

    # Initial Tickets
    tickets = [
        ("TK1", "M101", "Metropolitan Grand Arena", "Section 104", "A-12", "VIP", 250.0, "Samantha Wright", "samantha@example.com", "APX-TK-9021", "CONFIRMED"),
        ("TK2", "M101", "Metropolitan Grand Arena", "Section 208", "F-4", "CATEGORY_1", 120.0, "David Miller", "david@example.com", "APX-TK-9022", "CONFIRMED"),
        ("TK3", "M102", "Pacific Olympic Stadium", "Section 112", "C-15", "GENERAL", 65.0, "Elena Gomez", "elena@example.com", "APX-TK-9023", "CONFIRMED")
    ]
    cursor.executemany("""
        INSERT INTO tickets (id, match_id, venue_name, section, seat_number, category, price, customer_name, customer_email, booking_reference, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tickets)

    # Initial Scouting Data
    scouting = [
        ("SC1", "P101", "Lucas Sterling", 88, 92, 89, 87, 82, 86, 45, 80, 75000000, "Right", "Elite finisher with exceptional burst acceleration and high tactical intelligence."),
        ("SC2", "P102", "Mateo Kovac", 86, 89, 78, 80, 91, 88, 68, 75, 55000000, "Both", "Visionary playmaker with premier distribution and passing accuracy under heavy press."),
        ("SC3", "P103", "Viktor Petrov", 84, 86, 75, 50, 72, 70, 88, 89, 38000000, "Right", "Commanding aerial presence and decisive sliding tackle technique in low blocks."),
        ("SC4", "P104", "Gabriel Jesus", 87, 90, 86, 85, 80, 87, 52, 78, 68000000, "Right", "Explosive dribbler, highly efficient in one-on-one situations inside the penalty box.")
    ]
    cursor.executemany("""
        INSERT INTO player_scouting (id, player_id, player_name, overall_rating, potential, pace, shooting, passing, dribbling, defending, physical, market_value_eur, preferred_foot, scout_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, scouting)

    conn.commit()
