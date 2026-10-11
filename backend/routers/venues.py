"""
Venues Router - Stadiums, arenas, and pitch management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from ..database import get_db_connection
from ..models import VenueResponse, VenueCreate

router = APIRouter(prefix="/api/venues", tags=["Venues"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[VenueResponse], summary="List all stadiums and venues")
def get_venues():
    """Retrieve all venues with seat capacities and scheduled fixtures."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM venues ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{venue_id}", response_model=VenueResponse, summary="Get venue details by ID")
def get_venue(venue_id: str):
    """Retrieve details for a single venue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM venues WHERE id = ?", (venue_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Venue with ID '{venue_id}' not found")
    return row_to_dict(row)


@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED, summary="Add a stadium/venue")
def create_venue(venue_in: VenueCreate):
    """Add a new stadium venue to the league directory."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM venues")
    count = cursor.fetchone()["count"]
    new_id = f"V{count + 1}"

    image = venue_in.image or "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?auto=format&fit=crop&w=600&q=80"

    cursor.execute("""
        INSERT INTO venues (id, name, image, capacity, address, upcoming_matches_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        new_id, venue_in.name, image, venue_in.capacity,
        venue_in.address, venue_in.upcoming_matches_count
    ))

    conn.commit()
    cursor.execute("SELECT * FROM venues WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)


@router.delete("/{venue_id}", status_code=status.HTTP_200_OK, summary="Delete stadium venue")
def delete_venue(venue_id: str):
    """Remove a venue from the directory."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM venues WHERE id = ?", (venue_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Venue with ID '{venue_id}' not found")

    cursor.execute("DELETE FROM venues WHERE id = ?", (venue_id,))
    conn.commit()
    conn.close()
    return {"message": f"Venue '{venue_id}' deleted successfully", "id": venue_id}
