from pydantic import BaseModel, Field
from typing import List, Optional

# --- Chart Analytics Schemas ---
class SalesTrendPoint(BaseModel):
    date: str
    orders_count: int
    units_sold: int
    total_revenue: float

class CategoryDistributionPoint(BaseModel):
    category: str
    products_count: int
    units_sold: int
    total_revenue: float
    percentage_of_revenue: float

class SalesTrendResponse(BaseModel):
    period: str
    total_revenue: float
    total_orders: int
    total_units_sold: int
    trend_points: List[SalesTrendPoint]

class CategoryDistributionResponse(BaseModel):
    total_categories: int
    total_revenue: float
    categories: List[CategoryDistributionPoint]

# --- Benchmarking Schemas ---
class MetricBenchmark(BaseModel):
    metric_name: str
    vendor_value: float
    marketplace_avg: float
    percentage_diff: float
    performance_status: str  # ABOVE_AVERAGE, ON_PAR, BELOW_AVERAGE
    unit: str

class VendorBenchmarkingResponse(BaseModel):
    vendor_id: int
    vendor_name: str
    store_name: str
    overall_performance_rating: str
    metrics: List[MetricBenchmark]
    recommendations: List[str]
