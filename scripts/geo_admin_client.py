# -*- coding: utf-8 -*-
"""
Client API geo.admin.ch pour récupérer les données de bâtiments
Avec système de cache pour optimiser les performances
"""

import requests
import logging
from typing import Optional, Dict
from functools import lru_cache
from datetime import datetime

logger = logging.getLogger(__name__)


class GeoAdminClient:
    """
    Client pour récupérer les données de bâtiment via l'API geo.admin.ch

    Utilise le Registre fédéral des bâtiments et des logements (RegBL) via:
    - SearchServer pour la recherche par adresse
    - MapServer pour récupérer les détails complets

    Inclut un système de cache LRU pour optimiser les performances.
    """

    BASE_URL = "https://api3.geo.admin.ch/rest/services/api/SearchServer"
    FEATURE_LAYER = "ch.bfs.gebaeude_wohnungs_register"
    CACHE_SIZE = 100  # Nombre maximum d'entrées en cache

    @classmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def get_building_data_cached(cls, adresse: str, npa: str, localite: str) -> Optional[Dict]:
        """
        Version avec cache de get_building_data

        Le cache est basé sur (adresse, npa, localite) et garde les 100 dernières recherches.
        Cache vidé automatiquement lorsque plein (LRU = Least Recently Used).

        Args:
            adresse: Rue et numéro
            npa: Code postal
            localite: Localité

        Returns:
            Dictionnaire des données du bâtiment ou None si non trouvé
        """
        logger.info(f"🔍 Recherche bâtiment (avec cache): {adresse}, {npa} {localite}")
        return cls.get_building_data(adresse, npa, localite)

    @staticmethod
    def get_building_data(adresse: str, npa: str, localite: str) -> Optional[Dict]:
        """
        Récupère les données du bâtiment depuis geo.admin.ch

        Méthode en 2 étapes:
        1. SearchServer avec type=featuresearch pour obtenir le featureId
        2. MapServer pour récupérer les détails complets via le featureId

        Args:
            adresse: Rue et numéro (ex: "Route de l'Hôpital 16b")
            npa: Code postal (ex: "1180")
            localite: Localité (ex: "Rolle")

        Returns:
            Dict avec les clés: egid, garea, gastw, gbauj, gebnr, lparz, layer_name, coords
            None si aucun bâtiment trouvé
        """
        search_text = f"{adresse}, {npa} {localite}"
        logger.info(f"🔍 Recherche bâtiment: {search_text}")

        # ÉTAPE 1: Rechercher avec featuresearch pour obtenir le featureId
        params = {
            "searchText": search_text,
            "lang": "fr",
            "type": "featuresearch",
            "features": GeoAdminClient.FEATURE_LAYER
        }

        try:
            response = requests.get(GeoAdminClient.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data.get('results'):
                logger.warning(f"⚠️  Aucun bâtiment trouvé pour: {search_text}")
                return None

            # Prendre le premier résultat (meilleur match)
            first_result = data['results'][0]
            attrs = first_result.get('attrs', {})

            feature_id = attrs.get('featureId') or attrs.get('feature_id')
            lat = attrs.get('lat')
            lon = attrs.get('lon')

            if not feature_id:
                logger.warning(f"⚠️  Feature ID non trouvé dans la réponse")
                return None

            logger.info(f"   ✅ Feature ID trouvé: {feature_id}")

            # ÉTAPE 2: Récupérer les détails complets de la feature
            feature_url = f"https://api3.geo.admin.ch/rest/services/api/MapServer/{GeoAdminClient.FEATURE_LAYER}/{feature_id}"
            feature_params = {
                "lang": "fr",
                "sr": "4326"  # WGS84 pour les coordonnées
            }

            response = requests.get(feature_url, params=feature_params, timeout=30)
            response.raise_for_status()
            feature_data = response.json()

            # Extraire les attributs
            feature = feature_data.get('feature', {})
            properties = feature.get('attributes', {}) or feature.get('properties', {})

            # Construire le dictionnaire de données
            building_data = {
                'egid': properties.get('egid', 'N/A'),
                'garea': float(properties.get('garea', 0)) if properties.get('garea') else 0,
                'gastw': int(properties.get('gastw', 0)) if properties.get('gastw') else 0,
                'gbauj': properties.get('gbauj', 'N/A'),
                'gebnr': properties.get('gebnr', 'N/A'),
                'lparz': properties.get('lparz', 'N/A'),
                'layer_name': 'Bâtiment',
                'coords': (lat, lon)
            }

            logger.info(f"✅ Bâtiment trouvé:")
            logger.info(f"   EGID: {building_data['egid']}")
            logger.info(f"   Surface au sol: {building_data['garea']} m²")
            logger.info(f"   Niveaux hors-sol: {building_data['gastw']}")
            logger.info(f"   Année construction: {building_data['gbauj']}")
            logger.info(f"   Coordonnées: {building_data['coords']}")

            return building_data

        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout lors de la requête vers geo.admin.ch")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur API geo.admin.ch: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Status code: {e.response.status_code}")
                logger.error(f"   Réponse: {e.response.text[:200]}")
            return None
        except (KeyError, ValueError) as e:
            logger.error(f"❌ Erreur lors du parsing de la réponse: {e}")
            return None

    @staticmethod
    def get_default_building_data() -> Dict:
        """
        Retourne des données de bâtiment par défaut en cas d'échec

        Returns:
            Dictionnaire avec des valeurs par défaut
        """
        logger.warning("⚠️  Utilisation de données de bâtiment par défaut")
        return {
            'egid': 'N/A',
            'garea': 100,
            'gastw': 2,
            'gbauj': 'N/A',
            'gebnr': 'N/A',
            'lparz': 'N/A',
            'layer_name': 'Bâtiment',
            'coords': None
        }

    @classmethod
    def clear_cache(cls):
        """Vide le cache des recherches de bâtiments"""
        cls.get_building_data_cached.cache_clear()
        logger.info("🗑️  Cache geo.admin.ch vidé")

    @classmethod
    def get_cache_info(cls):
        """
        Retourne les statistiques du cache

        Returns:
            Named tuple avec hits, misses, maxsize, currsize
        """
        return cls.get_building_data_cached.cache_info()
