from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from services.auth import AuthService
from services.contract import ContractService
from schemas.contract import Contract, ContractCreate, ContractUpdate
from models.user import User, UserRole
from models.contract import ContractStatus

router = APIRouter()
contract_service = ContractService()

@router.get("/", response_model=List[Contract])
async def read_contracts(
    skip: int = 0,
    limit: int = 100,
    property_id: Optional[int] = None,
    tenant_id: Optional[int] = None,
    status: Optional[ContractStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Filter by tenant_id if user is a tenant
    if current_user.role == UserRole.TENANT:
        tenant_id = current_user.id
    
    return contract_service.get_contracts(
        db=db,
        skip=skip,
        limit=limit,
        property_id=property_id,
        tenant_id=tenant_id,
        status=status
    )

@router.post("/", response_model=Contract, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_data: ContractCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can create contracts
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return contract_service.create_contract(contract_data, db)

@router.get("/{contract_id}", response_model=Contract)
async def read_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    contract = contract_service.get_contract(contract_id, db)
    
    # Check if user has access to this contract
    if current_user.role == UserRole.TENANT and contract.tenant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return contract

@router.put("/{contract_id}", response_model=Contract)
async def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can update contracts
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    updated_contract = contract_service.update_contract(db, contract_id, contract_data)
    if not updated_contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    return updated_contract

@router.post("/{contract_id}/terminate", response_model=Contract)
async def terminate_contract(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can terminate contracts
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return contract_service.terminate_contract(contract_id, db)

@router.get("/expiring", response_model=List[Contract])
async def get_expiring_contracts(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Only admin and agent can view expiring contracts
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return contract_service.check_contract_expiration(db) 