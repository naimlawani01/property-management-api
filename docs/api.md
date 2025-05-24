# Documentation de l'API de Gestion Immobilière

## Introduction

Cette API permet de gérer des propriétés immobilières, des contrats de location, des paiements et des demandes de maintenance. Elle est construite avec FastAPI et utilise PostgreSQL comme base de données.

## Authentification

L'API utilise JWT (JSON Web Tokens) pour l'authentification. Pour accéder aux endpoints protégés, vous devez inclure le token dans l'en-tête `Authorization` :

```
Authorization: Bearer <votre_token>
```

### Endpoints d'authentification

#### Inscription
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "role": "tenant"
}
```

#### Connexion
```http
POST /api/v1/auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

## Gestion des Propriétés

### Créer une propriété
```http
POST /api/v1/properties
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Appartement T3",
    "description": "Bel appartement au centre-ville",
    "address": "123 rue Example",
    "city": "Paris",
    "postal_code": "75001",
    "surface": 75.5,
    "rooms": 3,
    "price": 1200.0,
    "type": "apartment",
    "status": "available"
}
```

### Obtenir une propriété
```http
GET /api/v1/properties/{property_id}
Authorization: Bearer <token>
```

### Lister les propriétés
```http
GET /api/v1/properties
Authorization: Bearer <token>
```

Paramètres de requête :
- `type`: Type de propriété (apartment, house, etc.)
- `status`: Statut (available, rented, etc.)
- `min_price`: Prix minimum
- `max_price`: Prix maximum
- `min_surface`: Surface minimum
- `max_surface`: Surface maximum

### Mettre à jour une propriété
```http
PUT /api/v1/properties/{property_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Appartement T3 rénové",
    "price": 1300.0
}
```

### Supprimer une propriété
```http
DELETE /api/v1/properties/{property_id}
Authorization: Bearer <token>
```

## Gestion des Contrats

### Créer un contrat
```http
POST /api/v1/contracts
Authorization: Bearer <token>
Content-Type: application/json

{
    "property_id": 1,
    "tenant_id": 2,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "rent_amount": 1200.0,
    "deposit_amount": 1200.0
}
```

### Obtenir un contrat
```http
GET /api/v1/contracts/{contract_id}
Authorization: Bearer <token>
```

### Lister les contrats
```http
GET /api/v1/contracts
Authorization: Bearer <token>
```

Paramètres de requête :
- `property_id`: ID de la propriété
- `tenant_id`: ID du locataire
- `status`: Statut du contrat (active, terminated, etc.)

### Mettre à jour un contrat
```http
PUT /api/v1/contracts/{contract_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "rent_amount": 1300.0
}
```

### Résilier un contrat
```http
POST /api/v1/contracts/{contract_id}/terminate
Authorization: Bearer <token>
Content-Type: application/json

{
    "termination_date": "2024-06-30",
    "reason": "Déménagement du locataire"
}
```

## Gestion des Paiements

### Créer un paiement
```http
POST /api/v1/payments
Authorization: Bearer <token>
Content-Type: application/json

{
    "contract_id": 1,
    "amount": 1200.0,
    "type": "rent",
    "due_date": "2024-01-01"
}
```

### Obtenir un paiement
```http
GET /api/v1/payments/{payment_id}
Authorization: Bearer <token>
```

### Lister les paiements
```http
GET /api/v1/payments
Authorization: Bearer <token>
```

Paramètres de requête :
- `contract_id`: ID du contrat
- `type`: Type de paiement (rent, deposit, etc.)
- `status`: Statut (pending, paid, overdue, etc.)

### Marquer un paiement comme payé
```http
POST /api/v1/payments/{payment_id}/mark-paid
Authorization: Bearer <token>
Content-Type: application/json

{
    "payment_date": "2024-01-01",
    "payment_method": "bank_transfer"
}
```

## Gestion des Demandes de Maintenance

### Créer une demande
```http
POST /api/v1/maintenance
Authorization: Bearer <token>
Content-Type: application/json

{
    "property_id": 1,
    "title": "Fuite d'eau",
    "description": "Fuite sous l'évier de la cuisine",
    "priority": "high"
}
```

### Obtenir une demande
```http
GET /api/v1/maintenance/{request_id}
Authorization: Bearer <token>
```

### Lister les demandes
```http
GET /api/v1/maintenance
Authorization: Bearer <token>
```

Paramètres de requête :
- `property_id`: ID de la propriété
- `priority`: Priorité (low, medium, high, emergency)
- `status`: Statut (pending, in_progress, completed, etc.)

### Mettre à jour une demande
```http
PUT /api/v1/maintenance/{request_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "in_progress",
    "notes": "Technicien contacté"
}
```

### Marquer une demande comme terminée
```http
POST /api/v1/maintenance/{request_id}/complete
Authorization: Bearer <token>
Content-Type: application/json

{
    "completion_date": "2024-01-02",
    "cost": 150.0,
    "notes": "Réparation effectuée"
}
```

## Codes d'erreur

- `400 Bad Request`: Requête invalide
- `401 Unauthorized`: Non authentifié
- `403 Forbidden`: Non autorisé
- `404 Not Found`: Ressource non trouvée
- `422 Unprocessable Entity`: Données invalides
- `429 Too Many Requests`: Limite de taux dépassée
- `500 Internal Server Error`: Erreur serveur

## Limitation de taux

L'API implémente une limitation de taux pour protéger contre les abus. Par défaut, chaque client est limité à 60 requêtes par minute. Les en-têtes de réponse incluent :

- `X-RateLimit-Limit`: Nombre maximum de requêtes
- `X-RateLimit-Remaining`: Nombre de requêtes restantes
- `X-RateLimit-Reset`: Timestamp de réinitialisation

## Exemples de réponses

### Succès
```json
{
    "id": 1,
    "title": "Appartement T3",
    "status": "success"
}
```

### Erreur
```json
{
    "detail": "Propriété non trouvée"
}
```

## Bonnes pratiques

1. Utilisez toujours HTTPS en production
2. Gérez correctement les tokens JWT
3. Validez les données avant l'envoi
4. Gérez les erreurs côté client
5. Utilisez la pagination pour les listes
6. Mettez en cache les réponses fréquentes
7. Respectez les limites de taux 