from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import AuthService
from app.services.property import PropertyService
from app.schemas.property import Property, PropertyCreate, PropertyUpdate
from app.models.user import User, UserRole
from app.models.property import PropertyStatus
from app.models.contract import Contract, ContractStatus

router = APIRouter()
property_service = PropertyService()

@router.get("/", response_model=List[Property])
async def read_properties(
    skip: int = 0,
    limit: int = 100,
    owner_id: Optional[int] = None,
    status: Optional[PropertyStatus] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    return property_service.get_properties(
        db=db,
        skip=skip,
        limit=limit,
        owner_id=owner_id,
        status=status,
        type=type,
        user_role=current_user.role,
        user_id=current_user.id
    )

@router.post("/", response_model=Property, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can create properties
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return property_service.create_property(property_data, db)

@router.get("/{property_id}", response_model=Property)
async def read_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    property = property_service.get_property(
        property_id=property_id,
        db=db,
        user_role=current_user.role,
        user_id=current_user.id
    )
    if not property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    return property

@router.put("/{property_id}", response_model=Property)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can update properties
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    updated_property = property_service.update_property(db, property_id, property_data)
    if not updated_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )
    return updated_property

@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin can delete properties
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    if not property_service.delete_property(db, property_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found"
        )

@router.patch("/{property_id}/status", response_model=Property)
async def update_property_status(
    property_id: int,
    status: PropertyStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can update property status
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return property_service.update_property_status(property_id, status, db) 