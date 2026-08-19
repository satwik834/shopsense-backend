from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime

class CustomerSegment(str, Enum):
    VIP = "VIP"              # Total spent >= ₹500
    REGULAR = "REGULAR"      # Total spent between ₹150 - ₹500
    NEW = "NEW"              # Total spent > 0 and < ₹150
    INACTIVE = "INACTIVE"    # 0 completed purchases

class CustomerSpendProfile(BaseModel):
    customer_id: int
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    total_orders: int
    total_spent: float
    average_order_value: float
    first_purchase_date: Optional[datetime] = None
    last_purchase_date: Optional[datetime] = None
    segment: CustomerSegment
    segment_description: str

    model_config = ConfigDict(from_attributes=True)

class SegmentBreakdown(BaseModel):
    segment: CustomerSegment
    customer_count: int
    percentage_of_customers: float
    total_revenue_contributed: float
    percentage_of_revenue: float
    average_customer_spend: float
    description: str

class CustomerSegmentationSummaryResponse(BaseModel):
    total_customers: int
    active_buyers_count: int
    inactive_buyers_count: int
    total_customer_revenue: float
    segments: List[SegmentBreakdown]
    top_vip_customers: List[CustomerSpendProfile]
