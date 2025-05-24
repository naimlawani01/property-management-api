import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models.payment import PaymentType, PaymentStatus
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
def contract_id(client: TestClient, owner_headers):
    """Crée une propriété et un contrat, et retourne l'ID du contrat."""
    # Créer une propriété
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
    property_response = client.post("/api/v1/properties", json=property_data, headers=owner_headers)
    property_id = property_response.json()["id"]
    
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
    contract_response = client.post("/api/v1/contracts", json=contract_data, headers=owner_headers)
    return contract_response.json()["id"]

def test_create_payment(client: TestClient, owner_headers, tenant_headers, contract_id):
    """Test la création d'un paiement."""
    payment_data = {
        "type": PaymentType.RENT,
        "status": PaymentStatus.PENDING,
        "amount": 1000.0,
        "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "payment_date": None,
        "payment_method": "BANK_TRANSFER",
        "reference": "REF123",
        "notes": "Monthly rent payment",
        "contract_id": contract_id
    }
    
    response = client.post("/api/v1/payments", json=payment_data, headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == payment_data["type"]
    assert data["status"] == payment_data["status"]
    assert data["amount"] == payment_data["amount"]
    assert data["contract_id"] == contract_id

def test_get_payment(client: TestClient, owner_headers, tenant_headers, contract_id):
    """Test la récupération d'un paiement."""
    # Créer un paiement
    payment_data = {
        "type": PaymentType.RENT,
        "status": PaymentStatus.PENDING,
        "amount": 1000.0,
        "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "payment_date": None,
        "payment_method": "BANK_TRANSFER",
        "reference": "REF123",
        "notes": "Monthly rent payment",
        "contract_id": contract_id
    }
    create_response = client.post("/api/v1/payments", json=payment_data, headers=owner_headers)
    payment_id = create_response.json()["id"]
    
    # Récupérer le paiement
    response = client.get(f"/api/v1/payments/{payment_id}", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == payment_id
    assert data["type"] == payment_data["type"]
    assert data["amount"] == payment_data["amount"]

def test_get_payments(client: TestClient, owner_headers, tenant_headers, contract_id):
    """Test la récupération de plusieurs paiements avec filtres."""
    # Créer plusieurs paiements
    payments_data = [
        {
            "type": PaymentType.RENT,
            "status": PaymentStatus.PENDING,
            "amount": 1000.0,
            "due_date": (datetime.utcnow() + timedelta(days=30 * i)).isoformat(),
            "payment_date": None,
            "payment_method": "BANK_TRANSFER",
            "reference": f"REF{i}",
            "notes": f"Payment {i}",
            "contract_id": contract_id
        } for i in range(3)
    ]
    
    for data in payments_data:
        client.post("/api/v1/payments", json=data, headers=owner_headers)
    
    # Tester la récupération sans filtres
    response = client.get("/api/v1/payments", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Tester la récupération avec filtre de type
    response = client.get("/api/v1/payments?type=RENT", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Tester la récupération avec filtre de statut
    response = client.get("/api/v1/payments?status=PENDING", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_update_payment(client: TestClient, owner_headers, tenant_headers, contract_id):
    """Test la mise à jour d'un paiement."""
    # Créer un paiement
    payment_data = {
        "type": PaymentType.RENT,
        "status": PaymentStatus.PENDING,
        "amount": 1000.0,
        "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "payment_date": None,
        "payment_method": "BANK_TRANSFER",
        "reference": "REF123",
        "notes": "Monthly rent payment",
        "contract_id": contract_id
    }
    create_response = client.post("/api/v1/payments", json=payment_data, headers=owner_headers)
    payment_id = create_response.json()["id"]
    
    # Mettre à jour le paiement
    update_data = {
        "amount": 1200.0,
        "notes": "Updated payment notes",
        "status": PaymentStatus.PAID,
        "payment_date": datetime.utcnow().isoformat()
    }
    response = client.put(f"/api/v1/payments/{payment_id}", json=update_data, headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == update_data["amount"]
    assert data["notes"] == update_data["notes"]
    assert data["status"] == update_data["status"]
    assert data["payment_date"] is not None

def test_mark_payment_as_paid(client: TestClient, owner_headers, tenant_headers, contract_id):
    """Test le marquage d'un paiement comme payé."""
    # Créer un paiement
    payment_data = {
        "type": PaymentType.RENT,
        "status": PaymentStatus.PENDING,
        "amount": 1000.0,
        "due_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "payment_date": None,
        "payment_method": "BANK_TRANSFER",
        "reference": "REF123",
        "notes": "Monthly rent payment",
        "contract_id": contract_id
    }
    create_response = client.post("/api/v1/payments", json=payment_data, headers=owner_headers)
    payment_id = create_response.json()["id"]
    
    # Marquer le paiement comme payé
    response = client.post(f"/api/v1/payments/{payment_id}/mark-as-paid", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == PaymentStatus.PAID
    assert data["payment_date"] is not None

def test_check_overdue_payments(client: TestClient, owner_headers, tenant_headers, contract_id):
    """Test la vérification des paiements en retard."""
    # Créer un paiement en retard
    payment_data = {
        "type": PaymentType.RENT,
        "status": PaymentStatus.PENDING,
        "amount": 1000.0,
        "due_date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
        "payment_date": None,
        "payment_method": "BANK_TRANSFER",
        "reference": "REF123",
        "notes": "Overdue payment",
        "contract_id": contract_id
    }
    client.post("/api/v1/payments", json=payment_data, headers=owner_headers)
    
    # Vérifier les paiements en retard
    response = client.get("/api/v1/payments/overdue", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == PaymentStatus.PENDING
    assert data[0]["amount"] == payment_data["amount"]

def test_generate_rent_payments(client: TestClient, owner_headers, tenant_headers, contract_id):
    """Test la génération des paiements de loyer."""
    # Générer les paiements de loyer
    response = client.post(f"/api/v1/payments/generate-rent/{contract_id}", headers=owner_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    
    # Vérifier que les paiements ont été créés
    payments_response = client.get("/api/v1/payments", headers=owner_headers)
    assert payments_response.status_code == 200
    payments_data = payments_response.json()
    assert len(payments_data) == len(data) 