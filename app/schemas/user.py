from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from app.models.user import UserRole

# Base User Schema
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole

# Schema for creating a user
class UserCreate(UserBase):
    password: constr(min_length=8)

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[constr(min_length=8)] = None
    is_active: Optional[bool] = None

# Schema for user in response
class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

# Schema for user with token
class UserWithToken(User):
    access_token: str
    token_type: str = "bearer" 