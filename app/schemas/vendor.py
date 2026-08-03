from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class VendorBase(BaseModel):
    name: str
    store_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    description: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    store_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class VendorResponse(VendorBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
