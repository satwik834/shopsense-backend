from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.recommendation import (
    CategoryTopSellersResponse,
    CrossSellResponse,
    CustomerPersonalizedRecommendationResponse
)
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Product Recommendations"])

@router.get("/top-selling", response_model=CategoryTopSellersResponse)
def get_top_selling_products(
    category: Optional[str] = Query(None, description="Optional category filter for top sellers"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Retrieve rule-based top selling products ranked by sales velocity."""
    return RecommendationService.get_top_selling_by_category(db, category=category, limit=limit)

@router.get("/frequently-bought-together/{product_id}", response_model=CrossSellResponse)
def get_frequently_bought_together(
    product_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Identify complementary and co-purchased cross-sell recommendations for a base product."""
    return RecommendationService.get_frequently_bought_together(db, product_id=product_id, limit=limit)

@router.get("/customer/{customer_id}", response_model=CustomerPersonalizedRecommendationResponse)
def get_customer_recommendations(
    customer_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Generate personalized recommendations based on the customer's historical purchasing affinity."""
    return RecommendationService.get_customer_personalized_recommendations(db, customer_id=customer_id, limit=limit)
