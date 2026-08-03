from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.deps import get_current_user
from app.models.enums import UserRole, ApprovalStatus
from app.models.admin import Admin
from app.models.vendor import Vendor
from app.schemas.auth import VendorRegister, LoginRequest, TokenResponse
from app.schemas.vendor import VendorResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register-vendor", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def register_vendor(vendor_in: VendorRegister, db: Session = Depends(get_db)):
    """Register a new vendor (Account starts in PENDING approval status)."""
    existing_vendor = db.query(Vendor).filter(Vendor.email == vendor_in.email).first()
    if existing_vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A vendor with this email already exists."
        )

    existing_admin = db.query(Admin).filter(Admin.email == vendor_in.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    hashed_pw = hash_password(vendor_in.password)

    vendor = Vendor(
        name=vendor_in.name,
        store_name=vendor_in.store_name,
        email=vendor_in.email,
        hashed_password=hashed_pw,
        phone=vendor_in.phone,
        description=vendor_in.description,
        role=UserRole.VENDOR,
        approval_status=ApprovalStatus.PENDING,
        is_active=True
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

@router.post("/login", response_model=TokenResponse)
def login(login_in: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate Admin or Vendor using Argon2 and issue JWT Token."""
    # Check Admin first
    admin = db.query(Admin).filter(Admin.email == login_in.email).first()
    if admin:
        if not verify_password(login_in.password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )
        
        token = create_access_token({"sub": str(admin.id), "role": UserRole.ADMIN.value})
        return TokenResponse(
            access_token=token,
            user_id=admin.id,
            user_name=admin.name,
            email=admin.email,
            role=UserRole.ADMIN
        )

    # Check Vendor
    vendor = db.query(Vendor).filter(Vendor.email == login_in.email).first()
    if vendor:
        if not verify_password(login_in.password, vendor.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        # Enforce Vendor Approval Check
        if vendor.approval_status == ApprovalStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your vendor account is pending approval by an admin. Please wait for approval before logging in."
            )
        elif vendor.approval_status == ApprovalStatus.REJECTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your vendor account application was rejected by an admin."
            )

        if not vendor.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your vendor account has been deactivated."
            )

        token = create_access_token({"sub": str(vendor.id), "role": UserRole.VENDOR.value})
        return TokenResponse(
            access_token=token,
            user_id=vendor.id,
            user_name=vendor.name,
            email=vendor.email,
            role=UserRole.VENDOR,
            approval_status=vendor.approval_status
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password."
    )

@router.get("/me")
def get_current_user_profile(current: dict = Depends(get_current_user)):
    """Get current authenticated user profile."""
    user = current["user"]
    role: UserRole = current["role"]
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": role.value,
        "approval_status": getattr(user, 'approval_status', None),
        "is_active": user.is_active
    }
