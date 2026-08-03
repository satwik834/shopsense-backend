from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    VENDOR = "vendor"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
