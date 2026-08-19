from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class RestockRequest(BaseModel):
    additional_quantity: int = Field(..., gt=0, description="Quantity to add to inventory stock")

class InventoryItem(BaseModel):
    product_id: int
    product_name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    vendor_id: int
    vendor_name: str
    price: float
    current_stock: int
    stock_status: str  # "IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"
    units_sold_total: int
    daily_sales_velocity: float
    estimated_days_remaining: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class LowStockAlert(BaseModel):
    product_id: int
    product_name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    vendor_id: int
    vendor_name: str
    price: float
    current_stock: int
    threshold: int
    units_sold: int
    alert_level: str  # "CRITICAL" (0 stock), "WARNING" (<= threshold)
    recommended_restock_quantity: int

    model_config = ConfigDict(from_attributes=True)

class InventorySummaryResponse(BaseModel):
    total_products_tracked: int
    in_stock_count: int
    low_stock_count: int
    out_of_stock_count: int
    threshold_applied: int
    items: List[InventoryItem]

class InventoryForecastResponse(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    daily_sales_velocity: float
    forecast_days: int
    projected_demand: int
    projected_stock_remaining: int
    stockout_predicted: bool
    estimated_stockout_days: Optional[int] = None
    recommended_reorder_quantity: int
    reorder_urgency: str  # "IMMEDIATE", "UPCOMING", "OPTIMAL"
