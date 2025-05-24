import pytest
from fastapi.testclient import TestClient
from app.models.property import PropertyType, PropertyStatus
from app.models.user import UserRole

@pytest.fixture
def auth_headers(client: TestClient):
    """Crée un utilisateur et retourne les headers d'authentification."""
    # Créer un utilisateur
    user_data = {
        "email": "owner@example.com",
        "password": "ownerpassword123",
        "full_name": "Property Owner",
        "role": UserRole.OWNER
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Se connecter pour obtenir un token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/api/v1/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

def test_create_property(client: TestClient, auth_headers):
    """Test la création d'une propriété."""
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
    
    response = client.post("/api/v1/properties", json=property_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == property_data["title"]
    assert data["type"] == property_data["type"]
    assert data["status"] == property_data["status"]

def test_get_property(client: TestClient, auth_headers):
    """Test la récupération d'une propriété."""
    # Créer une propriété
    property_data = {
        "title": "Get Test Property",
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
    create_response = client.post("/api/v1/properties", json=property_data, headers=auth_headers)
    property_id = create_response.json()["id"]
    
    # Récupérer la propriété
    response = client.get(f"/api/v1/properties/{property_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == property_id
    assert data["title"] == property_data["title"]

def test_get_properties(client: TestClient, auth_headers):
    """Test la récupération de plusieurs propriétés avec filtres."""
    # Créer plusieurs propriétés
    properties_data = [
        {
            "title": f"Test Property {i}",
            "description": f"A test property {i}",
            "type": PropertyType.APARTMENT,
            "status": PropertyStatus.AVAILABLE,
            "address": f"{i}23 Test Street",
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
        } for i in range(3)
    ]
    
    for data in properties_data:
        client.post("/api/v1/properties", json=data, headers=auth_headers)
    
    # Tester la récupération sans filtres
    response = client.get("/api/v1/properties", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Tester la récupération avec filtre de type
    response = client.get("/api/v1/properties?type=APARTMENT", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Tester la récupération avec filtre de statut
    response = client.get("/api/v1/properties?status=AVAILABLE", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_update_property(client: TestClient, auth_headers):
    """Test la mise à jour d'une propriété."""
    # Créer une propriété
    property_data = {
        "title": "Update Test Property",
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
    create_response = client.post("/api/v1/properties", json=property_data, headers=auth_headers)
    property_id = create_response.json()["id"]
    
    # Mettre à jour la propriété
    update_data = {
        "title": "Updated Property",
        "price": 1200.0,
        "status": PropertyStatus.RENTED
    }
    response = client.put(f"/api/v1/properties/{property_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["price"] == update_data["price"]
    assert data["status"] == update_data["status"]

def test_delete_property(client: TestClient, auth_headers):
    """Test la suppression d'une propriété."""
    # Créer une propriété
    property_data = {
        "title": "Delete Test Property",
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
    create_response = client.post("/api/v1/properties", json=property_data, headers=auth_headers)
    property_id = create_response.json()["id"]
    
    # Supprimer la propriété
    response = client.delete(f"/api/v1/properties/{property_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Vérifier que la propriété n'existe plus
    response = client.get(f"/api/v1/properties/{property_id}", headers=auth_headers)
    assert response.status_code == 404 