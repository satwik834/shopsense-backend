from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0, description="Product price must be greater than 0")
    stock_quantity: int = Field(0, ge=0, description="Stock quantity must be >= 0")
    category: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    vendor_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    vendor_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
