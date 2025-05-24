from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from sqlalchemy.orm import Session
import pytz
from .logging import get_logger
from .notifications import notification_manager
from models.contract import Contract
from models.payment import Payment
from models.maintenance import MaintenanceRequest
from .config import settings

logger = get_logger(__name__)

# Configure timezone
timezone = pytz.timezone('Europe/Paris')

class TaskScheduler:
    """Gestionnaire des tâches planifiées."""
    
    def __init__(self):
        """Initialise le planificateur de tâches."""
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=timezone
        )
        self.scheduler.start()
        logger.info("Planificateur de tâches démarré")
    
    def schedule_payment_reminders(self, db: Session) -> None:
        """
        Planifie l'envoi des rappels de paiement.
        
        Args:
            db: Session de base de données
        """
        try:
            # Récupérer les paiements à venir dans les 7 jours
            due_date = datetime.now(timezone) + timedelta(days=7)
            payments = db.query(Payment).filter(
                Payment.due_date <= due_date,
                Payment.status == "pending"
            ).all()
            
            for payment in payments:
                # Récupérer les informations du contrat et de la propriété
                contract = db.query(Contract).filter(Contract.id == payment.contract_id).first()
                if not contract:
                    continue
                
                # Préparer le message
                message = f"Rappel: Paiement de {payment.amount}€ pour {contract.property.address} dû le {payment.due_date.strftime('%d/%m/%Y')}"
                
                # Envoyer la notification
                notification_manager.send_notification(
                    message=message,
                    to_email=contract.tenant.email,
                    to_number=contract.tenant.phone,
                    subject="Rappel de paiement"
                )
            
            logger.info(f"Rappels de paiement envoyés pour {len(payments)} paiements")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi des rappels de paiement : {str(e)}")
    
    def check_contract_renewals(self, db: Session) -> None:
        """
        Vérifie les contrats à renouveler.
        
        Args:
            db: Session de base de données
        """
        try:
            # Récupérer les contrats qui expirent dans les 30 jours
            expiry_date = datetime.now(timezone) + timedelta(days=30)
            contracts = db.query(Contract).filter(
                Contract.end_date <= expiry_date,
                Contract.status == "active"
            ).all()
            
            for contract in contracts:
                # Préparer le message
                message = f"Votre contrat pour {contract.property.address} expire le {contract.end_date.strftime('%d/%m/%Y')}. Veuillez contacter le propriétaire pour le renouvellement."
                
                # Envoyer la notification
                notification_manager.send_notification(
                    message=message,
                    to_email=contract.tenant.email,
                    to_number=contract.tenant.phone,
                    subject="Contrat à renouveler"
                )
                
                # Notifier également le propriétaire
                notification_manager.send_notification(
                    message=f"Le contrat pour {contract.property.address} expire le {contract.end_date.strftime('%d/%m/%Y')}. Le locataire a été notifié.",
                    to_email=contract.property.owner.email,
                    to_number=contract.property.owner.phone,
                    subject="Contrat à renouveler"
                )
            
            logger.info(f"Notifications de renouvellement envoyées pour {len(contracts)} contrats")
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des contrats à renouveler : {str(e)}")
    
    def check_maintenance_requests(self, db: Session) -> None:
        """
        Vérifie les demandes de maintenance en attente.
        
        Args:
            db: Session de base de données
        """
        try:
            # Récupérer les demandes de maintenance en attente depuis plus de 24h
            threshold = datetime.now(timezone) - timedelta(days=1)
            requests = db.query(MaintenanceRequest).filter(
                MaintenanceRequest.created_at <= threshold,
                MaintenanceRequest.status == "pending"
            ).all()
            
            for request in requests:
                # Préparer le message
                message = f"La demande de maintenance pour {request.property.address} est en attente depuis plus de 24h. Priorité : {request.priority}"
                
                # Envoyer la notification au propriétaire
                notification_manager.send_notification(
                    message=message,
                    to_email=request.property.owner.email,
                    to_number=request.property.owner.phone,
                    subject="Demande de maintenance en attente"
                )
            
            logger.info(f"Notifications de maintenance envoyées pour {len(requests)} demandes")
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des demandes de maintenance : {str(e)}")
    
    def schedule_all_tasks(self, db: Session) -> None:
        """
        Planifie toutes les tâches récurrentes.
        
        Args:
            db: Session de base de données
        """
        # Rappels de paiement tous les jours à 9h
        self.scheduler.add_job(
            self.schedule_payment_reminders,
            CronTrigger(hour=9, minute=0, timezone=timezone),
            args=[db],
            id="payment_reminders"
        )
        
        # Vérification des contrats tous les lundis à 10h
        self.scheduler.add_job(
            self.check_contract_renewals,
            CronTrigger(day_of_week="mon", hour=10, minute=0, timezone=timezone),
            args=[db],
            id="contract_renewals"
        )
        
        # Vérification des demandes de maintenance toutes les 6 heures
        self.scheduler.add_job(
            self.check_maintenance_requests,
            CronTrigger(hour="*/6", timezone=timezone),
            args=[db],
            id="maintenance_requests"
        )
        
        logger.info("Toutes les tâches planifiées ont été configurées")
    
    def shutdown(self) -> None:
        """Arrête le planificateur de tâches."""
        self.scheduler.shutdown()
        logger.info("Planificateur de tâches arrêté")

# Instance globale du planificateur de tâches
task_scheduler = TaskScheduler() 