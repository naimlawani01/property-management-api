import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models.contract import ContractType, ContractStatus
from app.models.property import PropertyType, PropertyStatus
from app.models.user import UserRole

@pytest.fixture
def owner_headers(client: TestClient):
    """Crée un propriétaire et retourne les headers d'authentification."""
    user_data = {
        "email": "owner@example.com",
        "password": "ownerpassword123",
        "full_name": "Property Owner",
        "role": UserRole.OWNER
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/api/v1/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def tenant_headers(client: TestClient):
    """Crée un locataire et retourne les headers d'authentification."""
    user_data = {
        "email": "tenant@example.com",
        "password": "tenantpassword123",
        "full_name": "Property Tenant",
        "role": UserRole.TENANT
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/api/v1/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def property_id(client: TestClient, owner_headers):
    """Crée une propriété et retourne son ID."""
    property_data = {
        "title": "Test Property",
        "description": "A test property",
        "type": PropertyType.APARTMENT,
        "status": PropertyStatus.AVAILABLE,
        "address": "123 Test Street",
        "city": "Test City",
        "postal_code": "12345",
        "country": "Test Country",
        "surface_area": 100.0,
        "number_of_rooms": 3,
        "number_of_bathrooms": 2,
        "floor": 1,
        "parking": True,
        "elevator": True,
        "price": 1000.0,
        "deposit": 1000.0,
        "monthly_charges": 100.0
    }
    response = client.post("/api/v1/properties", json=property_data, headers=owner_headers)
    return response.json()["id"]

def test_create_contract(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la création d'un contrat."""
    contract_data = {
        "type": ContractType.RENTAL,
        "status": ContractStatus.ACTIVE,
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "rent_amount": 1000.0,
        "deposit_amount": 1000.0,
        "payment_day": 1,
        "terms": "Standard rental terms",
        "notes": "No special notes",
        "property_id": property_id
    }
    
    response = client.post("/api/v1/contracts", json=contract_data, headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == contract_data["type"]
    assert data["status"] == contract_data["status"]
    assert data["property_id"] == property_id
    
    # Vérifier que le statut de la propriété a été mis à jour
    property_response = client.get(f"/api/v1/properties/{property_id}", headers=owner_headers)
    assert property_response.json()["status"] == PropertyStatus.RENTED

def test_get_contract(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la récupération d'un contrat."""
    # Créer un contrat
    contract_data = {
        "type": ContractType.RENTAL,
        "status": ContractStatus.ACTIVE,
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "rent_amount": 1000.0,
        "deposit_amount": 1000.0,
        "payment_day": 1,
        "terms": "Standard rental terms",
        "notes": "No special notes",
        "property_id": property_id
    }
    create_response = client.post("/api/v1/contracts", json=contract_data, headers=owner_headers)
    contract_id = create_response.json()["id"]
    
    # Récupérer le contrat
    response = client.get(f"/api/v1/contracts/{contract_id}", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contract_id
    assert data["type"] == contract_data["type"]

def test_get_contracts(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la récupération de plusieurs contrats avec filtres."""
    # Créer plusieurs contrats
    contracts_data = [
        {
            "type": ContractType.RENTAL,
            "status": ContractStatus.ACTIVE,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            "rent_amount": 1000.0,
            "deposit_amount": 1000.0,
            "payment_day": 1,
            "terms": f"Contract {i} terms",
            "notes": f"Contract {i} notes",
            "property_id": property_id
        } for i in range(3)
    ]
    
    for data in contracts_data:
        client.post("/api/v1/contracts", json=data, headers=owner_headers)
    
    # Tester la récupération sans filtres
    response = client.get("/api/v1/contracts", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Tester la récupération avec filtre de type
    response = client.get("/api/v1/contracts?type=RENTAL", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Tester la récupération avec filtre de statut
    response = client.get("/api/v1/contracts?status=ACTIVE", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_update_contract(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la mise à jour d'un contrat."""
    # Créer un contrat
    contract_data = {
        "type": ContractType.RENTAL,
        "status": ContractStatus.ACTIVE,
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "rent_amount": 1000.0,
        "deposit_amount": 1000.0,
        "payment_day": 1,
        "terms": "Standard rental terms",
        "notes": "No special notes",
        "property_id": property_id
    }
    create_response = client.post("/api/v1/contracts", json=contract_data, headers=owner_headers)
    contract_id = create_response.json()["id"]
    
    # Mettre à jour le contrat
    update_data = {
        "rent_amount": 1200.0,
        "terms": "Updated terms",
        "status": ContractStatus.TERMINATED
    }
    response = client.put(f"/api/v1/contracts/{contract_id}", json=update_data, headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["rent_amount"] == update_data["rent_amount"]
    assert data["terms"] == update_data["terms"]
    assert data["status"] == update_data["status"]
    
    # Vérifier que le statut de la propriété a été mis à jour
    property_response = client.get(f"/api/v1/properties/{property_id}", headers=owner_headers)
    assert property_response.json()["status"] == PropertyStatus.AVAILABLE

def test_terminate_contract(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la résiliation d'un contrat."""
    # Créer un contrat
    contract_data = {
        "type": ContractType.RENTAL,
        "status": ContractStatus.ACTIVE,
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "rent_amount": 1000.0,
        "deposit_amount": 1000.0,
        "payment_day": 1,
        "terms": "Standard rental terms",
        "notes": "No special notes",
        "property_id": property_id
    }
    create_response = client.post("/api/v1/contracts", json=contract_data, headers=owner_headers)
    contract_id = create_response.json()["id"]
    
    # Résilier le contrat
    response = client.post(f"/api/v1/contracts/{contract_id}/terminate", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == ContractStatus.TERMINATED
    
    # Vérifier que le statut de la propriété a été mis à jour
    property_response = client.get(f"/api/v1/properties/{property_id}", headers=owner_headers)
    assert property_response.json()["status"] == PropertyStatus.AVAILABLE 