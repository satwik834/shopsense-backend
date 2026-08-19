from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class RecommendedProduct(BaseModel):
    product_id: int
    name: str
    category: Optional[str] = None
    price: float
    stock_quantity: int
    vendor_id: int
    vendor_name: str
    total_units_sold: int
    recommendation_score: float
    recommendation_reason: str

    model_config = ConfigDict(from_attributes=True)

class CategoryTopSellersResponse(BaseModel):
    category: str
    total_products_evaluated: int
    top_sellers: List[RecommendedProduct]

class CrossSellResponse(BaseModel):
    base_product_id: int
    base_product_name: str
    base_category: Optional[str] = None
    frequently_bought_together: List[RecommendedProduct]

class CustomerPersonalizedRecommendationResponse(BaseModel):
    customer_id: int
    customer_name: str
    favorite_categories: List[str]
    total_past_purchases: int
    recommended_products: List[RecommendedProduct]
