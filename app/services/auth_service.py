from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token
)
from app.models.enums import UserRole, ApprovalStatus
from app.models.admin import Admin
from app.models.vendor import Vendor
from app.models.customer import Customer
from app.schemas.auth import VendorRegister, CustomerRegister

class AuthService:
    @staticmethod
    def register_vendor(db: Session, vendor_in: VendorRegister) -> Vendor:
        existing_vendor = db.query(Vendor).filter(Vendor.email == vendor_in.email).first()
        if existing_vendor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vendor with email '{vendor_in.email}' already exists."
            )

        vendor = Vendor(
            name=vendor_in.name,
            store_name=vendor_in.store_name,
            email=vendor_in.email,
            hashed_password=hash_password(vendor_in.password),
            phone=vendor_in.phone,
            description=vendor_in.description,
            role=UserRole.VENDOR,
            approval_status=ApprovalStatus.PENDING
        )
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        return vendor

    @staticmethod
    def register_customer(db: Session, customer_in: CustomerRegister) -> Customer:
        existing_customer = db.query(Customer).filter(Customer.email == customer_in.email).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with email '{customer_in.email}' already exists."
            )
        
        customer = Customer(
            name=customer_in.name,
            email=customer_in.email,
            hashed_password=hash_password(customer_in.password),
            phone=customer_in.phone,
            address=customer_in.address,
            role=UserRole.CUSTOMER.value,
            is_active=True
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def authenticate_user(db: Session, response: Response, email: str, password: str) -> dict:
        # Check Admin table first
        admin = db.query(Admin).filter(Admin.email == email).first()
        if admin and verify_password(password, admin.hashed_password):
            user_data = {
                "sub": str(admin.id),
                "email": admin.email,
                "role": UserRole.ADMIN.value,
                "id": admin.id,
                "name": admin.name
            }
            token_info = AuthService._set_auth_cookies(response, user_data)
            user_data["access_token"] = token_info["access_token"]
            return user_data

        # Check Vendor table next
        vendor = db.query(Vendor).filter(Vendor.email == email).first()
        if vendor and verify_password(password, vendor.hashed_password):
            if vendor.approval_status != ApprovalStatus.APPROVED.value and vendor.approval_status != ApprovalStatus.APPROVED:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your vendor registration application is PENDING or REJECTED. Please wait for Admin approval."
                )
            if not vendor.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your vendor account has been deactivated. Contact Admin."
                )

            user_data = {
                "sub": str(vendor.id),
                "email": vendor.email,
                "role": UserRole.VENDOR.value,
                "id": vendor.id,
                "name": vendor.name
            }
            token_info = AuthService._set_auth_cookies(response, user_data)
            user_data["access_token"] = token_info["access_token"]
            return user_data

        # Check Customer table next
        customer = db.query(Customer).filter(Customer.email == email).first()
        if customer and verify_password(password, customer.hashed_password):
            if not customer.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your customer account has been deactivated."
                )

            user_data = {
                "sub": str(customer.id),
                "email": customer.email,
                "role": UserRole.CUSTOMER.value,
                "id": customer.id,
                "name": customer.name
            }
            token_info = AuthService._set_auth_cookies(response, user_data)
            user_data["access_token"] = token_info["access_token"]
            return user_data

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    @staticmethod
    def refresh_tokens(db: Session, response: Response, refresh_token: str) -> dict:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token cookie missing."
            )

        payload = decode_access_token(refresh_token)
        if not payload or payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        user_id = payload.get("sub")
        role = payload.get("role")
        email = payload.get("email")

        user_data = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "id": int(user_id) if user_id and user_id.isdigit() else user_id,
            "name": payload.get("name")
        }

        # Issue fresh access token cookie
        access_token = create_access_token(user_data)
        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            samesite=settings.COOKIE_SAMESITE,
            secure=settings.COOKIE_SECURE,
            path="/"
        )
        return {"message": "Access token refreshed successfully"}

    @staticmethod
    def logout(response: Response) -> dict:
        response.delete_cookie(settings.ACCESS_COOKIE_NAME, path="/")
        response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/")
        return {"message": "Logged out successfully"}

    @staticmethod
    def _set_auth_cookies(response: Response, user_data: dict) -> dict:
        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)

        response.set_cookie(
            key=settings.ACCESS_COOKIE_NAME,
            value=access_token,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            httponly=True,
            samesite=settings.COOKIE_SAMESITE,
            secure=settings.COOKIE_SECURE,
            path="/"
        )
        response.set_cookie(
            key=settings.REFRESH_COOKIE_NAME,
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            httponly=True,
            samesite=settings.COOKIE_SAMESITE,
            secure=settings.COOKIE_SECURE,
            path="/"
        )

        return {"access_token": access_token, "refresh_token": refresh_token}
