from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate

class CustomerService:
    @staticmethod
    def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
        existing_customer = db.query(Customer).filter(Customer.email == customer_in.email).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email '{customer_in.email}' already exists."
            )

        customer = Customer(
            name=customer_in.name,
            email=customer_in.email,
            phone=customer_in.phone,
            address=customer_in.address
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def list_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
        return db.query(Customer).offset(skip).limit(limit).all()

    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Customer:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found."
            )
        return customer
