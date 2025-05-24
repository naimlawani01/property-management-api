from typing import List, Optional
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.payment import Payment, PaymentStatus
from models.contract import Contract, ContractStatus
from schemas.payment import PaymentCreate, PaymentUpdate

class PaymentService:
    @staticmethod
    def get_payment(payment_id: int, db: Session) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment

    @staticmethod
    def get_payments(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        contract_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None,
        type: Optional[str] = None
    ) -> List[Payment]:
        query = db.query(Payment)
        
        if contract_id:
            query = query.filter(Payment.contract_id == contract_id)
        if status:
            query = query.filter(Payment.status == status)
        if type:
            query = query.filter(Payment.type == type)
            
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create_payment(payment_data: PaymentCreate, db: Session) -> Payment:
        # Verify contract exists and is active
        contract = db.query(Contract).filter(Contract.id == payment_data.contract_id).first()
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )
        if contract.status != ContractStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract is not active"
            )
        
        # Create payment
        db_payment = Payment(**payment_data.dict())
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment

    @staticmethod
    def update_payment(payment_id: int, payment_data: PaymentUpdate, db: Session) -> Payment:
        payment = PaymentService.get_payment(payment_id, db)
        
        # Update payment fields
        for field, value in payment_data.dict(exclude_unset=True).items():
            setattr(payment, field, value)
        
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def mark_payment_as_paid(payment_id: int, db: Session) -> Payment:
        payment = PaymentService.get_payment(payment_id, db)
        
        if payment.status == PaymentStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is already marked as paid"
            )
        
        payment.status = PaymentStatus.PAID
        payment.paid_date = date.today()
        
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def check_overdue_payments(db: Session) -> List[Payment]:
        """Check for payments that are overdue"""
        today = date.today()
        
        return db.query(Payment).filter(
            Payment.status == PaymentStatus.PENDING,
            Payment.due_date < today
        ).all()

    @staticmethod
    def generate_rent_payments(contract_id: int, db: Session) -> List[Payment]:
        """Generate rent payments for a contract"""
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contract not found"
            )
        
        if not contract.rent_amount or not contract.payment_day:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contract must have rent amount and payment day set"
            )
        
        # Generate payments for the remaining months of the contract
        payments = []
        current_date = date.today()
        end_date = contract.end_date or date(current_date.year + 1, current_date.month, current_date.day)
        
        while current_date <= end_date:
            payment = Payment(
                contract_id=contract_id,
                amount=contract.rent_amount,
                type="rent",
                status=PaymentStatus.PENDING,
                due_date=date(current_date.year, current_date.month, contract.payment_day)
            )
            payments.append(payment)
            current_date = date(current_date.year, current_date.month + 1, current_date.day)
        
        db.add_all(payments)
        db.commit()
        return payments 