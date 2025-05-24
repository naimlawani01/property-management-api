from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
import enum

from core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    AGENT = "agent"
    OWNER = "owner"
    TENANT = "tenant"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Relations
    properties = relationship("Property", back_populates="owner")
    tenant_contracts = relationship("Contract", back_populates="tenant")
    
    def __repr__(self):
        return f"<User {self.email}>" 