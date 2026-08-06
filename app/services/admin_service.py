from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.models.enums import ApprovalStatus
from app.models.vendor import Vendor
from app.schemas.vendor import VendorResponse

class AdminService:
    @staticmethod
    def get_pending_vendors(db: Session) -> List[Vendor]:
        return db.query(Vendor).filter(Vendor.approval_status == ApprovalStatus.PENDING).all()

    @staticmethod
    def approve_vendor(db: Session, vendor_id: int) -> Vendor:
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

    @staticmethod
    def reject_vendor(db: Session, vendor_id: int) -> Vendor:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found."
            )
        vendor.approval_status = ApprovalStatus.REJECTED
        vendor.is_active = False
        db.commit()
        db.refresh(vendor)
        return vendor
