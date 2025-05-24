import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentType, PaymentStatus
from app.models.contract import Contract, ContractType, ContractStatus
from app.models.property import Property, PropertyType, PropertyStatus
from app.models.user import User, UserRole
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.schemas.contract import ContractCreate
from app.schemas.property import PropertyCreate
from app.schemas.user import UserCreate
from app.services.payment import PaymentService
from app.services.contract import ContractService
from app.services.property import PropertyService
from app.services.auth import AuthService

@pytest.fixture
def owner(db: Session):
    """Crée un propriétaire pour les tests."""
    user_data = UserCreate(
        email="owner@example.com",
        password="password123",
        full_name="Property Owner",
        role=UserRole.OWNER
    )
    return AuthService.create_user(db, user_data)

@pytest.fixture
def tenant(db: Session):
    """Crée un locataire pour les tests."""
    user_data = UserCreate(
        email="tenant@example.com",
        password="password123",
        full_name="Property Tenant",
        role=UserRole.TENANT
    )
    return AuthService.create_user(db, user_data)

@pytest.fixture
def property(db: Session, owner: User):
    """Crée une propriété pour les tests."""
    property_data = PropertyCreate(
        title="Test Property",
        description="A test property",
        type=PropertyType.APARTMENT,
        status=PropertyStatus.AVAILABLE,
        address="123 Test Street",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        surface_area=100.0,
        number_of_rooms=3,
        number_of_bathrooms=2,
        floor=1,
        parking=True,
        elevator=True,
        price=1000.0,
        deposit=1000.0,
        monthly_charges=100.0,
        owner_id=owner.id
    )
    return PropertyService.create_property(db, property_data)

@pytest.fixture
def contract(db: Session, owner: User, tenant: User, property: Property):
    """Crée un contrat pour les tests."""
    contract_data = ContractCreate(
        type=ContractType.RENTAL,
        status=ContractStatus.ACTIVE,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=365),
        rent_amount=1000.0,
        deposit_amount=1000.0,
        payment_day=1,
        terms="Standard rental terms",
        notes="No special notes",
        property_id=property.id,
        tenant_id=tenant.id
    )
    return ContractService.create_contract(db, contract_data)

def test_create_payment(db: Session, contract: Contract):
    """Test la création d'un paiement."""
    payment_data = PaymentCreate(
        amount=1000.0,
        type=PaymentType.RENT,
        status=PaymentStatus.PENDING,
        due_date=datetime.utcnow() + timedelta(days=30),
        reference="RENT-001",
        notes="Monthly rent payment",
        contract_id=contract.id
    )
    
    payment = PaymentService.create_payment(db, payment_data)
    assert payment is not None
    assert payment.amount == payment_data.amount
    assert payment.type == payment_data.type
    assert payment.status == payment_data.status
    assert payment.contract_id == contract.id

def test_get_payment(db: Session, contract: Contract):
    """Test la récupération d'un paiement."""
    # Créer un paiement de test
    payment_data = PaymentCreate(
        amount=1000.0,
        type=PaymentType.RENT,
        status=PaymentStatus.PENDING,
        due_date=datetime.utcnow() + timedelta(days=30),
        reference="RENT-001",
        notes="Monthly rent payment",
        contract_id=contract.id
    )
    created_payment = PaymentService.create_payment(db, payment_data)
    
    # Récupérer le paiement
    payment = PaymentService.get_payment(db, created_payment.id)
    assert payment is not None
    assert payment.id == created_payment.id
    assert payment.amount == payment_data.amount

def test_get_payments(db: Session, contract: Contract):
    """Test la récupération de plusieurs paiements avec filtres."""
    # Créer plusieurs paiements
    payments_data = [
        PaymentCreate(
            amount=1000.0,
            type=PaymentType.RENT,
            status=PaymentStatus.PENDING,
            due_date=datetime.utcnow() + timedelta(days=30 * (i + 1)),
            reference=f"RENT-00{i+1}",
            notes=f"Monthly rent payment {i+1}",
            contract_id=contract.id
        ) for i in range(3)
    ]
    
    for data in payments_data:
        PaymentService.create_payment(db, data)
    
    # Tester la récupération sans filtres
    payments = PaymentService.get_payments(db)
    assert len(payments) == 3
    
    # Tester la récupération avec filtre de type
    payments = PaymentService.get_payments(db, type=PaymentType.RENT)
    assert len(payments) == 3
    
    # Tester la récupération avec filtre de statut
    payments = PaymentService.get_payments(db, status=PaymentStatus.PENDING)
    assert len(payments) == 3

def test_update_payment(db: Session, contract: Contract):
    """Test la mise à jour d'un paiement."""
    # Créer un paiement de test
    payment_data = PaymentCreate(
        amount=1000.0,
        type=PaymentType.RENT,
        status=PaymentStatus.PENDING,
        due_date=datetime.utcnow() + timedelta(days=30),
        reference="RENT-001",
        notes="Monthly rent payment",
        contract_id=contract.id
    )
    created_payment = PaymentService.create_payment(db, payment_data)
    
    # Mettre à jour le paiement
    update_data = PaymentUpdate(
        amount=1200.0,
        notes="Updated payment notes",
        status=PaymentStatus.PAID,
        paid_date=datetime.utcnow()
    )
    updated_payment = PaymentService.update_payment(db, created_payment.id, update_data)
    
    assert updated_payment is not None
    assert updated_payment.amount == update_data.amount
    assert updated_payment.notes == update_data.notes
    assert updated_payment.status == update_data.status
    assert updated_payment.paid_date == update_data.paid_date

def test_mark_payment_as_paid(db: Session, contract: Contract):
    """Test le marquage d'un paiement comme payé."""
    # Créer un paiement de test
    payment_data = PaymentCreate(
        amount=1000.0,
        type=PaymentType.RENT,
        status=PaymentStatus.PENDING,
        due_date=datetime.utcnow() + timedelta(days=30),
        reference="RENT-001",
        notes="Monthly rent payment",
        contract_id=contract.id
    )
    created_payment = PaymentService.create_payment(db, payment_data)
    
    # Marquer le paiement comme payé
    paid_payment = PaymentService.mark_payment_as_paid(db, created_payment.id)
    
    assert paid_payment is not None
    assert paid_payment.status == PaymentStatus.PAID
    assert paid_payment.paid_date is not None

def test_check_overdue_payments(db: Session, contract: Contract):
    """Test la vérification des paiements en retard."""
    # Créer un paiement en retard
    payment_data = PaymentCreate(
        amount=1000.0,
        type=PaymentType.RENT,
        status=PaymentStatus.PENDING,
        due_date=datetime.utcnow() - timedelta(days=1),
        reference="RENT-001",
        notes="Overdue payment",
        contract_id=contract.id
    )
    PaymentService.create_payment(db, payment_data)
    
    # Vérifier les paiements en retard
    overdue_payments = PaymentService.check_overdue_payments(db)
    assert len(overdue_payments) == 1
    assert overdue_payments[0].status == PaymentStatus.PENDING

def test_generate_rent_payments(db: Session, contract: Contract):
    """Test la génération des paiements de loyer."""
    # Générer les paiements de loyer
    payments = PaymentService.generate_rent_payments(db, contract.id)
    
    # Vérifier que les paiements ont été générés
    assert len(payments) > 0
    for payment in payments:
        assert payment.type == PaymentType.RENT
        assert payment.status == PaymentStatus.PENDING
        assert payment.amount == contract.rent_amount 