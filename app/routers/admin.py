from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.enums import ApprovalStatus
from app.models.vendor import Vendor
from app.models.admin import Admin
from app.schemas.vendor import VendorResponse

router = APIRouter(prefix="/admin", tags=["Admin Controls"])

@router.get("/pending-vendors", response_model=List[VendorResponse])
def get_pending_vendors(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """List all vendors waiting for admin approval (Admin only)."""
    pending = db.query(Vendor).filter(Vendor.approval_status == ApprovalStatus.PENDING).all()
    return pending

@router.put("/vendors/{vendor_id}/approve", response_model=VendorResponse)
def approve_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Approve a pending vendor application (Admin only)."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )
    vendor.approval_status = ApprovalStatus.APPROVED
    vendor.is_active = True
    db.commit()
    db.refresh(vendor)
    return vendor

@router.put("/vendors/{vendor_id}/reject", response_model=VendorResponse)
def reject_vendor(
    vendor_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Reject a pending vendor application (Admin only)."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )
    vendor.approval_status = ApprovalStatus.REJECTED
    db.commit()
    db.refresh(vendor)
    return vendor
