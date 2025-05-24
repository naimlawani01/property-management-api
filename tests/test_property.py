import pytest
from sqlalchemy.orm import Session
from app.models.property import Property, PropertyType, PropertyStatus
from app.models.user import User, UserRole
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.services.property import PropertyService
from app.services.auth import AuthService
from app.schemas.user import UserCreate

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

def test_create_property(db: Session, owner: User):
    """Test la création d'une propriété."""
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
    
    property = PropertyService.create_property(db, property_data)
    assert property is not None
    assert property.title == property_data.title
    assert property.owner_id == owner.id
    assert property.type == property_data.type
    assert property.status == property_data.status

def test_get_property(db: Session, owner: User):
    """Test la récupération d'une propriété."""
    # Créer une propriété de test
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
    created_property = PropertyService.create_property(db, property_data)
    
    # Récupérer la propriété
    property = PropertyService.get_property(db, created_property.id)
    assert property is not None
    assert property.id == created_property.id
    assert property.title == property_data.title

def test_get_properties(db: Session, owner: User):
    """Test la récupération de plusieurs propriétés avec filtres."""
    # Créer plusieurs propriétés
    properties_data = [
        PropertyCreate(
            title=f"Test Property {i}",
            description=f"A test property {i}",
            type=PropertyType.APARTMENT,
            status=PropertyStatus.AVAILABLE,
            address=f"{i}23 Test Street",
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
        ) for i in range(3)
    ]
    
    for data in properties_data:
        PropertyService.create_property(db, data)
    
    # Tester la récupération sans filtres
    properties = PropertyService.get_properties(db)
    assert len(properties) == 3
    
    # Tester la récupération avec filtre de type
    properties = PropertyService.get_properties(db, type=PropertyType.APARTMENT)
    assert len(properties) == 3
    
    # Tester la récupération avec filtre de statut
    properties = PropertyService.get_properties(db, status=PropertyStatus.AVAILABLE)
    assert len(properties) == 3

def test_update_property(db: Session, owner: User):
    """Test la mise à jour d'une propriété."""
    # Créer une propriété de test
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
    created_property = PropertyService.create_property(db, property_data)
    
    # Mettre à jour la propriété
    update_data = PropertyUpdate(
        title="Updated Property",
        price=1200.0,
        status=PropertyStatus.RENTED
    )
    updated_property = PropertyService.update_property(db, created_property.id, update_data)
    
    assert updated_property is not None
    assert updated_property.title == update_data.title
    assert updated_property.price == update_data.price
    assert updated_property.status == update_data.status

def test_delete_property(db: Session, owner: User):
    """Test la suppression d'une propriété."""
    # Créer une propriété de test
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
    created_property = PropertyService.create_property(db, property_data)
    
    # Supprimer la propriété
    PropertyService.delete_property(db, created_property.id)
    
    # Vérifier que la propriété n'existe plus
    property = PropertyService.get_property(db, created_property.id)
    assert property is None

def test_update_property_status(db: Session, owner: User):
    """Test la mise à jour du statut d'une propriété."""
    # Créer une propriété de test
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
    created_property = PropertyService.create_property(db, property_data)
    
    # Mettre à jour le statut
    updated_property = PropertyService.update_property_status(
        db, created_property.id, PropertyStatus.RENTED
    )
    
    assert updated_property is not None
    assert updated_property.status == PropertyStatus.RENTED 