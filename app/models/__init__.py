"""
Package models contenant les modèles de données de l'application.
"""

from .user import User, UserRole
from .property import Property, PropertyType, PropertyStatus
from .contract import Contract, ContractType, ContractStatus
from .payment import Payment, PaymentType, PaymentStatus
from .maintenance import MaintenanceRequest, MaintenanceType, MaintenanceStatus

# Export all models
__all__ = [
    "User",
    "UserRole",
    "Property",
    "PropertyType",
    "PropertyStatus",
    "Contract",
    "ContractType",
    "ContractStatus",
    "Payment",
    "PaymentType",
    "PaymentStatus",
    "MaintenanceRequest",
    "MaintenanceType",
    "MaintenanceStatus",
] 