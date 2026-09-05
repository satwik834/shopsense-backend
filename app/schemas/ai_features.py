from pydantic import BaseModel, Field
from typing import List, Optional

# --- RAG AI Shopping Assistant Schemas ---
class AIShoppingQueryRequest(BaseModel):
    query: str = Field(..., description="Customer natural language search or recommendation query")
    max_price: Optional[float] = Field(None, description="Optional maximum price filter")
    category: Optional[str] = Field(None, description="Optional product category filter")

class GroundedProductResult(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float
    vendor_name: str
    stock_status: str
    match_score: int
    match_reason: str

class AIShoppingQueryResponse(BaseModel):
    query: str
    ai_response: str
    suggested_products: List[GroundedProductResult]
    is_gemini_powered: bool

# --- AI Data Analyst & Store Advisor Schemas ---
class AIStoreAdvisorRequest(BaseModel):
    vendor_id: Optional[int] = Field(None, description="Vendor ID to audit (Admin can pass specific ID; Vendor defaults to self)")

class StoreDiagnosticInsight(BaseModel):
    category: str  # Sales Trend, Inventory Risk, Customer Retention, Pricing Strategy
    title: str
    finding: str
    impact_level: str  # HIGH, MEDIUM, LOW
    actionable_recommendation: str

class AIStoreAdvisorResponse(BaseModel):
    vendor_id: int
    store_name: str
    executive_summary: str
    diagnostics: List[StoreDiagnosticInsight]
    ai_generated_strategy: str
    is_gemini_powered: bool
