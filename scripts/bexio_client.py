# -*- coding: utf-8 -*-
"""
Client API Bexio avec gestion d'erreurs robuste et logging
"""

import requests
import logging
import json
from typing import Dict, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)


# ==========================================
# DÉCORATEUR POUR GESTION D'ERREURS
# ==========================================

def safe_api_call(func):
    """Décorateur pour gérer les erreurs API de manière robuste"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout lors de l'appel API: {func.__name__}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Erreur de connexion lors de l'appel API: {func.__name__}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur API dans {func.__name__}: {e}")
            raise
    return wrapper


# ==========================================
# CLIENT BEXIO
# ==========================================

class BexioClient:
    """
    Client pour interagir avec l'API Bexio v2.0

    Gère toutes les requêtes HTTP vers Bexio avec:
    - Gestion d'erreurs robuste
    - Logging détaillé
    - Timeout configuré
    - Headers standardisés
    """

    def __init__(self, api_token: str, base_url: str = "https://api.bexio.com"):
        """
        Initialise le client Bexio

        Args:
            api_token: Token d'authentification Bexio
            base_url: URL de base de l'API (par défaut: https://api.bexio.com)
        """
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        self.timeout = 30  # Timeout en secondes

    @safe_api_call
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Effectue une requête GET vers l'API Bexio

        Args:
            endpoint: Endpoint API (ex: "/2.0/contact")
            params: Paramètres de requête optionnels

        Returns:
            Réponse JSON de l'API

        Raises:
            requests.exceptions.RequestException: En cas d'erreur HTTP
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GET {url} avec params: {params}")

        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()

        return response.json()

    @safe_api_call
    def post(self, endpoint: str, data: Dict) -> Any:
        """
        Effectue une requête POST vers l'API Bexio

        Args:
            endpoint: Endpoint API (ex: "/2.0/contact")
            data: Données à envoyer (dict Python, sera converti en JSON)

        Returns:
            Réponse JSON de l'API

        Raises:
            requests.exceptions.RequestException: En cas d'erreur HTTP
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"POST {url}")
        logger.debug(f"Payload: {json.dumps(data, indent=2, ensure_ascii=False)}")

        response = requests.post(
            url,
            headers=self.headers,
            json=data,
            timeout=self.timeout
        )

        # Gestion détaillée des erreurs
        if not response.ok:
            logger.error(f"❌ Erreur POST {endpoint}")
            logger.error(f"   Status code: {response.status_code}")
            logger.error(f"   Réponse: {response.text}")

            # Tenter de parser la réponse JSON pour plus de détails
            try:
                error_detail = response.json()
                logger.error(f"   Détails: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                pass

            response.raise_for_status()

        return response.json()

    @safe_api_call
    def put(self, endpoint: str, data: Dict) -> Any:
        """
        Effectue une requête PUT vers l'API Bexio

        Args:
            endpoint: Endpoint API
            data: Données à mettre à jour

        Returns:
            Réponse JSON de l'API

        Raises:
            requests.exceptions.RequestException: En cas d'erreur HTTP
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PUT {url}")

        response = requests.put(
            url,
            headers=self.headers,
            json=data,
            timeout=self.timeout
        )
        response.raise_for_status()

        return response.json()

    @safe_api_call
    def patch(self, endpoint: str, data: Dict) -> Any:
        """
        Effectue une requête PATCH vers l'API Bexio

        Args:
            endpoint: Endpoint API
            data: Données à mettre à jour (mise à jour partielle)

        Returns:
            Réponse JSON de l'API

        Raises:
            requests.exceptions.RequestException: En cas d'erreur HTTP
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"PATCH {url}")
        logger.debug(f"Payload: {json.dumps(data, indent=2, ensure_ascii=False)}")

        response = requests.patch(
            url,
            headers=self.headers,
            json=data,
            timeout=self.timeout
        )

        # Gestion détaillée des erreurs
        if not response.ok:
            logger.error(f"❌ Erreur PATCH {endpoint}")
            logger.error(f"   Status code: {response.status_code}")
            logger.error(f"   Réponse: {response.text}")

            # Tenter de parser la réponse JSON pour plus de détails
            try:
                error_detail = response.json()
                logger.error(f"   Détails: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                pass

            response.raise_for_status()

        return response.json()

    @safe_api_call
    def delete(self, endpoint: str) -> Any:
        """
        Effectue une requête DELETE vers l'API Bexio

        Args:
            endpoint: Endpoint API

        Returns:
            Réponse JSON de l'API

        Raises:
            requests.exceptions.RequestException: En cas d'erreur HTTP
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"DELETE {url}")

        response = requests.delete(
            url,
            headers=self.headers,
            timeout=self.timeout
        )
        response.raise_for_status()

        return response.json()

    # ==========================================
    # MÉTHODES SPÉCIFIQUES BEXIO
    # ==========================================

    def search_contacts(self, search_term: str) -> list:
        """
        Recherche des contacts par terme de recherche

        Args:
            search_term: Terme à rechercher (nom, email, etc.)

        Returns:
            Liste de contacts trouvés
        """
        return self.get("/2.0/contact", params={"search": search_term})

    def create_contact(self, contact_data: Dict) -> Dict:
        """
        Crée un nouveau contact dans Bexio

        Args:
            contact_data: Données du contact

        Returns:
            Contact créé
        """
        return self.post("/2.0/contact", contact_data)

    def get_contact(self, contact_id: int) -> Dict:
        """
        Récupère un contact par son ID

        Args:
            contact_id: ID du contact

        Returns:
            Données du contact
        """
        return self.get(f"/2.0/contact/{contact_id}")

    def update_contact(self, contact_id: int, contact_data: Dict) -> Dict:
        """
        Met à jour un contact dans Bexio

        Args:
            contact_id: ID du contact
            contact_data: Données à mettre à jour

        Returns:
            Contact mis à jour
        """
        return self.patch(f"/2.0/contact/{contact_id}", contact_data)

    def create_quote(self, quote_data: Dict) -> Dict:
        """
        Crée une offre dans Bexio

        Args:
            quote_data: Données de l'offre

        Returns:
            Offre créée
        """
        return self.post("/2.0/kb_offer", quote_data)

    def get_quote(self, quote_id: int) -> Dict:
        """
        Récupère une offre par son ID

        Args:
            quote_id: ID de l'offre

        Returns:
            Données de l'offre
        """
        return self.get(f"/2.0/kb_offer/{quote_id}")

    def create_contact_relation(self, company_id: int, person_id: int) -> Dict:
        """
        Crée une relation entre une entreprise et une personne

        Args:
            company_id: ID de l'entreprise
            person_id: ID de la personne

        Returns:
            Relation créée
        """
        payload = {
            "contact_sub_id": person_id,
            "description": "Personne de contact"
        }
        return self.post(f"/2.0/contact/{company_id}/contact_relation", payload)

    def get_contact_relations(self, company_id: int) -> list:
        """
        Récupère les relations d'un contact

        Args:
            company_id: ID de l'entreprise

        Returns:
            Liste des relations
        """
        return self.get(f"/2.0/contact/{company_id}/contact_relation")
