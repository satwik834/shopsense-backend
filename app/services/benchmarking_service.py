from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.vendor import Vendor
from app.models.product import Product
from app.models.transaction import Transaction
from app.schemas.bi_reporting import (
    MetricBenchmark,
    VendorBenchmarkingResponse
)

class BenchmarkingService:
    @staticmethod
    def get_vendor_benchmarking(db: Session, vendor_id: int) -> VendorBenchmarkingResponse:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {vendor_id} not found."
            )

        all_vendors = db.query(Vendor).all()
        total_vendor_count = max(len(all_vendors), 1)

        # 1. Average Order Value (AOV)
        vendor_txs = db.query(Transaction).filter(
            Transaction.vendor_id == vendor_id,
            Transaction.status == "completed"
        ).all()
        v_order_count = len(vendor_txs)
        v_total_revenue = sum(t.total_amount for t in vendor_txs)
        v_aov = round(v_total_revenue / v_order_count, 2) if v_order_count > 0 else 0.0

        all_txs = db.query(Transaction).filter(Transaction.status == "completed").all()
        m_order_count = len(all_txs)
        m_total_revenue = sum(t.total_amount for t in all_txs)
        m_aov = round(m_total_revenue / m_order_count, 2) if m_order_count > 0 else 0.0

        # 2. Revenue Per Active Product
        v_prods = db.query(Product).filter(Product.vendor_id == vendor_id).all()
        v_prod_count = max(len(v_prods), 1)
        v_rev_per_prod = round(v_total_revenue / v_prod_count, 2)

        m_prods = db.query(Product).all()
        m_prod_count = max(len(m_prods), 1)
        m_rev_per_prod = round(m_total_revenue / m_prod_count, 2)

        # 3. Low-Stock Ratio (%)
        v_low_stock = sum(1 for p in v_prods if p.stock_quantity <= 10)
        v_low_stock_ratio = round((v_low_stock / v_prod_count * 100), 1)

        m_low_stock = sum(1 for p in m_prods if p.stock_quantity <= 10)
        m_low_stock_ratio = round((m_low_stock / m_prod_count * 100), 1)

        # 4. Units Sold Per Product (Sales Velocity Proxy)
        v_units_sold = sum(t.quantity for t in vendor_txs)
        v_units_per_prod = round(v_units_sold / v_prod_count, 1)

        m_units_sold = sum(t.quantity for t in all_txs)
        m_units_per_prod = round(m_units_sold / m_prod_count, 1)

        # Compute metric benchmark points
        def calc_metric(name: str, v_val: float, m_val: float, unit: str, lower_is_better: bool = False) -> MetricBenchmark:
            diff = round((v_val - m_val) / m_val * 100, 1) if m_val > 0 else 0.0
            if lower_is_better:
                if diff < -5:
                    status_label = "ABOVE_AVERAGE"  # Lower low-stock ratio is better
                elif diff > 5:
                    status_label = "BELOW_AVERAGE"
                else:
                    status_label = "ON_PAR"
            else:
                if diff > 5:
                    status_label = "ABOVE_AVERAGE"
                elif diff < -5:
                    status_label = "BELOW_AVERAGE"
                else:
                    status_label = "ON_PAR"

            return MetricBenchmark(
                metric_name=name,
                vendor_value=v_val,
                marketplace_avg=m_val,
                percentage_diff=diff,
                performance_status=status_label,
                unit=unit
            )

        m1 = calc_metric("Average Order Value (AOV)", v_aov, m_aov, "INR")
        m2 = calc_metric("Revenue Per Product", v_rev_per_prod, m_rev_per_prod, "INR")
        m3 = calc_metric("Inventory Vulnerability (Low-Stock Ratio)", v_low_stock_ratio, m_low_stock_ratio, "%", lower_is_better=True)
        m4 = calc_metric("Sales Velocity (Units Sold/Item)", v_units_per_prod, m_units_per_prod, "Units")

        metrics_list = [m1, m2, m3, m4]

        # Overall rating calculation
        above_cnt = sum(1 for m in metrics_list if m.performance_status == "ABOVE_AVERAGE")
        below_cnt = sum(1 for m in metrics_list if m.performance_status == "BELOW_AVERAGE")

        if above_cnt >= 2:
            rating = "MARKETPLACE_LEADER"
        elif below_cnt >= 2:
            rating = "NEEDS_OPTIMIZATION"
        else:
            rating = "STEADY_PERFORMER"

        # Actionable recommendations
        recs = []
        if m1.performance_status == "BELOW_AVERAGE":
            recs.append("Bundle low-cost accessories to increase your Average Order Value (AOV).")
        if m3.performance_status == "BELOW_AVERAGE":
            recs.append("Immediate restocking required: your low-stock inventory ratio exceeds marketplace safety benchmarks.")
        if m4.performance_status == "ABOVE_AVERAGE":
            recs.append("High sales velocity detected: consider expanding your catalog inventory to prevent stockouts.")
        if not recs:
            recs.append("Store performance is balanced and tracking aligned with marketplace averages.")

        return VendorBenchmarkingResponse(
            vendor_id=vendor.id,
            vendor_name=vendor.name,
            store_name=vendor.store_name,
            overall_performance_rating=rating,
            metrics=metrics_list,
            recommendations=recs
        )
