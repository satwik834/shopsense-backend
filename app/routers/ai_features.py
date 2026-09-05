from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.enums import UserRole
from app.schemas.ai_features import (
    AIShoppingQueryRequest,
    AIShoppingQueryResponse,
    AIStoreAdvisorRequest,
    AIStoreAdvisorResponse
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI & Decision Intelligence"])

@router.post("/shopping-assistant", response_model=AIShoppingQueryResponse)
def ai_shopping_assistant(
    body: AIShoppingQueryRequest,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """RAG-powered AI Shopping Assistant answering customer product search and recommendation queries."""
    return AIService.answer_shopping_query(
        db,
        query=body.query,
        max_price=body.max_price,
        category=body.category
    )

@router.post("/store-advisor", response_model=AIStoreAdvisorResponse)
def ai_store_advisor(
    body: Optional[AIStoreAdvisorRequest] = None,
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """AI Data Analyst generating strategic diagnostic advice and revenue/inventory optimization guidance for merchant stores."""
    if current["role"] == UserRole.VENDOR:
        target_vendor_id = current["user"].id
    else:
        req_id = body.vendor_id if body and body.vendor_id is not None else None
        target_vendor_id = req_id if req_id is not None else current["user"].id

    return AIService.generate_store_advisor_report(db, vendor_id=target_vendor_id)
