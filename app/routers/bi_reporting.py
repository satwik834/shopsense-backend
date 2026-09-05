from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.enums import UserRole
from app.schemas.bi_reporting import (
    SalesTrendResponse,
    CategoryDistributionResponse,
    VendorBenchmarkingResponse
)
from app.services.chart_analytics_service import ChartAnalyticsService
from app.services.benchmarking_service import BenchmarkingService
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/bi", tags=["Business Intelligence & Reporting"])

@router.get("/charts/sales-trends", response_model=SalesTrendResponse)
def get_sales_trends_chart(
    days: int = Query(30, ge=7, le=365, description="Historical trend window in days"),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Retrieve time-series daily sales volume and revenue trendlines formatted for frontend charts."""
    vendor_id = current["user"].id if current["role"] == UserRole.VENDOR else None
    return ChartAnalyticsService.get_sales_trends(db, vendor_id=vendor_id, days=days)

@router.get("/charts/category-distribution", response_model=CategoryDistributionResponse)
def get_category_distribution_chart(
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Retrieve category revenue and volume market share breakdowns formatted for frontend charts."""
    vendor_id = current["user"].id if current["role"] == UserRole.VENDOR else None
    return ChartAnalyticsService.get_category_distribution(db, vendor_id=vendor_id)

@router.get("/benchmarking", response_model=VendorBenchmarkingResponse)
def get_vendor_benchmarking(
    vendor_id: Optional[int] = Query(None, description="Optional vendor ID for Admin query; Vendors default to self"),
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Retrieve store-level benchmarking comparison metrics against marketplace averages."""
    if current["role"] == UserRole.VENDOR:
        target_vendor_id = current["user"].id
    else:
        target_vendor_id = vendor_id if vendor_id is not None else current["user"].id

    return BenchmarkingService.get_vendor_benchmarking(db, vendor_id=target_vendor_id)

@router.get("/export/sales-csv")
def export_sales_csv(
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Stream CSV report download for completed sales transactions."""
    vendor_id = current["user"].id if current["role"] == UserRole.VENDOR else None
    generator = ReportingService.generate_sales_csv(db, vendor_id=vendor_id)
    filename = "shopsense_sales_report.csv"
    return StreamingResponse(
        generator,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/inventory-csv")
def export_inventory_csv(
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Stream CSV report download for warehouse inventory levels and run-rate velocity."""
    vendor_id = current["user"].id if current["role"] == UserRole.VENDOR else None
    generator = ReportingService.generate_inventory_csv(db, vendor_id=vendor_id)
    filename = "shopsense_inventory_report.csv"
    return StreamingResponse(
        generator,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/customers-csv")
def export_customers_csv(
    db: Session = Depends(get_db),
    current: dict = Depends(get_current_user)
):
    """Stream CSV report download for customer RFM segmentation profiles and LTV metrics."""
    vendor_id = current["user"].id if current["role"] == UserRole.VENDOR else None
    generator = ReportingService.generate_customers_csv(db, vendor_id=vendor_id)
    filename = "shopsense_customer_rfm_report.csv"
    return StreamingResponse(
        generator,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
