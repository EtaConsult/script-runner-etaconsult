# -*- coding: utf-8 -*-
"""
Client OneDrive pour gérer les fichiers via l'API Microsoft Graph
Permet de créer des dossiers et uploader des fichiers depuis PythonAnywhere
"""

import requests
import msal
import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class OneDriveClient:
    """
    Client pour interagir avec OneDrive via Microsoft Graph API

    Nécessite:
    - CLIENT_ID: Application (client) ID depuis Azure Portal
    - CLIENT_SECRET: Client secret depuis Azure Portal
    - TENANT_ID: Directory (tenant) ID depuis Azure Portal (ou 'common')
    """

    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    SCOPES = ["https://graph.microsoft.com/.default"]

    def __init__(self, client_id: str, client_secret: str, tenant_id: str = "common"):
        """
        Initialise le client OneDrive

        Args:
            client_id: Application (client) ID
            client_secret: Client secret value
            tenant_id: Tenant ID (ou 'common' pour multi-tenant)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.access_token = None

        # Créer l'application MSAL
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}"
        )

    def _get_access_token(self) -> str:
        """
        Obtient un access token via Client Credentials Flow

        Returns:
            Access token valide

        Raises:
            Exception: Si l'authentification échoue
        """
        if self.access_token:
            return self.access_token

        result = self.app.acquire_token_for_client(scopes=self.SCOPES)

        if "access_token" in result:
            self.access_token = result["access_token"]
            logger.info("✅ Authentification OneDrive réussie")
            return self.access_token
        else:
            error = result.get("error_description", result.get("error", "Unknown error"))
            logger.error(f"❌ Échec authentification OneDrive: {error}")
            raise Exception(f"Impossible d'obtenir le token OneDrive: {error}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Effectue une requête à l'API Graph

        Args:
            method: Méthode HTTP (GET, POST, PUT, etc.)
            endpoint: Endpoint de l'API (ex: '/me/drive/root/children')
            **kwargs: Arguments additionnels pour requests

        Returns:
            Response object
        """
        token = self._get_access_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        url = f"{self.GRAPH_API_ENDPOINT}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)

        return response

    def create_folder(self, folder_path: str, parent_path: str = "") -> Optional[Dict]:
        """
        Crée un dossier dans OneDrive

        Args:
            folder_path: Nom du dossier à créer
            parent_path: Chemin du parent (ex: "/Documents_Eta Consult/12. Dossiers actifs")
                        Vide = racine

        Returns:
            Dict avec les infos du dossier créé ou None si erreur
        """
        # Construire l'endpoint
        if parent_path:
            # Encoder le chemin pour l'URL
            encoded_path = ":/" + parent_path.strip("/") + ":"
            endpoint = f"/me/drive/root{encoded_path}/children"
        else:
            endpoint = "/me/drive/root/children"

        data = {
            "name": folder_path,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }

        response = self._make_request("POST", endpoint, json=data)

        if response.status_code in [200, 201]:
            folder_info = response.json()
            logger.info(f"✅ Dossier créé: {folder_path}")
            return folder_info
        elif response.status_code == 409:
            # Le dossier existe déjà
            logger.info(f"ℹ️  Dossier existant: {folder_path}")
            return {"name": folder_path, "id": None}
        else:
            logger.error(f"❌ Erreur création dossier {folder_path}: {response.status_code}")
            logger.error(response.text)
            return None

    def create_folder_structure(self, base_path: str, subfolders: List[str]) -> bool:
        """
        Crée une structure de dossiers imbriqués

        Args:
            base_path: Chemin de base (ex: "/Documents_Eta Consult/12. Dossiers actifs/202501_Projet")
            subfolders: Liste des sous-dossiers à créer

        Returns:
            True si succès, False sinon
        """
        success = True

        for subfolder in subfolders:
            full_path = f"{base_path}/{subfolder}"
            result = self.create_folder(Path(subfolder).name, str(Path(full_path).parent))
            if result is None:
                success = False

        return success

    def upload_file(self, file_content: bytes, file_name: str, destination_path: str = "") -> Optional[Dict]:
        """
        Upload un fichier dans OneDrive

        Args:
            file_content: Contenu du fichier en bytes
            file_name: Nom du fichier
            destination_path: Chemin de destination (ex: "/Documents_Eta Consult/12. Dossiers actifs")

        Returns:
            Dict avec les infos du fichier uploadé ou None si erreur
        """
        # Construire l'endpoint
        if destination_path:
            encoded_path = ":/" + destination_path.strip("/") + f"/{file_name}:/content"
            endpoint = f"/me/drive/root{encoded_path}"
        else:
            endpoint = f"/me/drive/root:/{file_name}:/content"

        headers = {"Content-Type": "application/octet-stream"}

        response = self._make_request("PUT", endpoint, headers=headers, data=file_content)

        if response.status_code in [200, 201]:
            file_info = response.json()
            logger.info(f"✅ Fichier uploadé: {file_name}")
            return file_info
        else:
            logger.error(f"❌ Erreur upload {file_name}: {response.status_code}")
            logger.error(response.text)
            return None

    def upload_text_file(self, content: str, file_name: str, destination_path: str = "") -> Optional[Dict]:
        """
        Upload un fichier texte dans OneDrive

        Args:
            content: Contenu texte
            file_name: Nom du fichier
            destination_path: Chemin de destination

        Returns:
            Dict avec les infos du fichier uploadé ou None si erreur
        """
        file_bytes = content.encode("utf-8")
        return self.upload_file(file_bytes, file_name, destination_path)

    def list_folder_contents(self, folder_path: str = "") -> Optional[List[Dict]]:
        """
        Liste le contenu d'un dossier

        Args:
            folder_path: Chemin du dossier (vide = racine)

        Returns:
            Liste des éléments ou None si erreur
        """
        if folder_path:
            encoded_path = ":/" + folder_path.strip("/") + ":/children"
            endpoint = f"/me/drive/root{encoded_path}"
        else:
            endpoint = "/me/drive/root/children"

        response = self._make_request("GET", endpoint)

        if response.status_code == 200:
            data = response.json()
            return data.get("value", [])
        else:
            logger.error(f"❌ Erreur listing dossier: {response.status_code}")
            return None

    def download_file(self, file_path: str) -> Optional[bytes]:
        """
        Télécharge un fichier depuis OneDrive

        Args:
            file_path: Chemin du fichier (ex: "/Documents/fichier.pdf")

        Returns:
            Contenu du fichier en bytes ou None si erreur
        """
        encoded_path = ":/" + file_path.strip("/") + ":/content"
        endpoint = f"/me/drive/root{encoded_path}"

        response = self._make_request("GET", endpoint)

        if response.status_code == 200:
            logger.info(f"✅ Fichier téléchargé: {file_path}")
            return response.content
        else:
            logger.error(f"❌ Erreur download {file_path}: {response.status_code}")
            return None

    def copy_file(self, source_path: str, destination_folder_path: str, new_name: Optional[str] = None) -> bool:
        """
        Copie un fichier vers un autre emplacement

        Args:
            source_path: Chemin source du fichier
            destination_folder_path: Chemin du dossier de destination
            new_name: Nouveau nom (optionnel)

        Returns:
            True si succès, False sinon
        """
        # Télécharger le fichier
        content = self.download_file(source_path)
        if content is None:
            return False

        # Uploader dans la nouvelle destination
        file_name = new_name or Path(source_path).name
        result = self.upload_file(content, file_name, destination_folder_path)

        return result is not None
