from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_access_token
from app.core.deps import get_current_user
from app.models.enums import UserRole, ApprovalStatus
from app.models.admin import Admin
from app.models.vendor import Vendor
from app.schemas.auth import VendorRegister, LoginRequest, TokenResponse
from app.schemas.vendor import VendorResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    """Set HTTP-Only cookies for access and refresh tokens."""
    response.set_cookie(
        key=settings.ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        path="/"
    )
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        path="/"
    )

def clear_auth_cookies(response: Response):
    """Clear HTTP-Only auth cookies upon logout."""
    response.delete_cookie(key=settings.ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(key=settings.REFRESH_COOKIE_NAME, path="/")

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
def login(login_in: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate Admin or Vendor, issue JWT tokens and set HTTP-Only Cookies."""
    # Check Admin first
    admin = db.query(Admin).filter(Admin.email == login_in.email).first()
    if admin:
        if not verify_password(login_in.password, admin.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )
        
        acc_token = create_access_token({"sub": str(admin.id), "role": UserRole.ADMIN.value})
        ref_token = create_refresh_token({"sub": str(admin.id), "role": UserRole.ADMIN.value})

        # Set HTTP-Only Cookies
        set_auth_cookies(response, acc_token, ref_token)

        return TokenResponse(
            access_token=acc_token,
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

        acc_token = create_access_token({"sub": str(vendor.id), "role": UserRole.VENDOR.value})
        ref_token = create_refresh_token({"sub": str(vendor.id), "role": UserRole.VENDOR.value})

        # Set HTTP-Only Cookies
        set_auth_cookies(response, acc_token, ref_token)

        return TokenResponse(
            access_token=acc_token,
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

@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """Exchange valid HTTP-Only Refresh Token for a fresh Access Token."""
    refresh_tok = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not refresh_tok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token cookie."
        )

    payload = decode_access_token(refresh_tok)
    if not payload or payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    user_id = payload.get("sub")
    role_str = payload.get("role")

    if not user_id or not role_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload.")

    try:
        role = UserRole(role_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role in refresh token.")

    # Re-verify user exists and is active
    if role == UserRole.ADMIN:
        user = db.query(Admin).filter(Admin.id == int(user_id)).first()
    else:
        user = db.query(Vendor).filter(Vendor.id == int(user_id)).first()

    if not user or not getattr(user, 'is_active', True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found or deactivated.")

    # Create new access token and new refresh token
    new_access = create_access_token({"sub": str(user.id), "role": role.value})
    new_refresh = create_refresh_token({"sub": str(user.id), "role": role.value})

    set_auth_cookies(response, new_access, new_refresh)

    return {
        "message": "Token refreshed successfully",
        "user_id": user.id,
        "role": role.value
    }

@router.post("/logout")
def logout(response: Response):
    """Clear HTTP-Only authentication cookies."""
    clear_auth_cookies(response)
    return {"message": "Logged out successfully"}

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
