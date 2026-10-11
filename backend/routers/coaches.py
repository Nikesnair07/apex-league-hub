"""
Coaches Router - Manage head coaches across all league teams.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from ..database import get_db_connection
from ..models import CoachResponse, CoachCreate

router = APIRouter(prefix="/api/coaches", tags=["Coaches"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[CoachResponse], summary="List all coaches")
def get_coaches():
    """Retrieve full directory of head coaches."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coaches ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{coach_id}", response_model=CoachResponse, summary="Get coach by ID")
def get_coach(coach_id: str):
    """Retrieve details for a single coach."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coaches WHERE id = ?", (coach_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Coach with ID '{coach_id}' not found")
    return row_to_dict(row)


@router.post("", response_model=CoachResponse, status_code=status.HTTP_201_CREATED, summary="Add a coach profile")
def create_coach(coach_in: CoachCreate):
    """Register a new coach."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM coaches")
    count = cursor.fetchone()["count"]
    new_id = f"C{count + 1}"

    photo = coach_in.photo or "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=150&q=80"

    cursor.execute("""
        INSERT INTO coaches (id, name, team_name, experience, nationality, contact, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        new_id, coach_in.name, coach_in.team_name, coach_in.experience,
        coach_in.nationality, coach_in.contact, photo
    ))

    conn.commit()
    cursor.execute("SELECT * FROM coaches WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)


@router.delete("/{coach_id}", status_code=status.HTTP_200_OK, summary="Delete coach profile")
def delete_coach(coach_id: str):
    """Remove a coach record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM coaches WHERE id = ?", (coach_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Coach with ID '{coach_id}' not found")

    cursor.execute("DELETE FROM coaches WHERE id = ?", (coach_id,))
    conn.commit()
    conn.close()
    return {"message": f"Coach '{coach_id}' deleted successfully", "id": coach_id}
