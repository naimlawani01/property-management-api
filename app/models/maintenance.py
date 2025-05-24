from sqlalchemy import Boolean, Column, Integer, String, Float, Enum, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base

class MaintenanceType(str, enum.Enum):
    REPAIR = "repair"
    RENOVATION = "renovation"
    INSPECTION = "inspection"
    EMERGENCY = "emergency"
    OTHER = "other"

class MaintenanceStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(Enum(MaintenanceType), nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING)
    
    # Maintenance details
    request_date = Column(Date, nullable=False)
    completion_date = Column(Date)
    cost = Column(Float)
    priority = Column(Integer, default=1)  # 1-5, 5 being highest
    notes = Column(Text)
    
    # Relations
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    property = relationship("Property", back_populates="maintenance_requests")
    
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    def __repr__(self):
        return f"<MaintenanceRequest {self.id} - {self.title}>" 