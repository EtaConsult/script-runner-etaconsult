# -*- coding: utf-8 -*-
"""
Gestionnaire de contacts Bexio
Gère la création et la recherche de contacts (Privé et Société)
"""

import logging
from typing import Dict, Optional
from bexio_client import BexioClient

logger = logging.getLogger(__name__)


class ContactManager:
    """
    Gère la création et la recherche de contacts dans Bexio

    Supporte deux types de contacts:
    - Privé: Personne physique
    - Société: Entreprise avec personne de contact associée
    """

    def __init__(self, bexio_client: BexioClient, config: dict):
        """
        Initialise le gestionnaire de contacts

        Args:
            bexio_client: Instance du client Bexio
            config: Configuration contenant CONTACT_TYPES, SALUTATIONS, BEXIO_IDS
        """
        self.bexio = bexio_client
        self.contact_types = config.get("CONTACT_TYPES", {"Privé": 1, "Société": 2})
        self.salutations = config.get("SALUTATIONS", {"Mme": 1, "M.": 2, "Mx": None})
        self.bexio_ids = config.get("BEXIO_IDS", {})

    # ==========================================
    # MÉTHODE PRINCIPALE
    # ==========================================

    def get_or_create_contact(self, form_data: dict) -> Dict[str, Optional[int]]:
        """
        Récupère ou crée un contact selon le type

        Args:
            form_data: Données du formulaire contenant les infos de contact

        Returns:
            Dict avec:
                - contact_id: ID du contact principal (privé ou entreprise)
                - contact_sub_id: ID de la personne associée (None si privé)
        """
        # Normaliser le type de contact (retirer espaces avant/après)
        type_contact = form_data.get("type_contact", "").strip()

        logger.info(f"   🔍 type_contact reçu: repr={repr(type_contact)}")

        if type_contact == "Privé":
            return self._handle_private_contact(form_data)
        elif type_contact == "Société":
            return self._handle_company_contact(form_data)
        else:
            raise ValueError(
                f"Type de contact non reconnu: {repr(type_contact)}. "
                f"Valeurs attendues: 'Privé' ou 'Société'"
            )

    # ==========================================
    # GESTION CONTACT PRIVÉ
    # ==========================================

    def _handle_private_contact(self, data: dict) -> Dict[str, Optional[int]]:
        """
        Gère la création/récupération d'un contact privé

        Args:
            data: Données du formulaire

        Returns:
            Dict avec contact_id et contact_sub_id (None)
        """
        logger.info(f"👤 Gestion contact privé: {data['prenom']} {data['nom_famille']}")

        # Chercher par email si fourni
        contact = None
        if data.get("email"):
            found_contact = self._search_contact_by_email(data["email"])
            # Vérifier que le contact trouvé est bien de type Privé (type_id = 1)
            if found_contact and found_contact.get("contact_type_id") == self.contact_types["Privé"]:
                contact = found_contact
                logger.info(f"   → Contact privé existant trouvé par email (ID: {contact['id']})")
            elif found_contact:
                logger.info(f"   → Contact trouvé par email mais mauvais type ({found_contact.get('contact_type_id')}), création d'un nouveau contact")

        if not contact:
            logger.info(f"   → Création d'un nouveau contact privé")
            contact = self._create_private_contact(data)
        else:
            logger.info(f"   → Contact existant trouvé (ID: {contact['id']})")

        return {
            "contact_id": contact["id"],
            "contact_sub_id": None
        }

    def _create_private_contact(self, data: dict) -> dict:
        """
        Crée un contact privé dans Bexio

        Args:
            data: Données du formulaire

        Returns:
            Contact créé
        """
        contact_type_prive = self.contact_types.get("Privé", 1)

        payload = {
            "contact_type_id": contact_type_prive,
            "name_1": data["nom_famille"],
            "name_2": data["prenom"],
            "postcode": data["npa_facturation"],
            "city": data["localite_facturation"],
            "country_id": self.bexio_ids.get("country_id", 1),
            "language_id": self.bexio_ids.get("language_id", 2),
            "user_id": self.bexio_ids.get("user_id", 1),
            "owner_id": self.bexio_ids.get("user_id", 1),
        }

        # NOTE: Le champ "address" n'est PAS accepté lors de la création (erreur 422)
        # Bexio semble gérer l'adresse via d'autres mécanismes ou endpoints
        # TODO: Vérifier si on peut mettre à jour l'adresse après création

        # Ajouter l'email si fourni
        if data.get("email"):
            payload["mail"] = data["email"]

        # Ajouter le téléphone si fourni
        if data.get("telephone"):
            payload["phone_mobile"] = data["telephone"]

        # Ajouter la salutation si fournie
        salutation_id = self._get_salutation_id(data.get("appellation"))
        if salutation_id is not None:
            payload["salutation_id"] = salutation_id

        logger.info(f"   📤 Payload contact privé complet: {payload}")

        # Créer le contact
        created_contact = self.bexio.create_contact(payload)

        # Vérifier immédiatement le type du contact créé
        logger.info(f"   ✅ Contact créé - ID: {created_contact.get('id')}, contact_type_id: {created_contact.get('contact_type_id')}")

        if created_contact.get("contact_type_id") != contact_type_prive:
            logger.error(f"   ❌ ALERTE: Contact créé avec mauvais type! Attendu: {contact_type_prive}, Reçu: {created_contact.get('contact_type_id')}")

        # Mettre à jour l'adresse via un UPDATE (car POST ne l'accepte pas)
        try:
            logger.info(f"   🔄 Mise à jour de l'adresse du contact...")
            update_payload = {
                "address": data["rue_facturation"]
            }
            updated_contact = self.bexio.update_contact(created_contact['id'], update_payload)
            logger.info(f"   ✅ Adresse mise à jour: {data['rue_facturation']}")
            return updated_contact
        except Exception as e:
            logger.warning(f"   ⚠️  Impossible de mettre à jour l'adresse: {e}")
            return created_contact

    # ==========================================
    # GESTION CONTACT SOCIÉTÉ
    # ==========================================

    def _handle_company_contact(self, data: dict) -> Dict[str, Optional[int]]:
        """
        Gère la création/récupération d'une entreprise + personne associée

        Args:
            data: Données du formulaire

        Returns:
            Dict avec contact_id (entreprise) et contact_sub_id (personne)
        """
        logger.info(f"🏢 Gestion contact entreprise: {data['nom_entreprise']}")

        # 1. Chercher/créer l'entreprise
        company = self._search_contact_by_name(
            data["nom_entreprise"],
            contact_type=self.contact_types["Société"]
        )

        if not company:
            logger.info(f"   → Création d'une nouvelle entreprise")
            company = self._create_company_contact(data)
        else:
            logger.info(f"   → Entreprise existante trouvée (ID: {company['id']})")

        # 2. Chercher/créer la personne de contact
        person = None
        if data.get("email"):
            person = self._search_contact_by_email(data["email"])

        if not person:
            logger.info(f"   → Création d'un nouveau contact pour {data['prenom']} {data['nom_famille']}")
            person = self._create_private_contact(data)
        else:
            logger.info(f"   → Personne existante trouvée (ID: {person['id']})")

        # 3. Créer l'association si elle n'existe pas
        self._ensure_contact_relation(company["id"], person["id"])

        return {
            "contact_id": company["id"],
            "contact_sub_id": person["id"]
        }

    def _create_company_contact(self, data: dict) -> dict:
        """
        Crée un contact entreprise dans Bexio

        Args:
            data: Données du formulaire

        Returns:
            Contact entreprise créé
        """
        payload = {
            "contact_type_id": self.contact_types["Société"],
            "name_1": data["nom_entreprise"],
            "postcode": data["npa_facturation"],
            "city": data["localite_facturation"],
            "country_id": self.bexio_ids.get("country_id", 1),
            "user_id": self.bexio_ids.get("user_id", 1),
            "owner_id": self.bexio_ids.get("user_id", 1),
        }

        # NOTE: Le champ "address" n'est PAS accepté lors de la création (erreur 422)

        logger.debug(f"   📤 Payload entreprise: {payload}")
        created_company = self.bexio.create_contact(payload)

        # Mettre à jour l'adresse via un UPDATE
        try:
            logger.info(f"   🔄 Mise à jour de l'adresse de l'entreprise...")
            update_payload = {
                "address": data["rue_facturation"]
            }
            updated_company = self.bexio.update_contact(created_company['id'], update_payload)
            logger.info(f"   ✅ Adresse mise à jour: {data['rue_facturation']}")
            return updated_company
        except Exception as e:
            logger.warning(f"   ⚠️  Impossible de mettre à jour l'adresse: {e}")
            return created_company

    def _ensure_contact_relation(self, company_id: int, person_id: int):
        """
        Vérifie et crée l'association entreprise-personne si nécessaire

        Args:
            company_id: ID de l'entreprise
            person_id: ID de la personne
        """
        try:
            # Récupérer les relations existantes
            relations = self.bexio.get_contact_relations(company_id)

            # Vérifier si l'association existe déjà
            for rel in relations:
                if rel.get("contact_sub_id") == person_id:
                    logger.info(f"   → Association entreprise-personne déjà existante")
                    return

            # Créer l'association
            self.bexio.create_contact_relation(company_id, person_id)
            logger.info(f"   → Association entreprise-personne créée")

        except Exception as e:
            logger.warning(f"⚠️  Erreur lors de la création de l'association: {e}")

    # ==========================================
    # RECHERCHE
    # ==========================================

    def _search_contact_by_email(self, email: str) -> Optional[dict]:
        """
        Recherche un contact par email

        Args:
            email: Adresse email

        Returns:
            Contact trouvé ou None
        """
        if not email:
            return None

        try:
            results = self.bexio.search_contacts(email)
            if not results:
                return None

            # Filtrer pour trouver la correspondance exacte
            for contact in results:
                contact_email = contact.get("mail") or ""
                if contact_email.lower() == email.lower():
                    return contact

        except Exception as e:
            logger.warning(f"⚠️  Erreur lors de la recherche par email: {e}")

        return None

    def _search_contact_by_name(
        self,
        name: str,
        contact_type: Optional[int] = None
    ) -> Optional[dict]:
        """
        Recherche un contact par nom

        Args:
            name: Nom à rechercher
            contact_type: Type de contact (1=Privé, 2=Société) ou None

        Returns:
            Contact trouvé ou None
        """
        if not name:
            return None

        try:
            results = self.bexio.search_contacts(name)
            if not results:
                return None

            # Filtrer pour trouver la correspondance exacte
            for contact in results:
                if contact.get("name_1", "").lower() == name.lower():
                    if contact_type is None or contact.get("contact_type_id") == contact_type:
                        return contact

        except Exception as e:
            logger.warning(f"⚠️  Erreur lors de la recherche par nom: {e}")

        return None

    # ==========================================
    # UTILITAIRES
    # ==========================================

    def _get_salutation_id(self, appellation: Optional[str]) -> Optional[int]:
        """
        Convertit l'appellation en salutation_id Bexio

        Args:
            appellation: "Mme", "M." ou "Mx"

        Returns:
            ID de salutation ou None
        """
        if not appellation:
            return None

        return self.salutations.get(appellation)
