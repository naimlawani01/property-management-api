import pytest
from fastapi.testclient import TestClient
from app.models.user import UserRole
from app.schemas.user import UserCreate

def test_register_user(client: TestClient):
    """Test l'inscription d'un nouvel utilisateur."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": UserRole.TENANT
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["role"] == user_data["role"]
    assert "password" not in data

def test_login_user(client: TestClient):
    """Test la connexion d'un utilisateur."""
    # D'abord, créer un utilisateur
    user_data = {
        "email": "login@example.com",
        "password": "loginpassword123",
        "full_name": "Login User",
        "role": UserRole.TENANT
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Ensuite, tester la connexion
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == user_data["email"]

def test_login_wrong_password(client: TestClient):
    """Test la connexion avec un mauvais mot de passe."""
    # D'abord, créer un utilisateur
    user_data = {
        "email": "wrong@example.com",
        "password": "correctpassword123",
        "full_name": "Wrong Password User",
        "role": UserRole.TENANT
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Tester la connexion avec un mauvais mot de passe
    login_data = {
        "username": user_data["email"],
        "password": "wrongpassword123"
    }
    response = client.post("/api/v1/auth/token", data=login_data)
    assert response.status_code == 401

def test_get_current_user(client: TestClient):
    """Test la récupération des informations de l'utilisateur connecté."""
    # Créer un utilisateur
    user_data = {
        "email": "current@example.com",
        "password": "currentpassword123",
        "full_name": "Current User",
        "role": UserRole.TENANT
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Se connecter pour obtenir un token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/api/v1/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    # Récupérer les informations de l'utilisateur
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]

def test_update_current_user(client: TestClient):
    """Test la mise à jour des informations de l'utilisateur connecté."""
    # Créer un utilisateur
    user_data = {
        "email": "update@example.com",
        "password": "updatepassword123",
        "full_name": "Update User",
        "role": UserRole.TENANT
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Se connecter pour obtenir un token
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = client.post("/api/v1/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    # Mettre à jour les informations de l'utilisateur
    update_data = {
        "full_name": "Updated Name",
        "phone": "1234567890"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put("/api/v1/auth/me", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["phone"] == update_data["phone"]
    assert data["email"] == user_data["email"]  # L'email ne devrait pas changer 