from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator
import secrets
from pathlib import Path
from functools import lru_cache

class Settings(BaseSettings):
    # Configuration de la base de données
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/property_management"
    
    # Configuration de l'API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Property Management API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API de gestion immobilière"
    
    # Configuration CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Configuration JWT
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuration du mode debug
    DEBUG: bool = True
    
    # Sécurité
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Base de données
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "property_management"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Fichiers
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: Path = Path("logs")
    
    # Maintenance
    MAINTENANCE_EMAIL_NOTIFICATIONS: bool = True
    MAINTENANCE_SMS_NOTIFICATIONS: bool = False
    
    # Paiements
    PAYMENT_DUE_DAYS: int = 5
    PAYMENT_GRACE_PERIOD_DAYS: int = 3
    PAYMENT_LATE_FEE_PERCENTAGE: float = 5.0
    
    # Contrats
    CONTRACT_RENEWAL_NOTICE_DAYS: int = 90
    CONTRACT_MIN_DURATION_MONTHS: int = 12
    CONTRACT_MAX_DURATION_MONTHS: int = 36
    
    # Propriétés
    PROPERTY_MIN_PRICE: float = 0.0
    PROPERTY_MAX_PRICE: float = 10000000.0
    PROPERTY_MIN_SURFACE: float = 0.0
    PROPERTY_MAX_SURFACE: float = 1000.0
    
    # SMS
    SMS_PROVIDER: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    SMS_FROM_NUMBER: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

@lru_cache()
def get_settings() -> Settings:
    """Obtient les paramètres de configuration."""
    return Settings()

settings = get_settings() 