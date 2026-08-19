from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.customer_analytics import (
    CustomerSegment,
    CustomerSpendProfile,
    CustomerSegmentationSummaryResponse
)
from app.services.customer_analytics_service import CustomerAnalyticsService

router = APIRouter(prefix="/customer-analytics", tags=["Customer Analytics & Segmentation"])

@router.get("/segments", response_model=CustomerSegmentationSummaryResponse)
def get_customer_segments(
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Retrieve SQL-based customer segmentation overview, revenue distribution, and VIP profiles."""
    return CustomerAnalyticsService.get_segmentation_summary(db)

@router.get("/customers", response_model=List[CustomerSpendProfile])
def list_segmented_customers(
    segment: Optional[CustomerSegment] = Query(None, description="Filter customers by specific segment"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """List customer spending profiles with their computed RFM segmentation tier."""
    return CustomerAnalyticsService.list_segmented_customers(db, segment_filter=segment, skip=skip, limit=limit)

@router.get("/customers/{customer_id}", response_model=CustomerSpendProfile)
def get_customer_spend_profile(
    customer_id: int,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Retrieve comprehensive spending and segmentation history for an individual customer."""
    return CustomerAnalyticsService.get_customer_spend_profile(db, customer_id)
