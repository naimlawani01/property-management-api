from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class PropertyManagementException(HTTPException):
    """Exception de base pour l'application."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class NotFoundException(PropertyManagementException):
    """Exception pour les ressources non trouvées."""
    
    def __init__(self, detail: str = "Ressource non trouvée"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ValidationException(PropertyManagementException):
    """Exception pour les erreurs de validation."""
    
    def __init__(self, detail: str = "Données invalides"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class AuthenticationException(PropertyManagementException):
    """Exception pour les erreurs d'authentification."""
    
    def __init__(self, detail: str = "Authentification requise"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationException(PropertyManagementException):
    """Exception pour les erreurs d'autorisation."""
    
    def __init__(self, detail: str = "Accès non autorisé"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

class ConflictException(PropertyManagementException):
    """Exception pour les conflits de ressources."""
    
    def __init__(self, detail: str = "Conflit avec l'état actuel de la ressource"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )

class RateLimitException(PropertyManagementException):
    """Exception pour les dépassements de limite de taux."""
    
    def __init__(self, detail: str = "Limite de taux dépassée"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )

class DatabaseException(PropertyManagementException):
    """Exception pour les erreurs de base de données."""
    
    def __init__(self, detail: str = "Erreur de base de données"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class FileException(PropertyManagementException):
    """Exception pour les erreurs de gestion de fichiers."""
    
    def __init__(self, detail: str = "Erreur de gestion de fichier"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class NotificationException(PropertyManagementException):
    """Exception pour les erreurs de notification."""
    
    def __init__(self, detail: str = "Erreur d'envoi de notification"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class CacheException(PropertyManagementException):
    """Exception pour les erreurs de cache."""
    
    def __init__(self, detail: str = "Erreur de cache"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

# Exceptions spécifiques aux domaines

class PropertyNotFoundException(NotFoundException):
    """Exception pour les propriétés non trouvées."""
    
    def __init__(self, property_id: int):
        super().__init__(f"Propriété {property_id} non trouvée")

class ContractNotFoundException(NotFoundException):
    """Exception pour les contrats non trouvés."""
    
    def __init__(self, contract_id: int):
        super().__init__(f"Contrat {contract_id} non trouvé")

class PaymentNotFoundException(NotFoundException):
    """Exception pour les paiements non trouvés."""
    
    def __init__(self, payment_id: int):
        super().__init__(f"Paiement {payment_id} non trouvé")

class MaintenanceRequestNotFoundException(NotFoundException):
    """Exception pour les demandes de maintenance non trouvées."""
    
    def __init__(self, request_id: int):
        super().__init__(f"Demande de maintenance {request_id} non trouvée")

class UserNotFoundException(NotFoundException):
    """Exception pour les utilisateurs non trouvés."""
    
    def __init__(self, user_id: int):
        super().__init__(f"Utilisateur {user_id} non trouvé")

class PropertyNotAvailableException(ConflictException):
    """Exception pour les propriétés non disponibles."""
    
    def __init__(self, property_id: int):
        super().__init__(f"Propriété {property_id} non disponible")

class ContractAlreadyExistsException(ConflictException):
    """Exception pour les contrats déjà existants."""
    
    def __init__(self, property_id: int):
        super().__init__(f"Un contrat existe déjà pour la propriété {property_id}")

class PaymentAlreadyPaidException(ConflictException):
    """Exception pour les paiements déjà effectués."""
    
    def __init__(self, payment_id: int):
        super().__init__(f"Le paiement {payment_id} a déjà été effectué")

class MaintenanceRequestAlreadyCompletedException(ConflictException):
    """Exception pour les demandes de maintenance déjà terminées."""
    
    def __init__(self, request_id: int):
        super().__init__(f"La demande de maintenance {request_id} est déjà terminée")

class InvalidCredentialsException(AuthenticationException):
    """Exception pour les identifiants invalides."""
    
    def __init__(self):
        super().__init__("Identifiants invalides")

class TokenExpiredException(AuthenticationException):
    """Exception pour les tokens expirés."""
    
    def __init__(self):
        super().__init__("Token expiré")

class InsufficientPermissionsException(AuthorizationException):
    """Exception pour les permissions insuffisantes."""
    
    def __init__(self, required_role: str):
        super().__init__(f"Rôle {required_role} requis")

class InvalidFileTypeException(ValidationException):
    """Exception pour les types de fichiers invalides."""
    
    def __init__(self, allowed_types: list):
        super().__init__(f"Type de fichier non autorisé. Types autorisés : {', '.join(allowed_types)}")

class FileTooLargeException(ValidationException):
    """Exception pour les fichiers trop volumineux."""
    
    def __init__(self, max_size: int):
        super().__init__(f"Fichier trop volumineux. Taille maximale : {max_size} octets")

class RateLimitError(HTTPException):
    """Exception levée lorsqu'une limite de taux est dépassée."""
    
    def __init__(self, detail: str):
        """
        Initialise l'exception.
        
        Args:
            detail: Message d'erreur détaillé
        """
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers={"Retry-After": "60"}
        ) 