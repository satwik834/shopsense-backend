from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from app.core.database import Base
from app.models.base import TimestampMixin
from app.models.enums import UserRole

class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.ADMIN, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Admin(id={self.id}, name='{self.name}', email='{self.email}')>"
