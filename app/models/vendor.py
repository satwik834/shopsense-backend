from sqlalchemy import Column, Integer, String, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.enums import UserRole, ApprovalStatus

class Vendor(Base, TimestampMixin):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    store_name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.VENDOR, nullable=False)
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    products = relationship("Product", back_populates="vendor", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor(id={self.id}, name='{self.name}', email='{self.email}', status='{self.approval_status}')>"
