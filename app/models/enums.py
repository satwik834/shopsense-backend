from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    VENDOR = "vendor"
    CUSTOMER = "customer"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    