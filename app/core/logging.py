import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from app.core.config import settings

# Créer le dossier logs s'il n'existe pas
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configuration du format des logs
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configuration du handler pour la console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

# Configuration du handler pour les fichiers
file_handler = RotatingFileHandler(
    filename=log_dir / "app.log",
    maxBytes=10485760,  # 10MB
    backupCount=5,
    encoding="utf-8"
)
file_handler.setFormatter(log_format)

# Configuration du logger principal
logger = logging.getLogger("property_management")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Configuration des loggers spécifiques
api_logger = logging.getLogger("property_management.api")
db_logger = logging.getLogger("property_management.db")
auth_logger = logging.getLogger("property_management.auth")

# En mode développement, on active les logs de debug pour SQLAlchemy
if settings.DEBUG:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Retourne un logger avec le préfixe de l'application."""
    return logging.getLogger(f"property_management.{name}") 