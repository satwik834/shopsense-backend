from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorResponse

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def register_vendor(vendor_in: VendorCreate, db: Session = Depends(get_db)):
    """Register a new vendor."""
    existing_vendor = db.query(Vendor).filter(Vendor.email == vendor_in.email).first()
    if existing_vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A vendor with this email already exists."
        )
    
    vendor = Vendor(
        name=vendor_in.name,
        store_name=vendor_in.store_name,
        email=vendor_in.email,
        phone=vendor_in.phone,
        description=vendor_in.description
    )
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor

@router.get("/", response_model=List[VendorResponse])
def list_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered vendors."""
    vendors = db.query(Vendor).offset(skip).limit(limit).all()
    return vendors

@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor_profile(vendor_id: int, db: Session = Depends(get_db)):
    """Get vendor profile by vendor ID."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )
    return vendor

@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor_profile(vendor_id: int, vendor_in: VendorUpdate, db: Session = Depends(get_db)):
    """Update vendor profile information."""
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

@router.delete("/{vendor_id}", status_code=status.HTTP_200_OK)
def deactivate_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Deactivate a vendor profile."""
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )
    vendor.is_active = False
    db.commit()
    return {"message": f"Vendor {vendor_id} has been deactivated successfully."}
