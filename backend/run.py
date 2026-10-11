"""
Convenience server starter for Apex Sports League Management Backend.
Runs Uvicorn on 127.0.0.1:8000 with auto-reload.
"""

import sys
import os

# Ensure backend package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("🏆 STARTING APEX SPORTS LEAGUE HUB BACKEND API SERVER")
    print("=" * 70)
    print("📍 Local API URL:     http://127.0.0.1:8000")
    print("📖 Swagger UI Docs:   http://127.0.0.1:8000/docs")
    print("📑 ReDoc Specs:       http://127.0.0.1:8000/redoc")
    print("🌐 Full Web App:      http://127.0.0.1:8000/app/")
    print("=" * 70)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
