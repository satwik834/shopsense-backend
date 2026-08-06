from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.vendor import VendorUpdate, VendorResponse
from app.services.vendor_service import VendorService

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("/", response_model=List[VendorResponse])
def list_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered vendors."""
    return VendorService.list_vendors(db, skip=skip, limit=limit)

@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Get vendor profile by ID."""
    return VendorService.get_vendor(db, vendor_id)

@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: int, vendor_in: VendorUpdate, db: Session = Depends(get_db)):
    """Update vendor profile information."""
    return VendorService.update_vendor(db, vendor_id, vendor_in)

@router.delete("/{vendor_id}", response_model=VendorResponse)
def deactivate_vendor(vendor_id: int, db: Session = Depends(get_db)):
    """Deactivate a vendor account."""
    return VendorService.deactivate_vendor(db, vendor_id)
