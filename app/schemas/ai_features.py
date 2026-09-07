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

# --- AI Product Copywriter & Listing Generator Schemas ---
class AIGenerateListingRequest(BaseModel):
    raw_notes: str = Field(..., description="Raw product notes or features")
    category: str = Field(..., description="Product category")
    target_price: Optional[float] = Field(None, description="Optional target price")

class AIGenerateListingResponse(BaseModel):
    suggested_title: str
    detailed_description: str
    seo_tags: List[str]
    marketing_bullets: List[str]
    is_gemini_powered: bool

# --- AI Smart Price Optimizer Schemas ---
class AIPriceOptimizerRequest(BaseModel):
    product_id: int = Field(..., description="Product ID to evaluate for optimal pricing")

class AIPriceOptimizerResponse(BaseModel):
    product_id: int
    product_name: str
    current_price: float
    recommended_price: float
    min_price_bound: float
    max_price_bound: float
    elasticity_rating: str  # HIGH, MODERATE, INELASTIC
    pricing_strategy_rationale: str
    projected_revenue_impact: str
    is_gemini_powered: bool
