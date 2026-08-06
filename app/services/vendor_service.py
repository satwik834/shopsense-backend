from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.models.vendor import Vendor
from app.schemas.vendor import VendorUpdate

class VendorService:
    @staticmethod
    def get_vendor(db: Session, vendor_id: int) -> Vendor:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found."
            )
        return vendor

    @staticmethod
    def list_vendors(db: Session, skip: int = 0, limit: int = 100) -> List[Vendor]:
        return db.query(Vendor).offset(skip).limit(limit).all()

    @staticmethod
    def update_vendor(db: Session, vendor_id: int, vendor_in: VendorUpdate) -> Vendor:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found."
            )

        update_data = vendor_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)

        db.commit()
        db.refresh(vendor)
        return vendor

    @staticmethod
    def deactivate_vendor(db: Session, vendor_id: int) -> Vendor:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found."
            )
        vendor.is_active = False
        db.commit()
        db.refresh(vendor)
        return vendor
