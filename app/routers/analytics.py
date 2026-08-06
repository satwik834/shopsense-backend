from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin
from app.models.admin import Admin
from app.schemas.analytics import VendorAnalyticsResponse, MarketplaceSummaryResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/vendors/{vendor_id}", response_model=VendorAnalyticsResponse)
def get_vendor_analytics(
    vendor_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Calculate sales, revenue, and product analytics for a given vendor."""
    return AnalyticsService.get_vendor_analytics(db, vendor_id, current)

@router.get("/marketplace", response_model=MarketplaceSummaryResponse)
def get_marketplace_summary(
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    """Get high-level summary metrics across the entire ShopSense marketplace (Admin only)."""
    return AnalyticsService.get_marketplace_summary(db)
