from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.customer import Customer
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def record_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)):
    """Record a new sale transaction."""
    customer = db.query(Customer).filter(Customer.id == tx_in.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {tx_in.customer_id} not found."
        )

    vendor = db.query(Vendor).filter(Vendor.id == tx_in.vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {tx_in.vendor_id} not found."
        )

    product = db.query(Product).filter(Product.id == tx_in.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {tx_in.product_id} not found."
        )

    if product.vendor_id != tx_in.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product {tx_in.product_id} does not belong to vendor {tx_in.vendor_id}."
        )

    if product.stock_quantity < tx_in.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product '{product.name}'. Available: {product.stock_quantity}, requested: {tx_in.quantity}."
        )

    # Deduct stock
    product.stock_quantity -= tx_in.quantity

    unit_price = product.price
    total_amount = round(unit_price * tx_in.quantity, 2)

    transaction = Transaction(
        customer_id=tx_in.customer_id,
        vendor_id=tx_in.vendor_id,
        product_id=tx_in.product_id,
        quantity=tx_in.quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        status="completed"
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    vendor_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List transactions with optional filtering."""
    query = db.query(Transaction)
    if vendor_id:
        query = query.filter(Transaction.vendor_id == vendor_id)
    if customer_id:
        query = query.filter(Transaction.customer_id == customer_id)
    return query.offset(skip).limit(limit).all()
