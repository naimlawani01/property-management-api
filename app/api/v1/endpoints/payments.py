from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import AuthService
from app.services.payment import PaymentService
from app.schemas.payment import Payment, PaymentCreate, PaymentUpdate
from app.models.user import User, UserRole
from app.models.payment import PaymentStatus

router = APIRouter()        

@router.get("/", response_model=List[Payment])
async def read_payments(
    skip: int = 0,
    limit: int = 100,
    contract_id: Optional[int] = None,
    status: Optional[PaymentStatus] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # If user is a tenant, only show their payments
    if current_user.role == UserRole.TENANT:
        # Get all contracts for this tenant
        tenant_contracts = [c.id for c in current_user.tenant_contracts]
        if not tenant_contracts:
            return []
        return PaymentService.get_payments(
            db=db,
            skip=skip,
            limit=limit,
            contract_id=contract_id if contract_id in tenant_contracts else None,
            status=status,
            type=type
        )
    
    return PaymentService.get_payments(
        db=db,
        skip=skip,
        limit=limit,
        contract_id=contract_id,
        status=status,
        type=type
    )

@router.post("/", response_model=Payment, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can create payments
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return PaymentService.create_payment(payment_data, db)

@router.get("/{payment_id}", response_model=Payment)
async def read_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    payment = PaymentService.get_payment(payment_id, db)
    
    # Check if user has access to this payment
    if current_user.role == UserRole.TENANT:
        if payment.contract.tenant_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return payment

@router.put("/{payment_id}", response_model=Payment)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can update payments
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    updated_payment = PaymentService.update_payment(payment_id, payment_data, db)
    if not updated_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return updated_payment

@router.post("/{payment_id}/mark-paid", response_model=Payment)
async def mark_payment_as_paid(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can mark payments as paid
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return PaymentService.mark_payment_as_paid(payment_id, db)

@router.get("/overdue", response_model=List[Payment])
async def get_overdue_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can view overdue payments
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return PaymentService.check_overdue_payments(db)

@router.post("/contract/{contract_id}/generate-rent", response_model=List[Payment])
async def generate_rent_payments(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can generate rent payments
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return PaymentService.generate_rent_payments(contract_id, db) 