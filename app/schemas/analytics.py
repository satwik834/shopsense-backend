from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class VendorProductSummary(BaseModel):
    id: int
    name: str
    price: float
    stock_quantity: int
    units_sold: int
    revenue_generated: float

class VendorAnalyticsResponse(BaseModel):
    vendor_id: int
    vendor_name: str
    store_name: Optional[str] = None
    total_orders: int
    total_revenue: float
    total_units_sold: int
    average_order_value: float
    total_products_count: int
    top_selling_products: List[VendorProductSummary] = []

    model_config = ConfigDict(from_attributes=True)

class MarketplaceSummaryResponse(BaseModel):
    total_vendors: int
    total_customers: int
    total_products: int
    total_transactions: int
    total_marketplace_revenue: float
    average_revenue_per_vendor: float

    model_config = ConfigDict(from_attributes=True)
