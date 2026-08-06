from fastapi import APIRouter, Depends, Response, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.auth import VendorRegister, LoginRequest, TokenResponse
from app.schemas.vendor import VendorResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register-vendor", response_model=VendorResponse)
def register_vendor(vendor_in: VendorRegister, db: Session = Depends(get_db)):
    """Register a new vendor account."""
    return AuthService.register_vendor(db, vendor_in)

@router.post("/login", response_model=TokenResponse)
def login(login_in: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate user credentials and set HTTP-Only JWT cookies."""
    user_data = AuthService.authenticate_user(db, response, login_in.email, login_in.password)
    return TokenResponse(
        access_token=user_data["access_token"],
        token_type="bearer",
        user_id=user_data["id"],
        user_name=user_data["name"],
        email=user_data["email"],
        role=user_data["role"]
    )

@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """Refresh access token cookie using refresh_token cookie."""
    refresh_cookie = request.cookies.get("refresh_token")
    return AuthService.refresh_tokens(db, response, refresh_cookie)

@router.post("/logout")
def logout(response: Response):
    """Log out user and clear HTTP-Only JWT cookies."""
    return AuthService.logout(response)

@router.get("/me")
def get_me(current: dict = Depends(get_current_user)):
    """Get authenticated user profile."""
    user = current["user"]
    role = current["role"]
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": role.value if hasattr(role, "value") else str(role),
        "approval_status": getattr(user, "approval_status", "approved")
    }
