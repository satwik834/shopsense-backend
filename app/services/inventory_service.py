from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone

from app.models.enums import UserRole
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.transaction import Transaction
from app.schemas.inventory import (
    InventoryItem,
    LowStockAlert,
    InventorySummaryResponse,
    InventoryForecastResponse
)

class InventoryService:
    @staticmethod
    def get_inventory_summary(
        db: Session,
        current: dict,
        threshold: int = 10
    ) -> InventorySummaryResponse:
        user = current["user"]
        role: UserRole = current["role"]

        query = db.query(Product)
        if role == UserRole.VENDOR:
            query = query.filter(Product.vendor_id == user.id)

        products = query.all()
        items: List[InventoryItem] = []

        in_stock = 0
        low_stock = 0
        out_of_stock = 0

        for p in products:
            # Calculate total units sold
            total_sold = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
                Transaction.product_id == p.id,
                Transaction.status == "completed"
            ).scalar()

            # Calculate days active based on product creation date
            created_at = p.created_at
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            days_active = max((datetime.now(timezone.utc) - created_at).days, 1)
            daily_velocity = round(total_sold / days_active, 2)

            # Determine stock status
            if p.stock_quantity == 0:
                status_str = "OUT_OF_STOCK"
                out_of_stock += 1
                days_rem = 0
            elif p.stock_quantity <= threshold:
                status_str = "LOW_STOCK"
                low_stock += 1
                days_rem = int(p.stock_quantity / daily_velocity) if daily_velocity > 0 else 999
            else:
                status_str = "IN_STOCK"
                in_stock += 1
                days_rem = int(p.stock_quantity / daily_velocity) if daily_velocity > 0 else 999

            vendor_obj = p.vendor or db.query(Vendor).filter(Vendor.id == p.vendor_id).first()
            v_name = vendor_obj.name if vendor_obj else f"Vendor #{p.vendor_id}"

            items.append(
                InventoryItem(
                    product_id=p.id,
                    product_name=p.name,
                    sku=p.sku,
                    category=p.category,
                    vendor_id=p.vendor_id,
                    vendor_name=v_name,
                    price=p.price,
                    current_stock=p.stock_quantity,
                    stock_status=status_str,
                    units_sold_total=total_sold,
                    daily_sales_velocity=daily_velocity,
                    estimated_days_remaining=days_rem if days_rem != 999 else None
                )
            )

        return InventorySummaryResponse(
            total_products_tracked=len(products),
            in_stock_count=in_stock,
            low_stock_count=low_stock,
            out_of_stock_count=out_of_stock,
            threshold_applied=threshold,
            items=items
        )

    @staticmethod
    def get_low_stock_alerts(
        db: Session,
        current: dict,
        threshold: int = 10
    ) -> List[LowStockAlert]:
        user = current["user"]
        role: UserRole = current["role"]

        query = db.query(Product).filter(Product.stock_quantity <= threshold)
        if role == UserRole.VENDOR:
            query = query.filter(Product.vendor_id == user.id)

        low_products = query.order_by(Product.stock_quantity.asc()).all()
        alerts: List[LowStockAlert] = []

        for p in low_products:
            total_sold = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
                Transaction.product_id == p.id,
                Transaction.status == "completed"
            ).scalar()

            alert_level = "CRITICAL" if p.stock_quantity == 0 else "WARNING"
            # Recommendation: Restock up to 3x threshold or at least 25 units
            recommended_restock = max(threshold * 3 - p.stock_quantity, 25)

            vendor_obj = p.vendor or db.query(Vendor).filter(Vendor.id == p.vendor_id).first()
            v_name = vendor_obj.name if vendor_obj else f"Vendor #{p.vendor_id}"

            alerts.append(
                LowStockAlert(
                    product_id=p.id,
                    product_name=p.name,
                    sku=p.sku,
                    category=p.category,
                    vendor_id=p.vendor_id,
                    vendor_name=v_name,
                    price=p.price,
                    current_stock=p.stock_quantity,
                    threshold=threshold,
                    units_sold=total_sold,
                    alert_level=alert_level,
                    recommended_restock_quantity=recommended_restock
                )
            )

        return alerts

    @staticmethod
    def restock_product(
        db: Session,
        product_id: int,
        additional_quantity: int,
        current: dict
    ) -> Product:
        user = current["user"]
        role: UserRole = current["role"]

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found."
            )

        if role == UserRole.VENDOR and product.vendor_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only restock products belonging to your store."
            )

        product.stock_quantity += additional_quantity
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def forecast_demand(
        db: Session,
        product_id: int,
        forecast_days: int,
        current: dict
    ) -> InventoryForecastResponse:
        user = current["user"]
        role: UserRole = current["role"]

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found."
            )

        if role == UserRole.VENDOR and product.vendor_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view forecasts for your own products."
            )

        total_sold = db.query(func.coalesce(func.sum(Transaction.quantity), 0)).filter(
            Transaction.product_id == product.id,
            Transaction.status == "completed"
        ).scalar()

        created_at = product.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        days_active = max((datetime.now(timezone.utc) - created_at).days, 1)

        # Baseline Daily Sales Velocity (run-rate model)
        daily_velocity = max(round(total_sold / days_active, 2), 0.2)
        projected_demand = int(round(daily_velocity * forecast_days))
        projected_stock_remaining = max(product.stock_quantity - projected_demand, 0)
        stockout_predicted = projected_demand > product.stock_quantity

        if stockout_predicted and daily_velocity > 0:
            est_days = int(product.stock_quantity / daily_velocity)
        else:
            est_days = None

        if product.stock_quantity <= 5 or (est_days is not None and est_days <= 7):
            urgency = "IMMEDIATE"
        elif est_days is not None and est_days <= 14:
            urgency = "UPCOMING"
        else:
            urgency = "OPTIMAL"

        recommended_reorder = max(projected_demand * 2 - product.stock_quantity, 20)

        return InventoryForecastResponse(
            product_id=product.id,
            product_name=product.name,
            current_stock=product.stock_quantity,
            daily_sales_velocity=daily_velocity,
            forecast_days=forecast_days,
            projected_demand=projected_demand,
            projected_stock_remaining=projected_stock_remaining,
            stockout_predicted=stockout_predicted,
            estimated_stockout_days=est_days,
            recommended_reorder_quantity=recommended_reorder,
            reorder_urgency=urgency
        )
