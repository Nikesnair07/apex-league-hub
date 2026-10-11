"""
Referees Router - Officials directory, match assignments, and ratings.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from ..database import get_db_connection
from ..models import RefereeResponse, RefereeCreate

router = APIRouter(prefix="/api/referees", tags=["Referees"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[RefereeResponse], summary="List all referees")
def get_referees():
    """Retrieve full roster of certified match officials."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM referees ORDER BY rating DESC")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{referee_id}", response_model=RefereeResponse, summary="Get referee by ID")
def get_referee(referee_id: str):
    """Retrieve referee profile by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM referees WHERE id = ?", (referee_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Referee with ID '{referee_id}' not found")
    return row_to_dict(row)


@router.post("", response_model=RefereeResponse, status_code=status.HTTP_201_CREATED, summary="Add match referee")
def create_referee(referee_in: RefereeCreate):
    """Register a new certified official."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM referees")
    count = cursor.fetchone()["count"]
    new_id = f"R{count + 1}"

    photo = referee_in.photo or "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80"

    cursor.execute("""
        INSERT INTO referees (id, name, experience, assigned_matches, rating, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        new_id, referee_in.name, referee_in.experience,
        referee_in.assigned_matches, referee_in.rating, photo
    ))

    conn.commit()
    cursor.execute("SELECT * FROM referees WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)


@router.delete("/{referee_id}", status_code=status.HTTP_200_OK, summary="Delete referee")
def delete_referee(referee_id: str):
    """Remove a referee record."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM referees WHERE id = ?", (referee_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Referee with ID '{referee_id}' not found")

    cursor.execute("DELETE FROM referees WHERE id = ?", (referee_id,))
    conn.commit()
    conn.close()
    return {"message": f"Referee '{referee_id}' deleted successfully", "id": referee_id}
