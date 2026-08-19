from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.customer import Customer
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.transaction import Transaction
from app.schemas.recommendation import (
    RecommendedProduct,
    CategoryTopSellersResponse,
    CrossSellResponse,
    CustomerPersonalizedRecommendationResponse
)

class RecommendationService:
    @staticmethod
    def _map_product_to_recommendation(
        db: Session,
        product: Product,
        reason: str,
        score: float
    ) -> RecommendedProduct:
        units_sold = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
            Transaction.product_id == product.id,
            Transaction.status == "completed"
        ).scalar()

        vendor_obj = product.vendor or db.query(Vendor).filter(Vendor.id == product.vendor_id).first()
        v_name = vendor_obj.name if vendor_obj else f"Vendor #{product.vendor_id}"

        return RecommendedProduct(
            product_id=product.id,
            name=product.name,
            category=product.category,
            price=product.price,
            stock_quantity=product.stock_quantity,
            vendor_id=product.vendor_id,
            vendor_name=v_name,
            total_units_sold=units_sold,
            recommendation_score=round(score, 2),
            recommendation_reason=reason
        )

    @staticmethod
    def get_top_selling_by_category(
        db: Session,
        category: Optional[str] = None,
        limit: int = 10
    ) -> CategoryTopSellersResponse:
        query = db.query(Product)
        if category:
            query = query.filter(Product.category == category)

        products = query.all()
        scored_products = []

        for p in products:
            units = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
                Transaction.product_id == p.id,
                Transaction.status == "completed"
            ).scalar()
            # Recommendation score based on sales volume and stock availability
            stock_factor = 1.0 if p.stock_quantity > 0 else 0.2
            score = float(units * 10 + (p.price / 100)) * stock_factor
            reason = f"Top-selling product in {p.category or 'marketplace'} with {units} units sold."

            scored_products.append(
                RecommendationService._map_product_to_recommendation(db, p, reason, score)
            )

        scored_products.sort(key=lambda x: x.recommendation_score, reverse=True)
        top_items = scored_products[:limit]

        return CategoryTopSellersResponse(
            category=category or "All Categories",
            total_products_evaluated=len(products),
            top_sellers=top_items
        )

    @staticmethod
    def get_frequently_bought_together(
        db: Session,
        product_id: int,
        limit: int = 5
    ) -> CrossSellResponse:
        base_product = db.query(Product).filter(Product.id == product_id).first()
        if not base_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found."
            )

        # Find other products in the same category or from the same vendor
        related_products = db.query(Product).filter(
            Product.id != product_id,
            (Product.category == base_product.category) | (Product.vendor_id == base_product.vendor_id)
        ).all()

        recommendations = []
        for p in related_products:
            units = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
                Transaction.product_id == p.id,
                Transaction.status == "completed"
            ).scalar()

            if p.category == base_product.category and p.vendor_id == base_product.vendor_id:
                reason = "Same vendor and category match with high co-affinity."
                score = float(units * 15 + 50)
            elif p.category == base_product.category:
                reason = f"Category complementary item ({base_product.category})."
                score = float(units * 10 + 30)
            else:
                reason = "Popular alternative item from the same merchant store."
                score = float(units * 8 + 15)

            if p.stock_quantity <= 0:
                score *= 0.3

            recommendations.append(
                RecommendationService._map_product_to_recommendation(db, p, reason, score)
            )

        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        return CrossSellResponse(
            base_product_id=base_product.id,
            base_product_name=base_product.name,
            base_category=base_product.category,
            frequently_bought_together=recommendations[:limit]
        )

    @staticmethod
    def get_customer_personalized_recommendations(
        db: Session,
        customer_id: int,
        limit: int = 6
    ) -> CustomerPersonalizedRecommendationResponse:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found."
            )

        # Find categories customer previously purchased
        past_txs = db.query(Transaction).filter(
            Transaction.customer_id == customer_id,
            Transaction.status == "completed"
        ).all()

        purchased_product_ids = {t.product_id for t in past_txs}
        category_counts = {}

        for t in past_txs:
            p = db.query(Product).filter(Product.id == t.product_id).first()
            if p and p.category:
                category_counts[p.category] = category_counts.get(p.category, 0) + t.quantity

        fav_categories = sorted(category_counts.keys(), key=lambda c: category_counts[c], reverse=True)

        # Recommend top items matching customer affinity
        candidate_products = db.query(Product).filter(Product.id.notin_(purchased_product_ids)).all()
        recommendations = []

        for p in candidate_products:
            units = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
                Transaction.product_id == p.id,
                Transaction.status == "completed"
            ).scalar()

            if p.category in category_counts:
                cat_weight = category_counts[p.category] * 20
                reason = f"Based on your interest in {p.category} products."
                score = float(units * 10 + cat_weight)
            else:
                reason = "Trending bestseller across the marketplace."
                score = float(units * 8)

            if p.stock_quantity <= 0:
                score *= 0.1

            recommendations.append(
                RecommendationService._map_product_to_recommendation(db, p, reason, score)
            )

        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        return CustomerPersonalizedRecommendationResponse(
            customer_id=customer.id,
            customer_name=customer.name,
            favorite_categories=fav_categories,
            total_past_purchases=len(past_txs),
            recommended_products=recommendations[:limit]
        )
