from pydantic import BaseModel, constr
from typing import Optional
from datetime import date
from app.models.contract import ContractType, ContractStatus

# Base Contract Schema
class ContractBase(BaseModel):
    type: ContractType
    status: ContractStatus = ContractStatus.PENDING
    start_date: date
    end_date: Optional[date] = None
    rent_amount: Optional[float] = None
    deposit_amount: Optional[float] = None
    payment_day: Optional[int] = None
    terms: Optional[str] = None
    notes: Optional[str] = None

# Schema for creating a contract
class ContractCreate(ContractBase):
    property_id: int
    tenant_id: int

# Schema for updating a contract
class ContractUpdate(BaseModel):
    type: Optional[ContractType] = None
    status: Optional[ContractStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    rent_amount: Optional[float] = None
    deposit_amount: Optional[float] = None
    payment_day: Optional[int] = None
    terms: Optional[str] = None
    notes: Optional[str] = None

# Schema for contract in response
class Contract(ContractBase):
    id: int
    property_id: int
    tenant_id: int

    class Config:
        from_attributes = True 