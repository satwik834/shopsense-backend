from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import UserRole, ApprovalStatus

class VendorBase(BaseModel):
    name: str
    store_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    description: Optional[str] = None

class VendorCreate(VendorBase):
    password: str

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    store_name: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    approval_status: Optional[ApprovalStatus] = None

class VendorResponse(VendorBase):
    id: int
    role: UserRole
    approval_status: ApprovalStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
