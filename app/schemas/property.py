from pydantic import BaseModel, constr
from typing import Optional
from app.models.property import PropertyType, PropertyStatus

# Base Property Schema
class PropertyBase(BaseModel):
    title: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    type: PropertyType
    status: PropertyStatus = PropertyStatus.AVAILABLE
    
    # Location
    address: constr(min_length=1)
    city: constr(min_length=1)
    postal_code: constr(min_length=1)
    country: constr(min_length=1)
    
    # Characteristics
    surface_area: float
    number_of_rooms: Optional[int] = None
    number_of_bathrooms: Optional[int] = None
    floor: Optional[int] = None
    has_parking: bool = False
    has_elevator: bool = False
    
    # Financial
    price: float
    deposit: Optional[float] = None
    monthly_charges: Optional[float] = None

# Schema for creating a property
class PropertyCreate(PropertyBase):
    owner_id: int

# Schema for updating a property
class PropertyUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    type: Optional[PropertyType] = None
    status: Optional[PropertyStatus] = None
    address: Optional[constr(min_length=1)] = None
    city: Optional[constr(min_length=1)] = None
    postal_code: Optional[constr(min_length=1)] = None
    country: Optional[constr(min_length=1)] = None
    surface_area: Optional[float] = None
    number_of_rooms: Optional[int] = None
    number_of_bathrooms: Optional[int] = None
    floor: Optional[int] = None
    has_parking: Optional[bool] = None
    has_elevator: Optional[bool] = None
    price: Optional[float] = None
    deposit: Optional[float] = None
    monthly_charges: Optional[float] = None

# Schema for property in response
class Property(PropertyBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True 