from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.inventory import (
    InventorySummaryResponse,
    LowStockAlert,
    RestockRequest,
    InventoryForecastResponse
)
from app.schemas.product import ProductResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory Intelligence"])

@router.get("/stock-levels", response_model=InventorySummaryResponse)
def get_stock_levels(
    threshold: int = Query(10, ge=1, le=100, description="Stock threshold for low-stock classification"),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Retrieve real-time inventory stock levels, status classifications, and run-rate metrics."""
    return InventoryService.get_inventory_summary(db, current, threshold=threshold)

@router.get("/low-stock-alerts", response_model=List[LowStockAlert])
def get_low_stock_alerts(
    threshold: int = Query(10, ge=1, le=100, description="Stock threshold for triggering alerts"),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """List products that have breached low stock thresholds requiring immediate restocking."""
    return InventoryService.get_low_stock_alerts(db, current, threshold=threshold)

@router.put("/{product_id}/restock", response_model=ProductResponse)
def restock_product(
    product_id: int,
    restock_in: RestockRequest,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Restock inventory quantity for a specified product."""
    return InventoryService.restock_product(db, product_id, restock_in.additional_quantity, current)

@router.get("/{product_id}/forecast", response_model=InventoryForecastResponse)
def forecast_demand(
    product_id: int,
    days: int = Query(30, ge=7, le=90, description="Number of days to forecast inventory demand"),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Predict future product demand, estimated stockout timeline, and recommended reorder units."""
    return InventoryService.forecast_demand(db, product_id, days, current)
