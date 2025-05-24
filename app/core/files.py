import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile
from app.core.config import settings
from app.core.exceptions import FileException, InvalidFileTypeException, FileTooLargeException
from app.core.validators import FileValidator
from app.core.logging import get_logger

logger = get_logger(__name__)

class FileManager:
    """Gestionnaire de fichiers."""
    
    def __init__(self):
        """Initialise le gestionnaire de fichiers."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self._ensure_upload_dir()
    
    def _ensure_upload_dir(self) -> None:
        """Crée le répertoire de téléchargement s'il n'existe pas."""
        try:
            self.upload_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Erreur lors de la création du répertoire de téléchargement : {str(e)}")
            raise FileException("Impossible de créer le répertoire de téléchargement")
    
    def _get_file_path(self, filename: str) -> Path:
        """
        Génère un chemin de fichier unique.
        
        Args:
            filename: Nom du fichier
            
        Returns:
            Path: Chemin du fichier
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(filename)
        return self.upload_dir / f"{name}_{timestamp}{ext}"
    
    def _validate_file(self, file: UploadFile) -> None:
        """
        Valide un fichier.
        
        Args:
            file: Fichier à valider
            
        Raises:
            InvalidFileTypeException: Si le type de fichier est invalide
            FileTooLargeException: Si le fichier est trop volumineux
        """
        # Vérifier le type de fichier
        content_type = file.content_type
        if content_type not in settings.ALLOWED_EXTENSIONS:
            raise InvalidFileTypeException(list(settings.ALLOWED_EXTENSIONS))
        
        # Vérifier la taille du fichier
        file_size = 0
        for chunk in file.file:
            file_size += len(chunk)
            if file_size > settings.MAX_UPLOAD_SIZE:
                raise FileTooLargeException(settings.MAX_UPLOAD_SIZE)
        
        # Réinitialiser le curseur du fichier
        file.file.seek(0)
    
    async def save_file(self, file: UploadFile) -> Tuple[Path, str]:
        """
        Sauvegarde un fichier.
        
        Args:
            file: Fichier à sauvegarder
            
        Returns:
            Tuple[Path, str]: Chemin du fichier et type MIME
            
        Raises:
            FileException: Si une erreur survient lors de la sauvegarde
        """
        try:
            # Valider le fichier
            self._validate_file(file)
            
            # Générer un chemin unique
            file_path = self._get_file_path(file.filename)
            
            # Sauvegarder le fichier
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Fichier sauvegardé : {file_path}")
            return file_path, file.content_type
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du fichier : {str(e)}")
            raise FileException(f"Erreur lors de la sauvegarde du fichier : {str(e)}")
    
    def delete_file(self, file_path: Path) -> None:
        """
        Supprime un fichier.
        
        Args:
            file_path: Chemin du fichier
            
        Raises:
            FileException: Si une erreur survient lors de la suppression
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Fichier supprimé : {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier : {str(e)}")
            raise FileException(f"Erreur lors de la suppression du fichier : {str(e)}")
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        Obtient les informations d'un fichier.
        
        Args:
            file_path: Chemin du fichier
            
        Returns:
            dict: Informations du fichier
            
        Raises:
            FileException: Si une erreur survient lors de la récupération des informations
        """
        try:
            if not file_path.exists():
                raise FileException("Fichier non trouvé")
            
            stats = file_path.stat()
            return {
                "name": file_path.name,
                "size": stats.st_size,
                "created_at": datetime.fromtimestamp(stats.st_ctime),
                "modified_at": datetime.fromtimestamp(stats.st_mtime)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des informations du fichier : {str(e)}")
            raise FileException(f"Erreur lors de la récupération des informations du fichier : {str(e)}")
    
    def list_files(self, directory: Optional[Path] = None) -> list:
        """
        Liste les fichiers d'un répertoire.
        
        Args:
            directory: Répertoire à lister (optionnel)
            
        Returns:
            list: Liste des fichiers
            
        Raises:
            FileException: Si une erreur survient lors de la liste des fichiers
        """
        try:
            dir_path = directory or self.upload_dir
            if not dir_path.exists():
                raise FileException("Répertoire non trouvé")
            
            files = []
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    files.append(self.get_file_info(file_path))
            
            return files
        except Exception as e:
            logger.error(f"Erreur lors de la liste des fichiers : {str(e)}")
            raise FileException(f"Erreur lors de la liste des fichiers : {str(e)}")
    
    def create_directory(self, directory: Path) -> None:
        """
        Crée un répertoire.
        
        Args:
            directory: Chemin du répertoire
            
        Raises:
            FileException: Si une erreur survient lors de la création du répertoire
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Répertoire créé : {directory}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du répertoire : {str(e)}")
            raise FileException(f"Erreur lors de la création du répertoire : {str(e)}")
    
    def delete_directory(self, directory: Path) -> None:
        """
        Supprime un répertoire.
        
        Args:
            directory: Chemin du répertoire
            
        Raises:
            FileException: Si une erreur survient lors de la suppression du répertoire
        """
        try:
            if directory.exists():
                shutil.rmtree(directory)
                logger.info(f"Répertoire supprimé : {directory}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du répertoire : {str(e)}")
            raise FileException(f"Erreur lors de la suppression du répertoire : {str(e)}")

# Instance globale du gestionnaire de fichiers
file_manager = FileManager() 