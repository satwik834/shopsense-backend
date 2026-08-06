from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.vendor import Vendor
from app.models.customer import Customer
from app.models.product import Product
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate

class TransactionService:
    @staticmethod
    def record_transaction(db: Session, tx_in: TransactionCreate) -> Transaction:
        # Validate Customer existence
        customer = db.query(Customer).filter(Customer.id == tx_in.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {tx_in.customer_id} does not exist."
            )

        # Validate Vendor existence
        vendor = db.query(Vendor).filter(Vendor.id == tx_in.vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {tx_in.vendor_id} does not exist."
            )

        # Validate Product existence & vendor ownership
        product = db.query(Product).filter(Product.id == tx_in.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {tx_in.product_id} does not exist."
            )

        if product.vendor_id != tx_in.vendor_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' does not belong to Vendor ID {tx_in.vendor_id}."
            )

        # Verify sufficient stock
        if product.stock_quantity < tx_in.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient inventory stock for '{product.name}'. Available: {product.stock_quantity}, Requested: {tx_in.quantity}."
            )

        # Calculate unit price and total amount
        unit_price = product.price
        total_amount = round(unit_price * tx_in.quantity, 2)

        # Create Transaction record
        transaction = Transaction(
            customer_id=tx_in.customer_id,
            vendor_id=tx_in.vendor_id,
            product_id=tx_in.product_id,
            quantity=tx_in.quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            status="completed"
        )

        # Deduct stock quantity from product
        product.stock_quantity -= tx_in.quantity

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def list_transactions(
        db: Session,
        vendor_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Transaction]:
        query = db.query(Transaction)
        if vendor_id:
            query = query.filter(Transaction.vendor_id == vendor_id)
        if customer_id:
            query = query.filter(Transaction.customer_id == customer_id)
        return query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_transaction(db: Session, transaction_id: int) -> Transaction:
        tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Transaction with ID {transaction_id} not found."
            )
        return tx
