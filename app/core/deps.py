from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.enums import UserRole, ApprovalStatus
from app.models.admin import Admin
from app.models.vendor import Vendor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_token_from_cookie_or_header(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    authorization: Optional[str] = Header(None)
) -> str:
    """Extract token from HTTP-Only cookie first, then Bearer header fallback."""
    # 1. Try HTTP-Only cookie
    cookie_token = request.cookies.get(settings.ACCESS_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    # 2. Try OAuth2 scheme token
    if token:
        return token

    # 3. Try Authorization header
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated. Missing HTTP-Only cookie or Authorization header.",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_current_user(
    token: str = Depends(get_token_from_cookie_or_header),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Dependency: Extract and validate user from JWT token."""
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Enforce access token type
    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Expected access token.",
        )

    user_id = payload.get("sub")
    role_str = payload.get("role")

    if not user_id or not role_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identity or role.",
        )

    try:
        role = UserRole(role_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role in token payload.")

    if role == UserRole.ADMIN:
        user = db.query(Admin).filter(Admin.id == int(user_id)).first()
    else:
        user = db.query(Vendor).filter(Vendor.id == int(user_id)).first()

    if not user or not getattr(user, 'is_active', True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found or deactivated.")

    return {"user": user, "role": role, "payload": payload}

def require_roles(allowed_roles: List[UserRole]):
    """Dependency Injection Factory for Role-Based Access Control (RBAC)."""
    def role_checker(current: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if current["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {[r.value for r in allowed_roles]}",
            )
        return current
    return role_checker

def get_current_admin(current: Dict[str, Any] = Depends(require_roles([UserRole.ADMIN]))) -> Admin:
    """Dependency Injection: Restrict access to authenticated Admin users only."""
    return current["user"]

def get_current_approved_vendor(current: Dict[str, Any] = Depends(require_roles([UserRole.VENDOR]))) -> Vendor:
    """Dependency Injection: Restrict access to Approved Vendors only."""
    vendor: Vendor = current["user"]
    if vendor.approval_status != ApprovalStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Vendor account status is '{vendor.approval_status.value}'. Must be approved by an Admin.",
        )
    return vendor
