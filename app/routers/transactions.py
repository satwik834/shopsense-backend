from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def record_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)):
    """Record a purchase transaction, deduct inventory stock, and lock historical unit price."""
    return TransactionService.record_transaction(db, tx_in)

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    vendor_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List purchase transactions with optional vendor or customer filters."""
    return TransactionService.list_transactions(db, vendor_id=vendor_id, customer_id=customer_id, skip=skip, limit=limit)

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get transaction details by ID."""
    return TransactionService.get_transaction(db, transaction_id)
