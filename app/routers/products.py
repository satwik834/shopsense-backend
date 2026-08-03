from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.enums import UserRole
from app.models.vendor import Vendor
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Create a new product. Vendors automatically create products for their own store."""
    user = current["user"]
    role: UserRole = current["role"]

    if role == UserRole.VENDOR:
        # Force vendor ID to match logged in vendor
        target_vendor_id = user.id
        if user.approval_status != "approved":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your vendor account is not approved."
            )
    else:
        # Admin can specify vendor_id
        target_vendor_id = product_in.vendor_id
        vendor = db.query(Vendor).filter(Vendor.id == target_vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {target_vendor_id} does not exist."
            )

    if product_in.sku:
        existing_sku = db.query(Product).filter(Product.sku == product_in.sku).first()
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product_in.sku}' already exists."
            )

    product = Product(
        vendor_id=target_vendor_id,
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        stock_quantity=product_in.stock_quantity,
        category=product_in.category,
        sku=product_in.sku,
        image_url=product_in.image_url
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

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
    user = current["user"]
    role: UserRole = current["role"]

    query = db.query(Product)

    if role == UserRole.VENDOR:
        # Enforce vendor data isolation
        query = query.filter(Product.vendor_id == user.id)
    elif vendor_id:
        query = query.filter(Product.vendor_id == vendor_id)

    if category:
        query = query.filter(Product.category == category)

    return query.offset(skip).limit(limit).all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Get product details by ID."""
    user = current["user"]
    role: UserRole = current["role"]

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    if role == UserRole.VENDOR and product.vendor_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You do not own this product."
        )

    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Update product details or stock quantity."""
    user = current["user"]
    role: UserRole = current["role"]

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    if role == UserRole.VENDOR and product.vendor_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only update your own products."
        )

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Delete a product."""
    user = current["user"]
    role: UserRole = current["role"]

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    if role == UserRole.VENDOR and product.vendor_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only delete your own products."
        )

    db.delete(product)
    db.commit()
    return {"message": f"Product '{product.name}' (ID: {product_id}) deleted successfully."}
