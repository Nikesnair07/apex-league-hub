"""
Tickets Router - Match ticketing, seat reservations, and spectator booking.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
import random
from ..database import get_db_connection
from ..models import TicketResponse, TicketCreate

router = APIRouter(prefix="/api/tickets", tags=["Match Ticketing"])


def row_to_dict(row):
    return dict(row) if row else None


CATEGORY_PRICES = {
    "VIP": 250.0,
    "CATEGORY_1": 120.0,
    "CATEGORY_2": 80.0,
    "GENERAL": 50.0
}


@router.get("", response_model=List[TicketResponse], summary="List booked tickets")
def get_tickets(
    match_id: Optional[str] = Query(None, description="Filter by match ID (e.g. M101)")
):
    """Retrieve ticket bookings for league fixtures."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if match_id:
        cursor.execute("SELECT * FROM tickets WHERE match_id = ? ORDER BY id DESC", (match_id,))
    else:
        cursor.execute("SELECT * FROM tickets ORDER BY id DESC")

    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{booking_reference}", response_model=TicketResponse, summary="Look up ticket by booking reference")
def get_ticket(booking_reference: str):
    """Retrieve ticket confirmation by its booking reference code (e.g. APX-TK-9021)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE booking_reference = ?", (booking_reference,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Booking reference '{booking_reference}' not found")
    return row_to_dict(row)


@router.post("/book", response_model=TicketResponse, status_code=status.HTTP_201_CREATED, summary="Reserve / book match tickets")
def book_ticket(ticket_in: TicketCreate):
    """Purchase and reserve a match ticket with seat selection and automated reference."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify match exists
    cursor.execute("SELECT * FROM matches WHERE id = ?", (ticket_in.match_id,))
    match = cursor.fetchone()
    if not match:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Match with ID '{ticket_in.match_id}' not found")

    cursor.execute("SELECT COUNT(*) as count FROM tickets")
    count = cursor.fetchone()["count"]
    new_id = f"TK{count + 1}"

    cat = ticket_in.category.upper()
    price = CATEGORY_PRICES.get(cat, 50.0)
    ref = f"APX-TK-{random.randint(1000, 9999)}"

    cursor.execute("""
        INSERT INTO tickets (
            id, match_id, venue_name, section, seat_number, category, price, customer_name, customer_email, booking_reference, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED')
    """, (
        new_id, ticket_in.match_id, match["venue"],
        ticket_in.section or "Section 101", ticket_in.seat_number or "A-1",
        cat, price, ticket_in.customer_name, ticket_in.customer_email, ref
    ))

    conn.commit()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)


@router.delete("/{booking_reference}", status_code=status.HTTP_200_OK, summary="Cancel ticket booking")
def cancel_ticket(booking_reference: str):
    """Cancel a ticket reservation."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tickets WHERE booking_reference = ?", (booking_reference,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Booking '{booking_reference}' not found")

    cursor.execute("DELETE FROM tickets WHERE booking_reference = ?", (booking_reference,))
    conn.commit()
    conn.close()
    return {"message": f"Booking '{booking_reference}' successfully cancelled"}
