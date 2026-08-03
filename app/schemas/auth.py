from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.models.enums import UserRole, ApprovalStatus

class VendorRegister(BaseModel):
    name: str
    store_name: Optional[str] = None
    email: EmailStr
    password: str
    phone: Optional[str] = None
    description: Optional[str] = None

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str
    email: str
    role: UserRole
    approval_status: Optional[ApprovalStatus] = None

    model_config = ConfigDict(from_attributes=True)

class VendorApprovalAction(BaseModel):
    status: ApprovalStatus
