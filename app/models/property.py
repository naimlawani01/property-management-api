from sqlalchemy import Boolean, Column, Integer, String, Float, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base

class PropertyType(str, enum.Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    OFFICE = "office"
    COMMERCIAL = "commercial"

class PropertyStatus(str, enum.Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    SOLD = "sold"
    MAINTENANCE = "maintenance"

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    type = Column(Enum(PropertyType), nullable=False)
    status = Column(Enum(PropertyStatus), default=PropertyStatus.AVAILABLE)
    
    # Location
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    
    # Characteristics
    surface_area = Column(Float, nullable=False)  # in square meters
    number_of_rooms = Column(Integer)
    number_of_bathrooms = Column(Integer)
    floor = Column(Integer)
    has_parking = Column(Boolean, default=False)
    has_elevator = Column(Boolean, default=False)
    
    # Financial
    price = Column(Float, nullable=False)
    deposit = Column(Float)
    monthly_charges = Column(Float)
    
    # Relations
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="properties")
    contracts = relationship("Contract", back_populates="property")
    maintenance_requests = relationship("MaintenanceRequest", back_populates="property")
    
    def __repr__(self):
        return f"<Property {self.title}>" 