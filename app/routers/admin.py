from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.admin import Admin
from app.schemas.vendor import VendorResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin Controls"])

@router.get("/pending-vendors", response_model=List[VendorResponse])
def get_pending_vendors(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Retrieve all pending vendor applications (Admin only)."""
    return AdminService.get_pending_vendors(db)

@router.put("/vendors/{vendor_id}/approve", response_model=VendorResponse)
def approve_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Approve a pending vendor application (Admin only)."""
    return AdminService.approve_vendor(db, vendor_id)

@router.put("/vendors/{vendor_id}/reject", response_model=VendorResponse)
def reject_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Reject a vendor application (Admin only)."""
    return AdminService.reject_vendor(db, vendor_id)
