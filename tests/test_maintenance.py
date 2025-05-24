import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.maintenance import MaintenanceRequest, MaintenanceType, MaintenanceStatus
from app.models.property import Property, PropertyType, PropertyStatus
from app.models.user import User, UserRole
from app.schemas.maintenance import MaintenanceRequestCreate, MaintenanceRequestUpdate
from app.schemas.property import PropertyCreate
from app.schemas.user import UserCreate
from app.services.maintenance import MaintenanceService
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
def agent(db: Session):
    """Crée un agent pour les tests."""
    user_data = UserCreate(
        email="agent@example.com",
        password="password123",
        full_name="Property Agent",
        role=UserRole.AGENT
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

def test_create_maintenance_request(db: Session, tenant: User, property: Property):
    """Test la création d'une demande de maintenance."""
    request_data = MaintenanceRequestCreate(
        title="Leaking Faucet",
        description="The kitchen faucet is leaking",
        type=MaintenanceType.REPAIR,
        status=MaintenanceStatus.PENDING,
        request_date=datetime.utcnow(),
        priority="HIGH",
        notes="Please fix as soon as possible",
        property_id=property.id,
        requested_by_id=tenant.id
    )
    
    request = MaintenanceService.create_maintenance_request(db, request_data)
    assert request is not None
    assert request.title == request_data.title
    assert request.type == request_data.type
    assert request.status == request_data.status
    assert request.property_id == property.id
    assert request.requested_by_id == tenant.id

def test_get_maintenance_request(db: Session, tenant: User, property: Property):
    """Test la récupération d'une demande de maintenance."""
    # Créer une demande de test
    request_data = MaintenanceRequestCreate(
        title="Leaking Faucet",
        description="The kitchen faucet is leaking",
        type=MaintenanceType.REPAIR,
        status=MaintenanceStatus.PENDING,
        request_date=datetime.utcnow(),
        priority="HIGH",
        notes="Please fix as soon as possible",
        property_id=property.id,
        requested_by_id=tenant.id
    )
    created_request = MaintenanceService.create_maintenance_request(db, request_data)
    
    # Récupérer la demande
    request = MaintenanceService.get_maintenance_request(db, created_request.id)
    assert request is not None
    assert request.id == created_request.id
    assert request.title == request_data.title

def test_get_maintenance_requests(db: Session, tenant: User, property: Property):
    """Test la récupération de plusieurs demandes de maintenance avec filtres."""
    # Créer plusieurs demandes
    requests_data = [
        MaintenanceRequestCreate(
            title=f"Maintenance Request {i}",
            description=f"Description for request {i}",
            type=MaintenanceType.REPAIR,
            status=MaintenanceStatus.PENDING,
            request_date=datetime.utcnow(),
            priority="HIGH",
            notes=f"Notes for request {i}",
            property_id=property.id,
            requested_by_id=tenant.id
        ) for i in range(3)
    ]
    
    for data in requests_data:
        MaintenanceService.create_maintenance_request(db, data)
    
    # Tester la récupération sans filtres
    requests = MaintenanceService.get_maintenance_requests(db)
    assert len(requests) == 3
    
    # Tester la récupération avec filtre de type
    requests = MaintenanceService.get_maintenance_requests(db, type=MaintenanceType.REPAIR)
    assert len(requests) == 3
    
    # Tester la récupération avec filtre de statut
    requests = MaintenanceService.get_maintenance_requests(db, status=MaintenanceStatus.PENDING)
    assert len(requests) == 3

def test_update_maintenance_request(db: Session, tenant: User, agent: User, property: Property):
    """Test la mise à jour d'une demande de maintenance."""
    # Créer une demande de test
    request_data = MaintenanceRequestCreate(
        title="Leaking Faucet",
        description="The kitchen faucet is leaking",
        type=MaintenanceType.REPAIR,
        status=MaintenanceStatus.PENDING,
        request_date=datetime.utcnow(),
        priority="HIGH",
        notes="Please fix as soon as possible",
        property_id=property.id,
        requested_by_id=tenant.id
    )
    created_request = MaintenanceService.create_maintenance_request(db, request_data)
    
    # Mettre à jour la demande
    update_data = MaintenanceRequestUpdate(
        status=MaintenanceStatus.IN_PROGRESS,
        assigned_to_id=agent.id,
        notes="Assigned to agent for repair"
    )
    updated_request = MaintenanceService.update_maintenance_request(db, created_request.id, update_data)
    
    assert updated_request is not None
    assert updated_request.status == update_data.status
    assert updated_request.assigned_to_id == agent.id
    assert updated_request.notes == update_data.notes

def test_complete_maintenance_request(db: Session, tenant: User, agent: User, property: Property):
    """Test la complétion d'une demande de maintenance."""
    # Créer une demande de test
    request_data = MaintenanceRequestCreate(
        title="Leaking Faucet",
        description="The kitchen faucet is leaking",
        type=MaintenanceType.REPAIR,
        status=MaintenanceStatus.IN_PROGRESS,
        request_date=datetime.utcnow(),
        priority="HIGH",
        notes="Please fix as soon as possible",
        property_id=property.id,
        requested_by_id=tenant.id,
        assigned_to_id=agent.id
    )
    created_request = MaintenanceService.create_maintenance_request(db, request_data)
    
    # Compléter la demande
    completed_request = MaintenanceService.complete_maintenance_request(
        db, created_request.id, "Fixed the leaking faucet", 150.0
    )
    
    assert completed_request is not None
    assert completed_request.status == MaintenanceStatus.COMPLETED
    assert completed_request.completion_date is not None
    assert completed_request.cost == 150.0
    assert completed_request.notes == "Fixed the leaking faucet"

def test_get_high_priority_requests(db: Session, tenant: User, property: Property):
    """Test la récupération des demandes de haute priorité."""
    # Créer des demandes avec différentes priorités
    requests_data = [
        MaintenanceRequestCreate(
            title=f"Request {i}",
            description=f"Description {i}",
            type=MaintenanceType.REPAIR,
            status=MaintenanceStatus.PENDING,
            request_date=datetime.utcnow(),
            priority="HIGH" if i < 2 else "LOW",
            notes=f"Notes {i}",
            property_id=property.id,
            requested_by_id=tenant.id
        ) for i in range(3)
    ]
    
    for data in requests_data:
        MaintenanceService.create_maintenance_request(db, data)
    
    # Récupérer les demandes de haute priorité
    high_priority_requests = MaintenanceService.get_high_priority_requests(db)
    assert len(high_priority_requests) == 2
    for request in high_priority_requests:
        assert request.priority == "HIGH"

def test_get_emergency_requests(db: Session, tenant: User, property: Property):
    """Test la récupération des demandes d'urgence."""
    # Créer des demandes avec différents types
    requests_data = [
        MaintenanceRequestCreate(
            title=f"Request {i}",
            description=f"Description {i}",
            type=MaintenanceType.EMERGENCY if i < 2 else MaintenanceType.REPAIR,
            status=MaintenanceStatus.PENDING,
            request_date=datetime.utcnow(),
            priority="HIGH",
            notes=f"Notes {i}",
            property_id=property.id,
            requested_by_id=tenant.id
        ) for i in range(3)
    ]
    
    for data in requests_data:
        MaintenanceService.create_maintenance_request(db, data)
    
    # Récupérer les demandes d'urgence
    emergency_requests = MaintenanceService.get_emergency_requests(db)
    assert len(emergency_requests) == 2
    for request in emergency_requests:
        assert request.type == MaintenanceType.EMERGENCY 