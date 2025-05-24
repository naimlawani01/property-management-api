from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.contract import Contract, ContractStatus
from app.models.property import Property, PropertyStatus
from app.schemas.contract import ContractCreate, ContractUpdate
from app.models.user import User

class ContractService:
    @staticmethod
    def get_contract(contract_id: int, db: Session) -> Contract:
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )
        return contract

    @staticmethod
    def get_contracts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        property_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        status: Optional[ContractStatus] = None
    ) -> List[Contract]:
        query = db.query(Contract)
        
        if property_id:
            query = query.filter(Contract.property_id == property_id)
        if tenant_id:
            query = query.filter(Contract.tenant_id == tenant_id)
        if status:
            query = query.filter(Contract.status == status)
            
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_contract(contract_data: ContractCreate, db: Session) -> Contract:
        # Verify property exists and is available
        property = db.query(Property).filter(Property.id == contract_data.property_id).first()
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        if property.status != PropertyStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Property is not available"
            )
        
        # Verify tenant exists
        tenant = db.query(User).filter(User.id == contract_data.tenant_id).first()
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        # Create contract
        db_contract = Contract(**contract_data.dict())
        db.add(db_contract)
        
        # Update property status
        property.status = PropertyStatus.RENTED
        
        db.commit()
        db.refresh(db_contract)
        return db_contract

    @staticmethod
    def update_contract(contract_id: int, contract_data: ContractUpdate, db: Session) -> Contract:
        contract = ContractService.get_contract(contract_id, db)
        
        # Update contract fields
        for field, value in contract_data.dict(exclude_unset=True).items():
            setattr(contract, field, value)
        
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def terminate_contract(contract_id: int, db: Session) -> Contract:
        contract = ContractService.get_contract(contract_id, db)
        
        if contract.status == ContractStatus.TERMINATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract is already terminated"
            )
        
        # Update contract status
        contract.status = ContractStatus.TERMINATED
        contract.end_date = date.today()
        
        # Update property status
        property = contract.property
        property.status = PropertyStatus.AVAILABLE
        
        db.commit()
        db.refresh(contract)
        return contract

    @staticmethod
    def check_contract_expiration(db: Session) -> List[Contract]:
        """Check for contracts that are about to expire (within 30 days)"""
        today = date.today()
        thirty_days_later = date(today.year, today.month + 1, today.day)
        
        return db.query(Contract).filter(
            Contract.status == ContractStatus.ACTIVE,
            Contract.end_date <= thirty_days_later,
            Contract.end_date >= today
        ).all() 