from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Création du moteur SQLAlchemy
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation
    pool_size=5,  # Nombre de connexions dans le pool
    max_overflow=10,  # Nombre maximum de connexions supplémentaires
    echo=settings.DEBUG  # Active les logs SQL en mode debug
)

# Création de la factory de sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    Fournit une session de base de données.
    
    Yields:
        Session: Session de base de données
        
    Example:
        ```python
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.debug("Session de base de données fermée") 