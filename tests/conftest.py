import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.database import Base
from app.models import User, Property, Contract, Payment, MaintenanceRequest

# Créer une base de données de test
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    """Crée le moteur de base de données pour les tests."""
    engine = create_engine(
        TEST_SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="session")
def db_session(engine) -> Generator[Session, None, None]:
    """Crée une session de base de données pour les tests."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def db(db_session: Session) -> Generator[Session, None, None]:
    """Crée une transaction de base de données pour chaque test."""
    transaction = db_session.begin_nested()
    yield db_session
    transaction.rollback()

@pytest.fixture(scope="function")
def client(db: Session):
    """Crée un client de test pour l'API."""
    from fastapi.testclient import TestClient
    from app.main import app
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear() 