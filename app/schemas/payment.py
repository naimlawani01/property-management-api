from pydantic import BaseModel, constr
from typing import Optional
from datetime import date
from app.models.payment import PaymentType, PaymentStatus

# Base Payment Schema
class PaymentBase(BaseModel):
    amount: float
    type: PaymentType
    status: PaymentStatus = PaymentStatus.PENDING
    due_date: date
    paid_date: Optional[date] = None
    reference: Optional[str] = None
    notes: Optional[str] = None

# Schema for creating a payment
class PaymentCreate(PaymentBase):
    contract_id: int

# Schema for updating a payment
class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[PaymentType] = None
    status: Optional[PaymentStatus] = None
    due_date: Optional[date] = None
    paid_date: Optional[date] = None
    reference: Optional[str] = None
    notes: Optional[str] = None

# Schema for payment in response
class Payment(PaymentBase):
    id: int
    contract_id: int

    class Config:
        from_attributes = True 