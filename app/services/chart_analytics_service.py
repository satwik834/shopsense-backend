from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.transaction import Transaction
from app.models.product import Product
from app.schemas.bi_reporting import (
    SalesTrendPoint,
    SalesTrendResponse,
    CategoryDistributionPoint,
    CategoryDistributionResponse
)

class ChartAnalyticsService:
    @staticmethod
    def get_sales_trends(db: Session, vendor_id: Optional[int] = None, days: int = 30) -> SalesTrendResponse:
        query = db.query(Transaction).filter(Transaction.status == "completed")
        if vendor_id is not None:
            query = query.filter(Transaction.vendor_id == vendor_id)

        txs = query.order_by(Transaction.transaction_date.asc()).all()

        # Group transactions by date string YYYY-MM-DD
        trend_map = {}
        # Populate empty baseline for the last 'days'
        today = datetime.utcnow().date()
        for i in range(days - 1, -1, -1):
            d_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            trend_map[d_str] = {"orders": 0, "units": 0, "revenue": 0.0}

        for t in txs:
            if t.transaction_date:
                d_str = t.transaction_date.strftime("%Y-%m-%d")
                if d_str in trend_map:
                    trend_map[d_str]["orders"] += 1
                    trend_map[d_str]["units"] += t.quantity
                    trend_map[d_str]["revenue"] += t.total_amount
                else:
                    # Include transactions outside window if any
                    trend_map[d_str] = {
                        "orders": 1,
                        "units": t.quantity,
                        "revenue": t.total_amount
                    }

        sorted_dates = sorted(trend_map.keys())
        points = [
            SalesTrendPoint(
                date=d,
                orders_count=trend_map[d]["orders"],
                units_sold=trend_map[d]["units"],
                total_revenue=round(trend_map[d]["revenue"], 2)
            ) for d in sorted_dates
        ]

        tot_rev = sum(p.total_revenue for p in points)
        tot_orders = sum(p.orders_count for p in points)
        tot_units = sum(p.units_sold for p in points)

        return SalesTrendResponse(
            period=f"Last {days} Days",
            total_revenue=round(tot_rev, 2),
            total_orders=tot_orders,
            total_units_sold=tot_units,
            trend_points=points
        )

    @staticmethod
    def get_category_distribution(db: Session, vendor_id: Optional[int] = None) -> CategoryDistributionResponse:
        tx_query = db.query(Transaction).filter(Transaction.status == "completed")
        if vendor_id is not None:
            tx_query = tx_query.filter(Transaction.vendor_id == vendor_id)

        txs = tx_query.all()

        prod_query = db.query(Product)
        if vendor_id is not None:
            prod_query = prod_query.filter(Product.vendor_id == vendor_id)
        products = prod_query.all()

        cat_prod_map = {}
        for p in products:
            cat = p.category or "Uncategorized"
            cat_prod_map[cat] = cat_prod_map.get(cat, 0) + 1

        cat_data = {}
        for t in txs:
            cat = t.product.category if t.product and t.product.category else "Uncategorized"
            if cat not in cat_data:
                cat_data[cat] = {"units": 0, "revenue": 0.0}
            cat_data[cat]["units"] += t.quantity
            cat_data[cat]["revenue"] += t.total_amount

        all_categories = set(cat_prod_map.keys()).union(set(cat_data.keys()))
        tot_rev = sum(d["revenue"] for d in cat_data.values())

        points = []
        for cat in sorted(all_categories):
            p_cnt = cat_prod_map.get(cat, 0)
            u_cnt = cat_data.get(cat, {}).get("units", 0)
            rev = cat_data.get(cat, {}).get("revenue", 0.0)
            pct = round((rev / tot_rev * 100), 1) if tot_rev > 0 else 0.0

            points.append(
                CategoryDistributionPoint(
                    category=cat,
                    products_count=p_cnt,
                    units_sold=u_cnt,
                    total_revenue=round(rev, 2),
                    percentage_of_revenue=pct
                )
            )

        points.sort(key=lambda x: x.total_revenue, reverse=True)

        return CategoryDistributionResponse(
            total_categories=len(points),
            total_revenue=round(tot_rev, 2),
            categories=points
        )
