from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.customer import Customer
from app.models.transaction import Transaction
from app.schemas.customer_analytics import (
    CustomerSegment,
    CustomerSpendProfile,
    SegmentBreakdown,
    CustomerSegmentationSummaryResponse
)

class CustomerAnalyticsService:
    @staticmethod
    def _calculate_customer_profile(db: Session, customer: Customer, vendor_id: Optional[int] = None) -> CustomerSpendProfile:
        tx_query = db.query(Transaction).filter(
            Transaction.customer_id == customer.id,
            Transaction.status == "completed"
        )
        if vendor_id is not None:
            tx_query = tx_query.filter(Transaction.vendor_id == vendor_id)

        txs = tx_query.order_by(Transaction.created_at.asc()).all()

        total_orders = len(txs)
        total_spent = sum(t.total_amount for t in txs)
        aov = round(total_spent / total_orders, 2) if total_orders > 0 else 0.0

        first_date = txs[0].created_at if txs else None
        last_date = txs[-1].created_at if txs else None

        # SQL-based segmentation rules
        if total_orders == 0:
            segment = CustomerSegment.INACTIVE
            desc = "Registered customer with 0 completed orders."
        elif total_spent >= 500.0 or total_orders >= 5:
            segment = CustomerSegment.VIP
            desc = "High-value customer contributing major lifetime revenue."
        elif total_spent >= 150.0 or total_orders >= 2:
            segment = CustomerSegment.REGULAR
            desc = "Consistent repeat buyer with steady order frequency."
        else:
            segment = CustomerSegment.NEW
            desc = "Single-order or low lifetime expenditure buyer."

        return CustomerSpendProfile(
            customer_id=customer.id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
            total_orders=total_orders,
            total_spent=round(total_spent, 2),
            average_order_value=aov,
            first_purchase_date=first_date,
            last_purchase_date=last_date,
            segment=segment,
            segment_description=desc
        )

    @staticmethod
    def get_segmentation_summary(db: Session, vendor_id: Optional[int] = None) -> CustomerSegmentationSummaryResponse:
        if vendor_id is not None:
            vendor_cust_ids = db.query(Transaction.customer_id).filter(
                Transaction.vendor_id == vendor_id,
                Transaction.status == "completed"
            ).distinct().all()
            cust_ids = [c[0] for c in vendor_cust_ids]
            customers = db.query(Customer).filter(Customer.id.in_(cust_ids)).all() if cust_ids else []
        else:
            customers = db.query(Customer).all()

        profiles = [CustomerAnalyticsService._calculate_customer_profile(db, c, vendor_id=vendor_id) for c in customers]

        total_cust = len(profiles)
        active_count = sum(1 for p in profiles if p.total_orders > 0)
        inactive_count = total_cust - active_count
        total_revenue = sum(p.total_spent for p in profiles)

        segment_counts = {
            CustomerSegment.VIP: 0,
            CustomerSegment.REGULAR: 0,
            CustomerSegment.NEW: 0,
            CustomerSegment.INACTIVE: 0
        }
        segment_revenues = {
            CustomerSegment.VIP: 0.0,
            CustomerSegment.REGULAR: 0.0,
            CustomerSegment.NEW: 0.0,
            CustomerSegment.INACTIVE: 0.0
        }

        for p in profiles:
            segment_counts[p.segment] += 1
            segment_revenues[p.segment] += p.total_spent

        segment_descriptions = {
            CustomerSegment.VIP: "High lifetime value spenders (>= 500 or >= 5 orders).",
            CustomerSegment.REGULAR: "Frequent repeat buyers (150 - 500 spend).",
            CustomerSegment.NEW: "First-time or introductory buyers (< 150 spend).",
            CustomerSegment.INACTIVE: "Registered buyers with zero completed orders."
        }

        breakdowns: List[SegmentBreakdown] = []
        for seg in [CustomerSegment.VIP, CustomerSegment.REGULAR, CustomerSegment.NEW, CustomerSegment.INACTIVE]:
            cnt = segment_counts[seg]
            rev = segment_revenues[seg]
            pct_cust = round((cnt / total_cust * 100), 1) if total_cust > 0 else 0.0
            pct_rev = round((rev / total_revenue * 100), 1) if total_revenue > 0 else 0.0
            avg_spend = round(rev / cnt, 2) if cnt > 0 else 0.0

            breakdowns.append(
                SegmentBreakdown(
                    segment=seg,
                    customer_count=cnt,
                    percentage_of_customers=pct_cust,
                    total_revenue_contributed=round(rev, 2),
                    percentage_of_revenue=pct_rev,
                    average_customer_spend=avg_spend,
                    description=segment_descriptions[seg]
                )
            )

        vip_profiles = [p for p in profiles if p.segment == CustomerSegment.VIP]
        vip_profiles.sort(key=lambda x: x.total_spent, reverse=True)

        return CustomerSegmentationSummaryResponse(
            total_customers=total_cust,
            active_buyers_count=active_count,
            inactive_buyers_count=inactive_count,
            total_customer_revenue=round(total_revenue, 2),
            segments=breakdowns,
            top_vip_customers=vip_profiles
        )

    @staticmethod
    def list_segmented_customers(
        db: Session,
        segment_filter: Optional[CustomerSegment] = None,
        skip: int = 0,
        limit: int = 100,
        vendor_id: Optional[int] = None
    ) -> List[CustomerSpendProfile]:
        if vendor_id is not None:
            vendor_cust_ids = db.query(Transaction.customer_id).filter(
                Transaction.vendor_id == vendor_id,
                Transaction.status == "completed"
            ).distinct().all()
            cust_ids = [c[0] for c in vendor_cust_ids]
            customers = db.query(Customer).filter(Customer.id.in_(cust_ids)).offset(skip).limit(limit).all() if cust_ids else []
        else:
            customers = db.query(Customer).offset(skip).limit(limit).all()

        profiles = [CustomerAnalyticsService._calculate_customer_profile(db, c, vendor_id=vendor_id) for c in customers]

        if segment_filter:
            profiles = [p for p in profiles if p.segment == segment_filter]

        profiles.sort(key=lambda x: x.total_spent, reverse=True)
        return profiles

    @staticmethod
    def get_customer_spend_profile(db: Session, customer_id: int, vendor_id: Optional[int] = None) -> CustomerSpendProfile:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found."
            )
        return CustomerAnalyticsService._calculate_customer_profile(db, customer, vendor_id=vendor_id)
