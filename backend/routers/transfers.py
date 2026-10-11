"""
Transfers & Contracts Router - Player transfers, contracts, and market bids.
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..database import get_db_connection
from ..models import TransferResponse, TransferCreate, TransferUpdate

router = APIRouter(prefix="/api/transfers", tags=["Transfers & Contracts"])


def row_to_dict(row):
    return dict(row) if row else None


@router.get("", response_model=List[TransferResponse], summary="List all transfer market activities")
def get_transfers(
    transfer_status: Optional[str] = Query("ALL", description="Filter: ALL, PENDING, ACCEPTED, COMPLETED, REJECTED")
):
    """Retrieve transfer deals, market valuations, and contract proposals."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if transfer_status and transfer_status.upper() != "ALL":
        cursor.execute("SELECT * FROM transfers WHERE status = ? ORDER BY date DESC", (transfer_status.upper(),))
    else:
        cursor.execute("SELECT * FROM transfers ORDER BY date DESC")

    rows = cursor.fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


@router.get("/{transfer_id}", response_model=TransferResponse, summary="Get transfer proposal details")
def get_transfer(transfer_id: str):
    """Retrieve details for a single transfer offer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transfers WHERE id = ?", (transfer_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail=f"Transfer deal with ID '{transfer_id}' not found")
    return row_to_dict(row)


@router.post("", response_model=TransferResponse, status_code=status.HTTP_201_CREATED, summary="Submit transfer bid / contract offer")
def create_transfer(transfer_in: TransferCreate):
    """Submit a transfer bid for a player with fee and wage proposal."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM transfers")
    count = cursor.fetchone()["count"]
    new_id = f"TR{count + 1}"

    cursor.execute("""
        INSERT INTO transfers (
            id, player_id, player_name, from_team_id, from_team_name,
            to_team_id, to_team_name, transfer_fee, wage_weekly, contract_years, status, date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
    """, (
        new_id, transfer_in.player_id, transfer_in.player_name,
        transfer_in.from_team_id, transfer_in.from_team_name,
        transfer_in.to_team_id, transfer_in.to_team_name,
        transfer_in.transfer_fee, transfer_in.wage_weekly,
        transfer_in.contract_years, transfer_in.date
    ))

    conn.commit()
    cursor.execute("SELECT * FROM transfers WHERE id = ?", (new_id,))
    created = cursor.fetchone()
    conn.close()
    return row_to_dict(created)


@router.put("/{transfer_id}/status", response_model=TransferResponse, summary="Accept, reject, or complete transfer")
def update_transfer_status(transfer_id: str, status_in: TransferUpdate):
    """
    Update transfer status (PENDING, ACCEPTED, COMPLETED, REJECTED).
    If status is COMPLETED, player is automatically moved to the buyer team.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transfers WHERE id = ?", (transfer_id,))
    transfer = cursor.fetchone()
    if not transfer:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Transfer with ID '{transfer_id}' not found")

    new_status = status_in.status.upper()
    cursor.execute("UPDATE transfers SET status = ? WHERE id = ?", (new_status, transfer_id))

    # If completed, transfer the player automatically in players table
    if new_status == "COMPLETED":
        cursor.execute("""
            UPDATE players
            SET team_id = ?, team_name = ?
            WHERE id = ?
        """, (transfer["to_team_id"], transfer["to_team_name"], transfer["player_id"]))

    conn.commit()
    cursor.execute("SELECT * FROM transfers WHERE id = ?", (transfer_id,))
    updated = cursor.fetchone()
    conn.close()
    return row_to_dict(updated)


@router.delete("/{transfer_id}", status_code=status.HTTP_200_OK, summary="Cancel/delete transfer offer")
def delete_transfer(transfer_id: str):
    """Withdraw or remove a transfer proposal."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM transfers WHERE id = ?", (transfer_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Transfer with ID '{transfer_id}' not found")

    cursor.execute("DELETE FROM transfers WHERE id = ?", (transfer_id,))
    conn.commit()
    conn.close()
    return {"message": f"Transfer '{transfer_id}' successfully removed", "id": transfer_id}
