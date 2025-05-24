import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.contract import Contract, ContractType, ContractStatus
from app.models.property import Property, PropertyType, PropertyStatus
from app.models.user import User, UserRole
from app.schemas.contract import ContractCreate, ContractUpdate
from app.schemas.property import PropertyCreate
from app.schemas.user import UserCreate
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

def test_create_contract(db: Session, owner: User, tenant: User, property: Property):
    """Test la création d'un contrat."""
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
    
    contract = ContractService.create_contract(db, contract_data)
    assert contract is not None
    assert contract.type == contract_data.type
    assert contract.status == contract_data.status
    assert contract.property_id == property.id
    assert contract.tenant_id == tenant.id
    
    # Vérifier que le statut de la propriété a été mis à jour
    updated_property = PropertyService.get_property(db, property.id)
    assert updated_property.status == PropertyStatus.RENTED

def test_get_contract(db: Session, owner: User, tenant: User, property: Property):
    """Test la récupération d'un contrat."""
    # Créer un contrat de test
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
    created_contract = ContractService.create_contract(db, contract_data)
    
    # Récupérer le contrat
    contract = ContractService.get_contract(db, created_contract.id)
    assert contract is not None
    assert contract.id == created_contract.id
    assert contract.type == contract_data.type

def test_get_contracts(db: Session, owner: User, tenant: User, property: Property):
    """Test la récupération de plusieurs contrats avec filtres."""
    # Créer plusieurs contrats
    contracts_data = [
        ContractCreate(
            type=ContractType.RENTAL,
            status=ContractStatus.ACTIVE,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=365),
            rent_amount=1000.0,
            deposit_amount=1000.0,
            payment_day=1,
            terms=f"Contract {i} terms",
            notes=f"Contract {i} notes",
            property_id=property.id,
            tenant_id=tenant.id
        ) for i in range(3)
    ]
    
    for data in contracts_data:
        ContractService.create_contract(db, data)
    
    # Tester la récupération sans filtres
    contracts = ContractService.get_contracts(db)
    assert len(contracts) == 3
    
    # Tester la récupération avec filtre de type
    contracts = ContractService.get_contracts(db, type=ContractType.RENTAL)
    assert len(contracts) == 3
    
    # Tester la récupération avec filtre de statut
    contracts = ContractService.get_contracts(db, status=ContractStatus.ACTIVE)
    assert len(contracts) == 3

def test_update_contract(db: Session, owner: User, tenant: User, property: Property):
    """Test la mise à jour d'un contrat."""
    # Créer un contrat de test
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
    created_contract = ContractService.create_contract(db, contract_data)
    
    # Mettre à jour le contrat
    update_data = ContractUpdate(
        rent_amount=1200.0,
        terms="Updated terms",
        status=ContractStatus.TERMINATED
    )
    updated_contract = ContractService.update_contract(db, created_contract.id, update_data)
    
    assert updated_contract is not None
    assert updated_contract.rent_amount == update_data.rent_amount
    assert updated_contract.terms == update_data.terms
    assert updated_contract.status == update_data.status
    
    # Vérifier que le statut de la propriété a été mis à jour
    updated_property = PropertyService.get_property(db, property.id)
    assert updated_property.status == PropertyStatus.AVAILABLE

def test_terminate_contract(db: Session, owner: User, tenant: User, property: Property):
    """Test la résiliation d'un contrat."""
    # Créer un contrat de test
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
    created_contract = ContractService.create_contract(db, contract_data)
    
    # Résilier le contrat
    terminated_contract = ContractService.terminate_contract(db, created_contract.id)
    
    assert terminated_contract is not None
    assert terminated_contract.status == ContractStatus.TERMINATED
    
    # Vérifier que le statut de la propriété a été mis à jour
    updated_property = PropertyService.get_property(db, property.id)
    assert updated_property.status == PropertyStatus.AVAILABLE

def test_check_contract_expiration(db: Session, owner: User, tenant: User, property: Property):
    """Test la vérification des contrats qui expirent bientôt."""
    # Créer un contrat qui expire bientôt
    contract_data = ContractCreate(
        type=ContractType.RENTAL,
        status=ContractStatus.ACTIVE,
        start_date=datetime.utcnow() - timedelta(days=350),
        end_date=datetime.utcnow() + timedelta(days=15),
        rent_amount=1000.0,
        deposit_amount=1000.0,
        payment_day=1,
        terms="Standard rental terms",
        notes="No special notes",
        property_id=property.id,
        tenant_id=tenant.id
    )
    ContractService.create_contract(db, contract_data)
    
    # Vérifier les contrats qui expirent bientôt
    expiring_contracts = ContractService.check_contract_expiration(db)
    assert len(expiring_contracts) == 1
    assert expiring_contracts[0].status == ContractStatus.ACTIVE 