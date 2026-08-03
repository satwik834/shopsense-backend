from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin
from app.models.enums import UserRole
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.customer import Customer
from app.models.transaction import Transaction
from app.models.admin import Admin
from app.schemas.analytics import VendorAnalyticsResponse, VendorProductSummary, MarketplaceSummaryResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/vendors/{vendor_id}", response_model=VendorAnalyticsResponse)
def get_vendor_analytics(
    vendor_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Calculate sales, revenue, and product analytics for a given vendor."""
    user = current["user"]
    role: UserRole = current["role"]

    # Enforce RBAC: Vendor can ONLY view their own sales analytics
    if role == UserRole.VENDOR and user.id != vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own sales analytics."
        )

    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with ID {vendor_id} not found."
        )

    # Query completed transactions for this vendor
    tx_query = db.query(Transaction).filter(
        Transaction.vendor_id == vendor_id,
        Transaction.status == "completed"
    )

    total_orders = tx_query.count()
    total_revenue = db.query(func.coalesce(func.sum(Transaction.total_amount), 0.0)).filter(
        Transaction.vendor_id == vendor_id,
        Transaction.status == "completed"
    ).scalar()

    total_units_sold = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
        Transaction.vendor_id == vendor_id,
        Transaction.status == "completed"
    ).scalar()

    average_order_value = round(total_revenue / total_orders, 2) if total_orders > 0 else 0.0

    total_products_count = db.query(Product).filter(Product.vendor_id == vendor_id).count()

    # Calculate product performance
    products = db.query(Product).filter(Product.vendor_id == vendor_id).all()
    top_selling_products: List[VendorProductSummary] = []

    for prod in products:
        prod_units = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
            Transaction.product_id == prod.id,
            Transaction.status == "completed"
        ).scalar()

        prod_rev = db.query(func.coalesce(func.sum(Transaction.total_amount), 0.0)).filter(
            Transaction.product_id == prod.id,
            Transaction.status == "completed"
        ).scalar()

        top_selling_products.append(
            VendorProductSummary(
                id=prod.id,
                name=prod.name,
                price=prod.price,
                stock_quantity=prod.stock_quantity,
                units_sold=prod_units,
                revenue_generated=round(prod_rev, 2)
            )
        )

    # Sort products by revenue descending
    top_selling_products.sort(key=lambda p: p.revenue_generated, reverse=True)

    return VendorAnalyticsResponse(
        vendor_id=vendor.id,
        vendor_name=vendor.name,
        store_name=vendor.store_name,
        total_orders=total_orders,
        total_revenue=round(total_revenue, 2),
        total_units_sold=total_units_sold,
        average_order_value=average_order_value,
        total_products_count=total_products_count,
        top_selling_products=top_selling_products
    )

@router.get("/marketplace", response_model=MarketplaceSummaryResponse)
def get_marketplace_summary(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get high-level summary metrics across the entire ShopSense marketplace (Admin only)."""
    total_vendors = db.query(Vendor).count()
    total_customers = db.query(Customer).count()
    total_products = db.query(Product).count()
    total_transactions = db.query(Transaction).filter(Transaction.status == "completed").count()

    total_marketplace_revenue = db.query(func.coalesce(func.sum(Transaction.total_amount), 0.0)).filter(
        Transaction.status == "completed"
    ).scalar()

    avg_rev_per_vendor = (
        round(total_marketplace_revenue / total_vendors, 2) if total_vendors > 0 else 0.0
    )

    return MarketplaceSummaryResponse(
        total_vendors=total_vendors,
        total_customers=total_customers,
        total_products=total_products,
        total_transactions=total_transactions,
        total_marketplace_revenue=round(total_marketplace_revenue, 2),
        average_revenue_per_vendor=avg_rev_per_vendor
    )
