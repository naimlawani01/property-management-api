from pydantic import BaseModel, constr
from typing import Optional
from datetime import date
from app.models.maintenance import MaintenanceStatus, MaintenanceType

# Base Maintenance Request Schema
class MaintenanceRequestBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    description: str
    type: MaintenanceType
    status: MaintenanceStatus = MaintenanceStatus.PENDING
    priority: int = 1  # 1-5, 5 being highest
    request_date: date
    completion_date: Optional[date] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

# Schema for creating a maintenance request
class MaintenanceRequestCreate(MaintenanceRequestBase):
    property_id: int
    requested_by_id: int
    assigned_to_id: Optional[int] = None

# Schema for updating a maintenance request
class MaintenanceRequestUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    type: Optional[MaintenanceType] = None
    status: Optional[MaintenanceStatus] = None
    priority: Optional[int] = None
    completion_date: Optional[date] = None
    cost: Optional[float] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None

# Schema for maintenance request in response
class MaintenanceRequest(MaintenanceRequestBase):
    id: int
    property_id: int
    requested_by_id: int
    assigned_to_id: Optional[int] = None

    class Config:
        from_attributes = True 