import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict, Any
import requests
from app.core.config import settings
from app.core.exceptions import NotificationException
from app.core.logging import get_logger

logger = get_logger(__name__)

class NotificationManager:
    """Gestionnaire de notifications."""
    
    def __init__(self):
        """Initialise le gestionnaire de notifications."""
        self.smtp_settings = {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "username": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
            "tls": settings.SMTP_TLS
        }
        self.sms_settings = {
            "provider": settings.SMS_PROVIDER,
            "api_key": settings.SMS_API_KEY,
            "from_number": settings.SMS_FROM_NUMBER
        }
    
    def _create_email_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Crée un message email.
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            body: Corps du message en texte brut
            html_body: Corps du message en HTML (optionnel)
            
        Returns:
            MIMEMultipart: Message email
        """
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.EMAILS_FROM_EMAIL
        message["To"] = to_email
        
        # Ajouter le corps en texte brut
        message.attach(MIMEText(body, "plain"))
        
        # Ajouter le corps en HTML si fourni
        if html_body:
            message.attach(MIMEText(html_body, "html"))
        
        return message
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> None:
        """
        Envoie un email.
        
        Args:
            to_email: Adresse email du destinataire
            subject: Sujet de l'email
            body: Corps du message en texte brut
            html_body: Corps du message en HTML (optionnel)
            
        Raises:
            NotificationException: Si une erreur survient lors de l'envoi
        """
        try:
            # Créer le message
            message = self._create_email_message(to_email, subject, body, html_body)
            
            # Configurer la connexion SMTP
            with smtplib.SMTP(self.smtp_settings["host"], self.smtp_settings["port"]) as server:
                if self.smtp_settings["tls"]:
                    server.starttls()
                
                # Authentification
                if self.smtp_settings["username"] and self.smtp_settings["password"]:
                    server.login(
                        self.smtp_settings["username"],
                        self.smtp_settings["password"]
                    )
                
                # Envoyer l'email
                server.send_message(message)
            
            logger.info(f"Email envoyé à {to_email}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email : {str(e)}")
            raise NotificationException(f"Erreur lors de l'envoi de l'email : {str(e)}")
    
    def send_sms(
        self,
        to_number: str,
        message: str,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Envoie un SMS.
        
        Args:
            to_number: Numéro de téléphone du destinataire
            message: Message à envoyer
            template_id: ID du template (optionnel)
            template_data: Données pour le template (optionnel)
            
        Raises:
            NotificationException: Si une erreur survient lors de l'envoi
        """
        try:
            # Préparer les données de la requête
            data = {
                "to": to_number,
                "from": self.sms_settings["from_number"],
                "message": message
            }
            
            if template_id:
                data["template_id"] = template_id
            
            if template_data:
                data["template_data"] = template_data
            
            # Envoyer la requête à l'API du fournisseur SMS
            response = requests.post(
                f"https://api.{self.sms_settings['provider']}.com/sms/send",
                json=data,
                headers={
                    "Authorization": f"Bearer {self.sms_settings['api_key']}",
                    "Content-Type": "application/json"
                }
            )
            
            # Vérifier la réponse
            response.raise_for_status()
            
            logger.info(f"SMS envoyé à {to_number}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du SMS : {str(e)}")
            raise NotificationException(f"Erreur lors de l'envoi du SMS : {str(e)}")
    
    def send_notification(
        self,
        message: str,
        to_email: Optional[str] = None,
        to_number: Optional[str] = None,
        subject: Optional[str] = None,
        html_message: Optional[str] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Envoie une notification par email et/ou SMS.
        
        Args:
            message: Message à envoyer
            to_email: Adresse email du destinataire (optionnel)
            to_number: Numéro de téléphone du destinataire (optionnel)
            subject: Sujet de l'email (optionnel)
            html_message: Message HTML pour l'email (optionnel)
            template_id: ID du template SMS (optionnel)
            template_data: Données pour le template SMS (optionnel)
            
        Raises:
            NotificationException: Si une erreur survient lors de l'envoi
        """
        if not to_email and not to_number:
            raise NotificationException("Aucun destinataire spécifié")
        
        # Envoyer l'email si une adresse est fournie
        if to_email and subject:
            self.send_email(to_email, subject, message, html_message)
        
        # Envoyer le SMS si un numéro est fourni
        if to_number:
            self.send_sms(to_number, message, template_id, template_data)
    
    def send_bulk_notification(
        self,
        message: str,
        recipients: List[Dict[str, str]],
        subject: Optional[str] = None,
        html_message: Optional[str] = None,
        template_id: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Envoie une notification à plusieurs destinataires.
        
        Args:
            message: Message à envoyer
            recipients: Liste des destinataires avec leurs coordonnées
            subject: Sujet de l'email (optionnel)
            html_message: Message HTML pour l'email (optionnel)
            template_id: ID du template SMS (optionnel)
            template_data: Données pour le template SMS (optionnel)
            
        Raises:
            NotificationException: Si une erreur survient lors de l'envoi
        """
        for recipient in recipients:
            try:
                self.send_notification(
                    message=message,
                    to_email=recipient.get("email"),
                    to_number=recipient.get("phone"),
                    subject=subject,
                    html_message=html_message,
                    template_id=template_id,
                    template_data=template_data
                )
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de la notification : {str(e)}")
                # Continuer avec les autres destinataires
                continue

# Instance globale du gestionnaire de notifications
notification_manager = NotificationManager() 