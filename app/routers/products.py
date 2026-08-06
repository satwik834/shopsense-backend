from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Create a new product. Vendors automatically create products for their own store."""
    return ProductService.create_product(db, product_in, current)

@router.get("/", response_model=List[ProductResponse])
def list_products(
    vendor_id: Optional[int] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """List products. Vendors ONLY see their own products."""
    return ProductService.list_products(db, current, vendor_id=vendor_id, category=category, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Get product details by ID."""
    return ProductService.get_product(db, product_id, current)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Update product details or stock quantity."""
    return ProductService.update_product(db, product_id, product_in, current)

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Delete a product."""
    return ProductService.delete_product(db, product_id, current)
