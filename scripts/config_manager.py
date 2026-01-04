# -*- coding: utf-8 -*-
"""
Gestionnaire de configuration robuste pour le script de création de devis
Gère le chargement des tarifs, textes et configuration depuis différentes sources
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Gestionnaire centralisé de configuration

    Charge les paramètres depuis:
    1. tarifs.json (si disponible)
    2. textes.json (si disponible)
    3. config.py (fallback)
    """

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialise le gestionnaire de configuration

        Args:
            base_dir: Répertoire de base (par défaut: répertoire parent du script)
        """
        if base_dir is None:
            # Remonter au répertoire parent (depuis scripts/ vers la racine)
            base_dir = Path(__file__).parent.parent

        self.base_dir = Path(base_dir)
        self.tarifs_file = self.base_dir / "tarifs.json"
        self.textes_file = self.base_dir / "textes.json"

        # Charger la configuration
        self.tarifs = self._load_tarifs()
        self.textes = self._load_textes()

        # Charger le module config pour les autres paramètres
        self.config_module = self._load_config_module()

    def _load_config_module(self):
        """Charge le module config.py"""
        try:
            import sys
            parent_dir = str(self.base_dir)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)

            import config
            return config
        except ImportError:
            logger.error("❌ Fichier config.py non trouvé!")
            raise

    def _load_tarifs(self) -> Dict[str, Any]:
        """
        Charge les tarifs depuis tarifs.json si disponible, sinon depuis config.py

        Returns:
            Dictionnaire des tarifs
        """
        if self.tarifs_file.exists():
            try:
                with open(self.tarifs_file, 'r', encoding='utf-8') as f:
                    tarifs = json.load(f)
                    logger.info(f"✅ Tarifs chargés depuis {self.tarifs_file}")
                    return tarifs
            except Exception as e:
                logger.warning(f"⚠️  Erreur lecture tarifs.json: {e}")
                logger.info("📋 Utilisation des tarifs par défaut de config.py")

        # Fallback vers config.py
        try:
            import config
            return config.TARIFS
        except (ImportError, AttributeError):
            logger.error("❌ Impossible de charger les tarifs")
            return self._get_default_tarifs()

    def _load_textes(self) -> Dict[str, str]:
        """
        Charge les textes depuis textes.json si disponible, sinon depuis config.py

        Returns:
            Dictionnaire des textes
        """
        if self.textes_file.exists():
            try:
                with open(self.textes_file, 'r', encoding='utf-8') as f:
                    textes = json.load(f)
                    logger.info(f"✅ Textes chargés depuis {self.textes_file}")
                    return textes
            except Exception as e:
                logger.warning(f"⚠️  Erreur lecture textes.json: {e}")
                logger.info("📋 Utilisation des textes par défaut de config.py")

        # Fallback vers config.py
        try:
            import config
            return config.TEXTES
        except (ImportError, AttributeError):
            logger.error("❌ Impossible de charger les textes")
            return self._get_default_textes()

    def _get_default_tarifs(self) -> Dict[str, Any]:
        """Retourne les tarifs par défaut en cas d'erreur"""
        return {
            "base_price": 500,
            "km_factor_proche": 0.9,
            "km_factor_loin": 0.7,
            "km_seuil": 25,
            "surface_factor_petit": 0.6,
            "surface_factor_grand": 0.5,
            "surface_seuil": 750,
            "plus_factor": 1.4,
            "plus_price_max": 1989,
            "frais_emission_cecb": 80,
            "prix_conseil_incitatif": 0,
            "forfait_normal": 0,
            "forfait_express": 135,
            "forfait_urgent": 270,
            "pct_acompte": 30
        }

    def _get_default_textes(self) -> Dict[str, str]:
        """Retourne les textes par défaut en cas d'erreur"""
        return {
            "footer_acompte": "Conditions de paiement : Acompte de 30% à la commande, solde à réception du rapport.",
            "prestations_incluses_cecb": "Prestations incluses pour CECB",
            "prestations_non_incluses_cecb": "Prestations non-incluses",
            "prestations_incluses_cecb_plus": "Prestations incluses pour CECB Plus",
            "prestations_incluses_conseil": "Prestations incluses pour Conseil Incitatif"
        }

    # ==========================================
    # ACCESSEURS POUR TARIFS
    # ==========================================

    def get_tarif(self, key: str, default: Any = None) -> Any:
        """
        Récupère un tarif avec fallback

        Args:
            key: Clé du tarif
            default: Valeur par défaut si non trouvée

        Returns:
            Valeur du tarif ou default
        """
        return self.tarifs.get(key, default)

    def get_all_tarifs(self) -> Dict[str, Any]:
        """Retourne tous les tarifs"""
        return self.tarifs.copy()

    # ==========================================
    # ACCESSEURS POUR TEXTES
    # ==========================================

    def get_texte(self, key: str, default: str = "") -> str:
        """
        Récupère un texte avec fallback

        Args:
            key: Clé du texte
            default: Valeur par défaut si non trouvée

        Returns:
            Texte ou default
        """
        return self.textes.get(key, default)

    def get_all_textes(self) -> Dict[str, str]:
        """Retourne tous les textes"""
        return self.textes.copy()

    # ==========================================
    # ACCESSEURS POUR CONFIG MODULE
    # ==========================================

    def get_bexio_api_token(self) -> str:
        """Retourne le token API Bexio"""
        return getattr(self.config_module, 'BEXIO_API_TOKEN', '')

    def get_google_maps_api_key(self) -> str:
        """Retourne la clé API Google Maps"""
        return getattr(self.config_module, 'GOOGLE_MAPS_API_KEY', '')

    def get_bexio_base_url(self) -> str:
        """Retourne l'URL de base Bexio"""
        return getattr(self.config_module, 'BEXIO_BASE_URL', 'https://api.bexio.com')

    def get_eta_consult_address(self) -> str:
        """Retourne l'adresse d'Êta Consult"""
        return getattr(self.config_module, 'ETA_CONSULT_ADDRESS', 'Route de l\'Hôpital 16b, 1180 Rolle, Suisse')

    def get_bexio_ids(self) -> Dict[str, Any]:
        """Retourne les IDs Bexio"""
        return getattr(self.config_module, 'BEXIO_IDS', {})

    def get_contact_types(self) -> Dict[str, int]:
        """Retourne les types de contact Bexio"""
        return getattr(self.config_module, 'CONTACT_TYPES', {"Privé": 1, "Société": 2})

    def get_salutations(self) -> Dict[str, Optional[int]]:
        """Retourne les salutations Bexio"""
        return getattr(self.config_module, 'SALUTATIONS', {"Mme": 1, "M.": 2, "Mx": None})

    # ==========================================
    # SAUVEGARDE
    # ==========================================

    def save_tarifs(self, tarifs: Dict[str, Any]) -> bool:
        """
        Sauvegarde les tarifs dans tarifs.json

        Args:
            tarifs: Dictionnaire des tarifs à sauvegarder

        Returns:
            True si succès, False sinon
        """
        try:
            with open(self.tarifs_file, 'w', encoding='utf-8') as f:
                json.dump(tarifs, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Tarifs sauvegardés dans {self.tarifs_file}")
            self.tarifs = tarifs
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde des tarifs: {e}")
            return False

    def save_textes(self, textes: Dict[str, str]) -> bool:
        """
        Sauvegarde les textes dans textes.json

        Args:
            textes: Dictionnaire des textes à sauvegarder

        Returns:
            True si succès, False sinon
        """
        try:
            with open(self.textes_file, 'w', encoding='utf-8') as f:
                json.dump(textes, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Textes sauvegardés dans {self.textes_file}")
            self.textes = textes
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde des textes: {e}")
            return False

    # ==========================================
    # VALIDATION
    # ==========================================

    def validate_config(self) -> bool:
        """
        Valide que tous les paramètres essentiels sont présents

        Returns:
            True si configuration valide

        Raises:
            ValueError: Si configuration incomplète
        """
        # Vérifier les tokens
        if not self.get_bexio_api_token():
            raise ValueError("BEXIO_API_TOKEN manquant dans config.py")

        if not self.get_google_maps_api_key():
            logger.warning("⚠️  GOOGLE_MAPS_API_KEY manquant - calcul de distance désactivé")

        # Vérifier les tarifs essentiels
        essential_tarifs = [
            "base_price", "frais_emission_cecb", "plus_factor",
            "surface_factor_petit", "surface_factor_grand", "km_factor_proche", "km_factor_loin"
        ]

        for key in essential_tarifs:
            if key not in self.tarifs:
                raise ValueError(f"Tarif essentiel manquant: {key}")

        logger.info("✅ Configuration validée avec succès")
        return True
