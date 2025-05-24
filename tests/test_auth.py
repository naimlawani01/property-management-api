import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import AuthService

def test_create_access_token():
    """Test la création d'un token d'accès."""
    data = {"sub": "test@example.com"}
    token = AuthService.create_access_token(data)
    assert token is not None
    assert isinstance(token, str)

def test_verify_token():
    """Test la vérification d'un token."""
    data = {"sub": "test@example.com"}
    token = AuthService.create_access_token(data)
    payload = AuthService.verify_token(token)
    assert payload is not None
    assert payload.get("sub") == "test@example.com"

def test_authenticate_user(db: Session):
    """Test l'authentification d'un utilisateur."""
    # Créer un utilisateur de test
    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
        role=UserRole.TENANT
    )
    user = AuthService.create_user(db, user_data)
    
    # Tester l'authentification réussie
    authenticated_user = AuthService.authenticate_user(db, "test@example.com", "testpassword123")
    assert authenticated_user is not None
    assert authenticated_user.email == user.email
    
    # Tester l'authentification échouée
    failed_auth = AuthService.authenticate_user(db, "test@example.com", "wrongpassword")
    assert failed_auth is None

def test_create_user(db: Session):
    """Test la création d'un utilisateur."""
    user_data = UserCreate(
        email="new@example.com",
        password="newpassword123",
        full_name="New User",
        role=UserRole.OWNER
    )
    
    user = AuthService.create_user(db, user_data)
    assert user is not None
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name
    assert user.role == user_data.role
    
    # Vérifier que le mot de passe est hashé
    assert user.hashed_password != user_data.password

def test_create_duplicate_user(db: Session):
    """Test la création d'un utilisateur avec un email déjà existant."""
    user_data = UserCreate(
        email="duplicate@example.com",
        password="password123",
        full_name="Duplicate User",
        role=UserRole.AGENT
    )
    
    # Créer le premier utilisateur
    AuthService.create_user(db, user_data)
    
    # Tenter de créer un utilisateur avec le même email
    with pytest.raises(ValueError):
        AuthService.create_user(db, user_data)

def test_update_user(db: Session):
    """Test la mise à jour d'un utilisateur."""
    # Créer un utilisateur de test
    user_data = UserCreate(
        email="update@example.com",
        password="password123",
        full_name="Update User",
        role=UserRole.TENANT
    )
    user = AuthService.create_user(db, user_data)
    
    # Mettre à jour l'utilisateur
    update_data = UserUpdate(
        full_name="Updated Name",
        phone="1234567890"
    )
    updated_user = AuthService.update_user(db, user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.full_name == update_data.full_name
    assert updated_user.phone == update_data.phone
    assert updated_user.email == user.email  # L'email ne devrait pas changer

def test_get_current_user(db: Session):
    """Test la récupération de l'utilisateur courant."""
    # Créer un utilisateur de test
    user_data = UserCreate(
        email="current@example.com",
        password="password123",
        full_name="Current User",
        role=UserRole.ADMIN
    )
    user = AuthService.create_user(db, user_data)
    
    # Créer un token pour l'utilisateur
    token = AuthService.create_access_token({"sub": user.email})
    
    # Récupérer l'utilisateur courant
    current_user = AuthService.get_current_user(db, token)
    assert current_user is not None
    assert current_user.id == user.id
    assert current_user.email == user.email

def test_get_current_user_invalid_token(db: Session):
    """Test la récupération de l'utilisateur courant avec un token invalide."""
    with pytest.raises(ValueError):
        AuthService.get_current_user(db, "invalid_token")

def test_get_current_user_expired_token(db: Session):
    """Test la récupération de l'utilisateur courant avec un token expiré."""
    # Créer un token expiré
    data = {"sub": "test@example.com", "exp": datetime.utcnow() - timedelta(minutes=1)}
    expired_token = AuthService.create_access_token(data)
    
    with pytest.raises(ValueError):
        AuthService.get_current_user(db, expired_token) 