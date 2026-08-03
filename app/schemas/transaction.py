from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    customer_id: int
    vendor_id: int
    product_id: int
    quantity: int = Field(1, gt=0, description="Quantity must be at least 1")

class TransactionResponse(BaseModel):
    id: int
    customer_id: int
    vendor_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    status: str
    transaction_date: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
