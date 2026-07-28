from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, utc_now

class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="completed", nullable=False)
    transaction_date = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    vendor = relationship("Vendor", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.id}, customer_id={self.customer_id}, total_amount={self.total_amount})>"
