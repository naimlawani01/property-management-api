from sqlalchemy import Boolean, Column, Integer, String, Float, Enum, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
import enum

from core.database import Base

class PaymentType(str, enum.Enum):
    RENT = "rent"
    DEPOSIT = "deposit"
    CHARGES = "charges"
    MAINTENANCE = "maintenance"
    OTHER = "other"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(PaymentType), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Payment details
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date)
    reference = Column(String)
    notes = Column(Text)
    
    # Relations
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    contract = relationship("Contract", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment {self.id} - {self.type}>" 