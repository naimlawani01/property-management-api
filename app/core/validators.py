from datetime import datetime, date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re
from app.core.exceptions import ValidationException
from app.core.config import settings

class BaseValidator(BaseModel):
    """Classe de base pour la validation des données."""
    
    class Config:
        """Configuration de la validation."""
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }

class UserValidator(BaseValidator):
    """Validateur pour les données utilisateur."""
    
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    role: str = Field(..., pattern="^(admin|owner|tenant)$")
    
    @validator("password")
    def validate_password(cls, v: str) -> str:
        """Valide le mot de passe."""
        if not any(c.isupper() for c in v):
            raise ValidationException("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.islower() for c in v):
            raise ValidationException("Le mot de passe doit contenir au moins une minuscule")
        if not any(c.isdigit() for c in v):
            raise ValidationException("Le mot de passe doit contenir au moins un chiffre")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValidationException("Le mot de passe doit contenir au moins un caractère spécial")
        return v

class PropertyValidator(BaseValidator):
    """Validateur pour les données de propriété."""
    
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    address: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    postal_code: str = Field(..., pattern=r"^\d{5}$")
    surface: float = Field(..., gt=0, le=1000)
    rooms: int = Field(..., gt=0, le=20)
    price: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(apartment|house|commercial|land)$")
    status: str = Field(..., pattern="^(available|rented|maintenance|sold)$")
    
    @validator("surface")
    def validate_surface(cls, v: float) -> float:
        """Valide la surface."""
        if v < settings.PROPERTY_MIN_SURFACE:
            raise ValidationException(f"La surface doit être supérieure à {settings.PROPERTY_MIN_SURFACE}m²")
        if v > settings.PROPERTY_MAX_SURFACE:
            raise ValidationException(f"La surface doit être inférieure à {settings.PROPERTY_MAX_SURFACE}m²")
        return v

class ContractValidator(BaseValidator):
    """Validateur pour les données de contrat."""
    
    property_id: int = Field(..., gt=0)
    tenant_id: int = Field(..., gt=0)
    start_date: date
    end_date: date
    rent_amount: float = Field(..., gt=0)
    deposit_amount: float = Field(..., gt=0)
    payment_day: int = Field(..., ge=1, le=31)
    
    @validator("end_date")
    def validate_dates(cls, v: date, values: Dict[str, Any]) -> date:
        """Valide les dates du contrat."""
        if "start_date" in values and v <= values["start_date"]:
            raise ValidationException("La date de fin doit être postérieure à la date de début")
        return v
    
    @validator("deposit_amount")
    def validate_deposit(cls, v: float, values: Dict[str, Any]) -> float:
        """Valide le montant de la caution."""
        if "rent_amount" in values and v < values["rent_amount"]:
            raise ValidationException("La caution doit être au moins égale au montant du loyer")
        return v

class PaymentValidator(BaseValidator):
    """Validateur pour les données de paiement."""
    
    contract_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(rent|deposit|maintenance|other)$")
    due_date: date
    
    @validator("amount")
    def validate_amount(cls, v: float) -> float:
        """Valide le montant du paiement."""
        if v <= 0:
            raise ValidationException("Le montant doit être supérieur à 0")
        return v

class MaintenanceRequestValidator(BaseValidator):
    """Validateur pour les données de demande de maintenance."""
    
    property_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=1000)
    priority: str = Field(..., pattern="^(low|medium|high|emergency)$")
    
    @validator("priority")
    def validate_priority(cls, v: str) -> str:
        """Valide la priorité."""
        if v == "emergency":
            # Vérifier si le nombre de demandes d'urgence en cours n'est pas trop élevé
            # TODO: Implémenter la vérification
            pass
        return v

class FileValidator(BaseValidator):
    """Validateur pour les données de fichier."""
    
    filename: str
    content_type: str
    size: int
    
    @validator("content_type")
    def validate_content_type(cls, v: str) -> str:
        """Valide le type de contenu."""
        allowed_types = {
            "image/jpeg": "jpg",
            "image/png": "png",
            "application/pdf": "pdf"
        }
        if v not in allowed_types:
            raise ValidationException(f"Type de fichier non autorisé. Types autorisés : {', '.join(allowed_types.values())}")
        return v
    
    @validator("size")
    def validate_size(cls, v: int) -> int:
        """Valide la taille du fichier."""
        if v > settings.MAX_UPLOAD_SIZE:
            raise ValidationException(f"Fichier trop volumineux. Taille maximale : {settings.MAX_UPLOAD_SIZE} octets")
        return v

class SearchValidator(BaseValidator):
    """Validateur pour les paramètres de recherche."""
    
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
    sort: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    
    @validator("sort")
    def validate_sort(cls, v: Optional[str]) -> Optional[str]:
        """Valide le paramètre de tri."""
        if v:
            parts = v.split(":")
            if len(parts) != 2 or parts[1] not in ["asc", "desc"]:
                raise ValidationException("Format de tri invalide. Utilisez 'champ:asc' ou 'champ:desc'")
        return v

class PaginationValidator(BaseValidator):
    """Validateur pour la pagination."""
    
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)
    total: int = Field(..., ge=0)
    
    @property
    def offset(self) -> int:
        """Calcule l'offset pour la pagination."""
        return (self.page - 1) * self.size
    
    @property
    def total_pages(self) -> int:
        """Calcule le nombre total de pages."""
        return (self.total + self.size - 1) // self.size
    
    @property
    def has_next(self) -> bool:
        """Vérifie s'il y a une page suivante."""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Vérifie s'il y a une page précédente."""
        return self.page > 1

class PasswordValidator:
    """Classe pour valider les mots de passe."""
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Valide un mot de passe selon les critères suivants :
        - Au moins 8 caractères
        - Au moins une lettre majuscule
        - Au moins une lettre minuscule
        - Au moins un chiffre
        - Au moins un caractère spécial
        """
        if len(password) < 8:
            return False
        
        if not re.search(r"[A-Z]", password):
            return False
            
        if not re.search(r"[a-z]", password):
            return False
            
        if not re.search(r"\d", password):
            return False
            
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
            
        return True

class PhoneNumberValidator:
    """Classe pour valider les numéros de téléphone."""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Valide un numéro de téléphone français.
        Format accepté : +33XXXXXXXXX ou 0XXXXXXXXX
        """
        pattern = r"^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$"
        return bool(re.match(pattern, phone))

class DateValidator:
    """Classe pour valider les dates."""
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Vérifie si la date de fin est après la date de début."""
        return end_date > start_date
    
    @staticmethod
    def validate_future_date(date: datetime) -> bool:
        """Vérifie si la date est dans le futur."""
        return date > datetime.now()

class AmountValidator:
    """Classe pour valider les montants."""
    
    @staticmethod
    def validate_positive_amount(amount: float) -> bool:
        """Vérifie si le montant est positif."""
        return amount > 0
    
    @staticmethod
    def validate_amount_range(amount: float, min_amount: float, max_amount: float) -> bool:
        """Vérifie si le montant est dans la plage spécifiée."""
        return min_amount <= amount <= max_amount

class AddressValidator:
    """Classe pour valider les adresses."""
    
    @staticmethod
    def validate_postal_code(postal_code: str) -> bool:
        """Valide un code postal français."""
        pattern = r"^[0-9]{5}$"
        return bool(re.match(pattern, postal_code))
    
    @staticmethod
    def validate_city(city: str) -> bool:
        """Valide une ville française."""
        # Liste des villes françaises (à compléter selon les besoins)
        valid_cities = ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille"]
        return city in valid_cities

class MaintenanceValidator:
    """Classe pour valider les demandes de maintenance."""
    
    @staticmethod
    def validate_priority(priority: str) -> bool:
        """Vérifie si la priorité est valide."""
        valid_priorities = ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]
        return priority in valid_priorities
    
    @staticmethod
    def validate_status(status: str) -> bool:
        """Vérifie si le statut est valide."""
        valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
        return status in valid_statuses 