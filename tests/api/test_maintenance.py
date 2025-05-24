import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.models.maintenance import MaintenancePriority, MaintenanceStatus
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

def test_create_maintenance_request(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la création d'une demande de maintenance."""
    maintenance_data = {
        "title": "Broken Window",
        "description": "Window in living room is broken",
        "priority": MaintenancePriority.HIGH,
        "status": MaintenanceStatus.PENDING,
        "property_id": property_id,
        "reported_by": "tenant@example.com"
    }
    
    response = client.post("/api/v1/maintenance", json=maintenance_data, headers=tenant_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == maintenance_data["title"]
    assert data["priority"] == maintenance_data["priority"]
    assert data["status"] == maintenance_data["status"]
    assert data["property_id"] == property_id

def test_get_maintenance_request(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la récupération d'une demande de maintenance."""
    # Créer une demande de maintenance
    maintenance_data = {
        "title": "Broken Window",
        "description": "Window in living room is broken",
        "priority": MaintenancePriority.HIGH,
        "status": MaintenanceStatus.PENDING,
        "property_id": property_id,
        "reported_by": "tenant@example.com"
    }
    create_response = client.post("/api/v1/maintenance", json=maintenance_data, headers=tenant_headers)
    maintenance_id = create_response.json()["id"]
    
    # Récupérer la demande de maintenance
    response = client.get(f"/api/v1/maintenance/{maintenance_id}", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == maintenance_id
    assert data["title"] == maintenance_data["title"]
    assert data["priority"] == maintenance_data["priority"]

def test_get_maintenance_requests(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la récupération de plusieurs demandes de maintenance avec filtres."""
    # Créer plusieurs demandes de maintenance
    maintenance_requests = [
        {
            "title": f"Maintenance Request {i}",
            "description": f"Description for request {i}",
            "priority": MaintenancePriority.HIGH if i == 0 else MaintenancePriority.MEDIUM,
            "status": MaintenanceStatus.PENDING,
            "property_id": property_id,
            "reported_by": "tenant@example.com"
        } for i in range(3)
    ]
    
    for data in maintenance_requests:
        client.post("/api/v1/maintenance", json=data, headers=tenant_headers)
    
    # Tester la récupération sans filtres
    response = client.get("/api/v1/maintenance", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Tester la récupération avec filtre de priorité
    response = client.get("/api/v1/maintenance?priority=HIGH", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
    # Tester la récupération avec filtre de statut
    response = client.get("/api/v1/maintenance?status=PENDING", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_update_maintenance_request(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la mise à jour d'une demande de maintenance."""
    # Créer une demande de maintenance
    maintenance_data = {
        "title": "Broken Window",
        "description": "Window in living room is broken",
        "priority": MaintenancePriority.HIGH,
        "status": MaintenanceStatus.PENDING,
        "property_id": property_id,
        "reported_by": "tenant@example.com"
    }
    create_response = client.post("/api/v1/maintenance", json=maintenance_data, headers=tenant_headers)
    maintenance_id = create_response.json()["id"]
    
    # Mettre à jour la demande de maintenance
    update_data = {
        "title": "Updated Maintenance Request",
        "description": "Updated description",
        "priority": MaintenancePriority.MEDIUM,
        "status": MaintenanceStatus.IN_PROGRESS
    }
    response = client.put(f"/api/v1/maintenance/{maintenance_id}", json=update_data, headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["priority"] == update_data["priority"]
    assert data["status"] == update_data["status"]

def test_complete_maintenance_request(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la complétion d'une demande de maintenance."""
    # Créer une demande de maintenance
    maintenance_data = {
        "title": "Broken Window",
        "description": "Window in living room is broken",
        "priority": MaintenancePriority.HIGH,
        "status": MaintenanceStatus.PENDING,
        "property_id": property_id,
        "reported_by": "tenant@example.com"
    }
    create_response = client.post("/api/v1/maintenance", json=maintenance_data, headers=tenant_headers)
    maintenance_id = create_response.json()["id"]
    
    # Compléter la demande de maintenance
    completion_data = {
        "completion_notes": "Window has been replaced",
        "completion_date": datetime.utcnow().isoformat(),
        "cost": 500.0
    }
    response = client.post(f"/api/v1/maintenance/{maintenance_id}/complete", json=completion_data, headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == MaintenanceStatus.COMPLETED
    assert data["completion_notes"] == completion_data["completion_notes"]
    assert data["completion_date"] is not None
    assert data["cost"] == completion_data["cost"]

def test_get_high_priority_requests(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la récupération des demandes de maintenance prioritaires."""
    # Créer plusieurs demandes de maintenance avec différentes priorités
    maintenance_requests = [
        {
            "title": f"Maintenance Request {i}",
            "description": f"Description for request {i}",
            "priority": MaintenancePriority.HIGH if i < 2 else MaintenancePriority.MEDIUM,
            "status": MaintenanceStatus.PENDING,
            "property_id": property_id,
            "reported_by": "tenant@example.com"
        } for i in range(3)
    ]
    
    for data in maintenance_requests:
        client.post("/api/v1/maintenance", json=data, headers=tenant_headers)
    
    # Récupérer les demandes prioritaires
    response = client.get("/api/v1/maintenance/high-priority", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(request["priority"] == MaintenancePriority.HIGH for request in data)

def test_get_emergency_requests(client: TestClient, owner_headers, tenant_headers, property_id):
    """Test la récupération des demandes de maintenance d'urgence."""
    # Créer plusieurs demandes de maintenance avec différentes priorités
    maintenance_requests = [
        {
            "title": f"Maintenance Request {i}",
            "description": f"Description for request {i}",
            "priority": MaintenancePriority.EMERGENCY if i == 0 else MaintenancePriority.HIGH,
            "status": MaintenanceStatus.PENDING,
            "property_id": property_id,
            "reported_by": "tenant@example.com"
        } for i in range(3)
    ]
    
    for data in maintenance_requests:
        client.post("/api/v1/maintenance", json=data, headers=tenant_headers)
    
    # Récupérer les demandes d'urgence
    response = client.get("/api/v1/maintenance/emergency", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == MaintenancePriority.EMERGENCY 