import io
import csv
from typing import Generator, Optional
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.product import Product
from app.models.customer import Customer
from app.services.customer_analytics_service import CustomerAnalyticsService

class ReportingService:
    @staticmethod
    def generate_sales_csv(db: Session, vendor_id: Optional[int] = None) -> Generator[str, None, None]:
        output = io.StringIO()
        writer = csv.writer(output)

        # CSV Header
        writer.writerow([
            "Transaction ID",
            "Transaction Date",
            "Customer Name",
            "Customer Email",
            "Vendor Name",
            "Product Name",
            "Category",
            "Quantity",
            "Unit Price (INR)",
            "Total Amount (INR)",
            "Status"
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        query = db.query(Transaction).filter(Transaction.status == "completed")
        if vendor_id is not None:
            query = query.filter(Transaction.vendor_id == vendor_id)

        txs = query.order_by(Transaction.transaction_date.desc()).all()

        for t in txs:
            writer.writerow([
                t.id,
                t.transaction_date.strftime("%Y-%m-%d %H:%M:%S") if t.transaction_date else "",
                t.customer.name if t.customer else "",
                t.customer.email if t.customer else "",
                t.vendor.name if t.vendor else "",
                t.product.name if t.product else "",
                t.product.category if t.product else "",
                t.quantity,
                f"{t.unit_price:.2f}",
                f"{t.total_amount:.2f}",
                t.status
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    @staticmethod
    def generate_inventory_csv(db: Session, vendor_id: Optional[int] = None) -> Generator[str, None, None]:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Product ID",
            "Product Name",
            "SKU",
            "Category",
            "Vendor Name",
            "Unit Price (INR)",
            "Stock Quantity",
            "Stock Status",
            "Daily Sales Velocity (units/day)",
            "Stockout Run-Rate (Days)"
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        query = db.query(Product)
        if vendor_id is not None:
            query = query.filter(Product.vendor_id == vendor_id)

        products = query.order_by(Product.stock_quantity.asc()).all()

        for p in products:
            tx_count = db.query(Transaction).filter(
                Transaction.product_id == p.id,
                Transaction.status == "completed"
            ).count()

            velocity = max(round(tx_count / 30, 1), 0.5)
            days_left = max(round(p.stock_quantity / velocity), 0)

            status_str = "OUT_OF_STOCK" if p.stock_quantity == 0 else ("LOW_STOCK" if p.stock_quantity <= 10 else "IN_STOCK")

            writer.writerow([
                p.id,
                p.name,
                p.sku or "",
                p.category or "",
                p.vendor.name if p.vendor else "",
                f"{p.price:.2f}",
                p.stock_quantity,
                status_str,
                velocity,
                days_left
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    @staticmethod
    def generate_customers_csv(db: Session, vendor_id: Optional[int] = None) -> Generator[str, None, None]:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Customer ID",
            "Customer Name",
            "Email",
            "Phone",
            "Total Completed Orders",
            "Lifetime Spend (INR)",
            "Average Order Value (INR)",
            "RFM Segment Tier",
            "Segment Remarks"
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        profiles = CustomerAnalyticsService.list_segmented_customers(db, vendor_id=vendor_id)

        for p in profiles:
            writer.writerow([
                p.customer_id,
                p.name,
                p.email,
                p.phone or "",
                p.total_orders,
                f"{p.total_spent:.2f}",
                f"{p.average_order_value:.2f}",
                p.segment,
                p.segment_description
            ])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
