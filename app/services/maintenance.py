from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.maintenance import MaintenanceRequest, MaintenanceStatus
from app.models.property import Property
from app.schemas.maintenance import MaintenanceRequestCreate, MaintenanceRequestUpdate
from app.models.user import User

class MaintenanceService:
    @staticmethod
    def get_maintenance_request(request_id: int, db: Session) -> MaintenanceRequest:
        request = db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request_id).first()
        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maintenance request not found"
            )
        return request

    @staticmethod
    def get_maintenance_requests(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        property_id: Optional[int] = None,
        status: Optional[MaintenanceStatus] = None,
        type: Optional[str] = None,
        priority: Optional[int] = None
    ) -> List[MaintenanceRequest]:
        query = db.query(MaintenanceRequest)
        
        if property_id:
            query = query.filter(MaintenanceRequest.property_id == property_id)
        if status:
            query = query.filter(MaintenanceRequest.status == status)
        if type:
            query = query.filter(MaintenanceRequest.type == type)
        if priority:
            query = query.filter(MaintenanceRequest.priority == priority)
            
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_maintenance_request(request_data: MaintenanceRequestCreate, db: Session) -> MaintenanceRequest:
        # Verify property exists
        property = db.query(Property).filter(Property.id == request_data.property_id).first()
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        
        # Verify requester exists
        requester = db.query(User).filter(User.id == request_data.requested_by_id).first()
        if not requester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requester not found"
            )
        
        # Verify assignee exists if provided
        if request_data.assigned_to_id:
            assignee = db.query(User).filter(User.id == request_data.assigned_to_id).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found"
                )
        
        # Create maintenance request
        db_request = MaintenanceRequest(**request_data.dict())
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        return db_request

    @staticmethod
    def update_maintenance_request(request_id: int, request_data: MaintenanceRequestUpdate, db: Session) -> MaintenanceRequest:
        request = MaintenanceService.get_maintenance_request(request_id, db)
        
        # Update request fields
        for field, value in request_data.dict(exclude_unset=True).items():
            setattr(request, field, value)
        
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def complete_maintenance_request(request_id: int, cost: float, db: Session) -> MaintenanceRequest:
        request = MaintenanceService.get_maintenance_request(request_id, db)
        
        if request.status == MaintenanceStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maintenance request is already completed"
            )
        
        request.status = MaintenanceStatus.COMPLETED
        request.completion_date = date.today()
        request.cost = cost
        
        db.commit()
        db.refresh(request)
        return request

    @staticmethod
    def get_high_priority_requests(db: Session) -> List[MaintenanceRequest]:
        """Get all high priority (4-5) maintenance requests"""
        return db.query(MaintenanceRequest).filter(
            MaintenanceRequest.priority >= 4,
            MaintenanceRequest.status != MaintenanceStatus.COMPLETED
        ).all()

    @staticmethod
    def get_emergency_requests(db: Session) -> List[MaintenanceRequest]:
        """Get all emergency maintenance requests"""
        return db.query(MaintenanceRequest).filter(
            MaintenanceRequest.type == "emergency",
            MaintenanceRequest.status != MaintenanceStatus.COMPLETED
        ).all() 