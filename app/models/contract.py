from sqlalchemy import Boolean, Column, Integer, String, Float, Enum, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
import enum

from core.database import Base

class ContractType(str, enum.Enum):
    RENTAL = "rental"
    SALE = "sale"

class ContractStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    PENDING = "pending"

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ContractType), nullable=False)
    status = Column(Enum(ContractStatus), default=ContractStatus.PENDING)
    
    # Contract details
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    rent_amount = Column(Float)
    deposit_amount = Column(Float)
    payment_day = Column(Integer)  # Day of the month for rent payment
    
    # Additional information
    terms = Column(Text)
    notes = Column(Text)
    
    # Relations
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    property = relationship("Property", back_populates="contracts")
    
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tenant = relationship("User", back_populates="tenant_contracts")
    
    payments = relationship("Payment", back_populates="contract")
    
    def __repr__(self):
        return f"<Contract {self.id} - {self.type}>" 