# API de Gestion Immobilière

Cette API permet de gérer des propriétés immobilières, des contrats de location, des paiements et des demandes de maintenance.

## Fonctionnalités

- **Authentification** : Gestion des utilisateurs et des tokens JWT
- **Propriétés** : Gestion des biens immobiliers (création, modification, suppression)
- **Contrats** : Gestion des contrats de location
- **Paiements** : Suivi des paiements de loyer et autres charges
- **Maintenance** : Gestion des demandes de maintenance

## Prérequis

- Python 3.11+
- PostgreSQL 15+
- pip (gestionnaire de paquets Python)

## Installation

1. Cloner le repository :
```bash
git clone <repository-url>
cd property-management-api
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Unix/macOS
# ou
.\venv\Scripts\activate  # Sur Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer le fichier .env avec vos paramètres
```

5. Initialiser la base de données :
```bash
alembic upgrade head
```

## Démarrage

### Développement

```bash
python run.py
```

L'API sera accessible à l'adresse : http://localhost:8000

### Production avec Docker

```bash
docker-compose up --build
```

## Documentation de l'API

La documentation interactive de l'API est disponible aux adresses suivantes :
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## Tests

Exécuter les tests unitaires et d'intégration :
```bash
pytest
```

Avec couverture de code :
```bash
pytest --cov=app --cov-report=term-missing
```

## Structure du Projet

```
property-management-api/
├── alembic/              # Migrations de base de données
├── app/
│   ├── api/             # Routes de l'API
│   ├── core/            # Configuration et utilitaires
│   ├── models/          # Modèles de base de données
│   ├── schemas/         # Schémas Pydantic
│   └── services/        # Logique métier
├── logs/                # Fichiers de logs
├── tests/               # Tests unitaires et d'intégration
├── .env                 # Variables d'environnement
├── .env.example         # Exemple de variables d'environnement
├── alembic.ini          # Configuration Alembic
├── docker-compose.yml   # Configuration Docker
├── Dockerfile          # Configuration Docker
├── requirements.txt    # Dépendances Python
└── run.py             # Script de démarrage
```

## Endpoints Principaux

### Authentification
- `POST /api/v1/auth/register` : Inscription d'un nouvel utilisateur
- `POST /api/v1/auth/token` : Connexion et obtention du token JWT
- `GET /api/v1/auth/me` : Informations de l'utilisateur connecté

### Propriétés
- `GET /api/v1/properties` : Liste des propriétés
- `POST /api/v1/properties` : Création d'une propriété
- `GET /api/v1/properties/{id}` : Détails d'une propriété
- `PUT /api/v1/properties/{id}` : Mise à jour d'une propriété
- `DELETE /api/v1/properties/{id}` : Suppression d'une propriété

### Contrats
- `GET /api/v1/contracts` : Liste des contrats
- `POST /api/v1/contracts` : Création d'un contrat
- `GET /api/v1/contracts/{id}` : Détails d'un contrat
- `PUT /api/v1/contracts/{id}` : Mise à jour d'un contrat
- `POST /api/v1/contracts/{id}/terminate` : Résiliation d'un contrat

### Paiements
- `GET /api/v1/payments` : Liste des paiements
- `POST /api/v1/payments` : Création d'un paiement
- `GET /api/v1/payments/{id}` : Détails d'un paiement
- `PUT /api/v1/payments/{id}` : Mise à jour d'un paiement
- `POST /api/v1/payments/{id}/mark-as-paid` : Marquage d'un paiement comme payé
- `GET /api/v1/payments/overdue` : Liste des paiements en retard

### Maintenance
- `GET /api/v1/maintenance` : Liste des demandes de maintenance
- `POST /api/v1/maintenance` : Création d'une demande
- `GET /api/v1/maintenance/{id}` : Détails d'une demande
- `PUT /api/v1/maintenance/{id}` : Mise à jour d'une demande
- `POST /api/v1/maintenance/{id}/complete` : Complétion d'une demande
- `GET /api/v1/maintenance/high-priority` : Demandes prioritaires
- `GET /api/v1/maintenance/emergency` : Demandes d'urgence

## Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 