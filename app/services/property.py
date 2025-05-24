from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.property import Property, PropertyType, PropertyStatus
from app.core.logging import get_logger

from app.schemas.property import PropertyCreate, PropertyUpdate
from app.models.user import User, UserRole
from app.models.contract import Contract, ContractStatus

logger = get_logger(__name__)

class PropertyService:
    @staticmethod
    def get_property(
        property_id: int,
        db: Session,
        user_role: Optional[UserRole] = None,
        user_id: Optional[int] = None
    ) -> Property:
        """
        Récupère une propriété spécifique avec vérification des permissions.
        
        Args:
            property_id: ID de la propriété à récupérer
            db: Session de base de données
            user_role: Rôle de l'utilisateur qui fait la requête
            user_id: ID de l'utilisateur qui fait la requête
            
        Returns:
            Property: La propriété demandée
            
        Raises:
            HTTPException: Si la propriété n'existe pas ou si l'utilisateur n'a pas les permissions
        """
        property = db.query(Property).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )

        # Vérification des permissions selon le rôle
        if user_role == UserRole.ADMIN or user_role == UserRole.AGENT:
            # Les admins et agents peuvent voir toutes les propriétés
            pass
        elif user_role == UserRole.OWNER:
            # Les propriétaires ne peuvent voir que leurs propriétés
            if property.owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez voir que vos propres propriétés"
                )
        elif user_role == UserRole.TENANT:
            # Les locataires ne peuvent voir que les propriétés qu'ils louent
            has_active_contract = db.query(Contract).filter(
                Contract.property_id == property_id,
                Contract.tenant_id == user_id,
                Contract.status == ContractStatus.ACTIVE
            ).first() is not None
            
            if not has_active_contract:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Vous ne pouvez voir que les propriétés que vous louez"
                )

        return property

    @staticmethod
    def get_properties(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        owner_id: Optional[int] = None,
        status: Optional[PropertyStatus] = None,
        type: Optional[PropertyType] = None,
        user_role: Optional[UserRole] = None,
        user_id: Optional[int] = None
    ) -> List[Property]:
        """
        Récupère une liste de propriétés avec filtres et pagination.
        
        Args:
            db: Session de base de données
            skip: Nombre d'éléments à sauter (doit être >= 0)
            limit: Nombre maximum d'éléments (doit être entre 1 et 100)
            owner_id: ID du propriétaire pour filtrer (uniquement pour ADMIN/AGENT)
            status: Statut de la propriété pour filtrer
            type: Type de propriété pour filtrer
            user_role: Rôle de l'utilisateur qui fait la requête
            user_id: ID de l'utilisateur qui fait la requête
            
        Returns:
            List[Property]: Liste des propriétés correspondant aux critères
            
        Raises:
            HTTPException: Si les paramètres sont invalides ou en cas d'erreur
        """
        try:
            # Validation des paramètres de pagination
            if skip < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le paramètre 'skip' doit être positif"
                )
            
            if not 1 <= limit <= 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le paramètre 'limit' doit être entre 1 et 100"
                )

            # Construction de la requête de base
            query = db.query(Property)

            # Application des filtres selon le rôle de l'utilisateur
            if user_role == UserRole.ADMIN or user_role == UserRole.AGENT:
                # Les admins et agents peuvent voir toutes les propriétés
                if owner_id:
                    query = query.filter(Property.owner_id == owner_id)
            elif user_role == UserRole.OWNER:
                # Les propriétaires ne peuvent voir que leurs propriétés
                if owner_id and owner_id != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Vous ne pouvez voir que vos propres propriétés"
                    )
                query = query.filter(Property.owner_id == user_id)
            elif user_role == UserRole.TENANT:
                # Les locataires ne peuvent voir que les propriétés qu'ils louent
                tenant_contracts = db.query(Contract).filter(
                    Contract.tenant_id == user_id,
                    Contract.status == ContractStatus.ACTIVE
                ).all()
                property_ids = [contract.property_id for contract in tenant_contracts]
                if not property_ids:
                    return []  # Aucune propriété louée
                query = query.filter(Property.id.in_(property_ids))

            # Application des filtres supplémentaires
            if status:
                query = query.filter(Property.status == status)
            if type:
                query = query.filter(Property.type == type)

            # Compte total des résultats (pour la pagination)
            total_count = query.count()
            
            # Application de la pagination
            query = query.order_by(Property.id)  # Tri par ID pour une pagination cohérente
            query = query.offset(skip).limit(limit)
            
            # Exécution de la requête
            properties = query.all()
            
            logger.info(
                f"Récupération de {len(properties)}/{total_count} propriétés avec les filtres: "
                f"skip={skip}, limit={limit}, owner_id={owner_id}, "
                f"status={status}, type={type}, user_role={user_role}"
            )
            
            return properties
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des propriétés: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la récupération des propriétés"
            )

    @staticmethod
    def create_property(property_data: PropertyCreate, db: Session) -> Property:
        # Verify owner exists
        owner = db.query(User).filter(User.id == property_data.owner_id).first()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Owner not found"
            )
        
        # Create property
        db_property = Property(**property_data.dict())
        db.add(db_property)
        db.commit()
        db.refresh(db_property)
        return db_property

    @staticmethod
    def update_property(property_id: int, property_data: PropertyUpdate, db: Session) -> Property:
        property = PropertyService.get_property(property_id, db)
        
        # Update property fields
        for field, value in property_data.dict(exclude_unset=True).items():
            setattr(property, field, value)
        
        db.commit()
        db.refresh(property)
        return property

    @staticmethod
    def delete_property(property_id: int, db: Session) -> None:
        property = PropertyService.get_property(property_id, db)
        
        # Check if property has active contracts
        if property.contracts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete property with active contracts"
            )
        
        db.delete(property)
        db.commit()

    @staticmethod
    def update_property_status(property_id: int, status: PropertyStatus, db: Session) -> Property:
        property = PropertyService.get_property(property_id, db)
        property.status = status
        db.commit()
        db.refresh(property)
        return property 