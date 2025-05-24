from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import AuthService
from app.services.maintenance import MaintenanceService
from app.schemas.maintenance import (
    MaintenanceRequest,
    MaintenanceRequestCreate,
    MaintenanceRequestUpdate
)
from app.models.user import User, UserRole
from app.models.maintenance import MaintenanceStatus

router = APIRouter()
maintenance_service = MaintenanceService()

@router.get("/", response_model=List[MaintenanceRequest])
async def read_maintenance_requests(
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[int] = None,
    status: Optional[MaintenanceStatus] = None,
    type: Optional[str] = None,
    priority: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # If user is a tenant, only show their requests
    if current_user.role == UserRole.TENANT:
        # Get all properties for this tenant
        tenant_properties = [c.property_id for c in current_user.tenant_contracts]
        if not tenant_properties:
            return []
        return maintenance_service.get_maintenance_requests(
            db=db,
            skip=skip,
            limit=limit,
            property_id=property_id if property_id in tenant_properties else None,
            status=status,
            type=type,
            priority=priority
        )
    
    return maintenance_service.get_maintenance_requests(
        db=db,
        skip=skip,
        limit=limit,
        property_id=property_id,
        status=status,
        type=type,
        priority=priority
    )

@router.post("/", response_model=MaintenanceRequest, status_code=status.HTTP_201_CREATED)
async def create_maintenance_request(
    request_data: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Set the requester to the current user if not specified
    if not request_data.requested_by_id:
        request_data.requested_by_id = current_user.id
    
    return maintenance_service.create_maintenance_request(request_data, db)

@router.get("/{request_id}", response_model=MaintenanceRequest)
async def read_maintenance_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    request = maintenance_service.get_maintenance_request(request_id, db)
    
    # Check if user has access to this request
    if current_user.role == UserRole.TENANT:
        if request.property_id not in [c.property_id for c in current_user.tenant_contracts]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return request

@router.put("/{request_id}", response_model=MaintenanceRequest)
async def update_maintenance_request(
    request_id: int,
    request_data: MaintenanceRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can update maintenance requests
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    updated_request = maintenance_service.update_maintenance_request(request_id, request_data, db)
    if not updated_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance request not found"
        )
    return updated_request

@router.post("/{request_id}/complete", response_model=MaintenanceRequest)
async def complete_maintenance_request(
    request_id: int,
    cost: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can complete maintenance requests
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return MaintenanceService.complete_maintenance_request(request_id, cost, db)

@router.get("/high-priority", response_model=List[MaintenanceRequest])
async def get_high_priority_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can view high priority requests
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return MaintenanceService.get_high_priority_requests(db)

@router.get("/emergency", response_model=List[MaintenanceRequest])
async def get_emergency_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can view emergency requests
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return MaintenanceService.get_emergency_requests(db) 