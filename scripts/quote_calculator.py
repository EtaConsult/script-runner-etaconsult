# -*- coding: utf-8 -*-
"""
Calculateur de prix pour les devis CECB, CECB Plus et Conseil Incitatif
Encapsule toute la logique de calcul tarifaire
"""

import logging
import requests
from typing import Dict, Tuple, Optional
from validators import validate_pricing_data

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoteCalculator:
    """
    Calculateur de prix pour les devis CECB

    Cette classe encapsule toute la logique de calcul selon la formule tarifaire:
    - Prix CECB = base_price + (km × km_factor) + (S_eq × surface_factor)
    - Prix CECB Plus = Prix CECB × plus_factor (max: plus_price_max)
    """

    def __init__(self, tarifs: dict, google_maps_api_key: str, eta_consult_address: str):
        """
        Initialise le calculateur avec les tarifs

        Args:
            tarifs: Dictionnaire contenant tous les tarifs
            google_maps_api_key: Clé API Google Maps pour calcul de distance
            eta_consult_address: Adresse d'Êta Consult (point de départ)
        """
        self.tarifs = tarifs
        self.google_maps_api_key = google_maps_api_key
        self.eta_consult_address = eta_consult_address

    # ==========================================
    # CALCULS DE BASE
    # ==========================================

    def calculate_equivalent_floors(self, gastw: int, sous_sol: str, combles: str) -> float:
        """
        Calcule les étages équivalents

        Args:
            gastw: Nombre d'étages hors-sol
            sous_sol: Type de sous-sol ("Non chauffé ou inexistant", "Partiellement chauffé 50%", etc.)
            combles: Type de combles (même format que sous_sol)

        Returns:
            Nombre d'étages équivalents
        """
        et_ss = self._parse_sous_sol_combles(sous_sol)
        et_co = self._parse_sous_sol_combles(combles)
        et_eq = et_ss + et_co + gastw

        logger.info(f"   Étages équivalents: {et_eq} (sous-sol: {et_ss}, combles: {et_co}, hors-sol: {gastw})")
        return et_eq

    def calculate_equivalent_surface(self, et_eq: float, garea: float) -> float:
        """
        Calcule la surface équivalente

        Args:
            et_eq: Nombre d'étages équivalents
            garea: Surface au sol en m²

        Returns:
            Surface équivalente en m²
        """
        s_eq = et_eq * garea
        logger.info(f"   Surface équivalente: {s_eq:.2f} m² ({et_eq} × {garea} m²)")
        return s_eq

    def calculate_cecb_price(self, distance_km: float, surface_eq: float, is_plus: bool = False) -> float:
        """
        Calcule le prix CECB selon les paramètres

        Args:
            distance_km: Distance en km depuis Êta Consult
            surface_eq: Surface équivalente en m²
            is_plus: True pour CECB Plus, False pour CECB standard

        Returns:
            Prix unitaire en CHF

        Raises:
            ValueError: Si les données sont invalides
        """
        # Validation des données
        validate_pricing_data(distance_km, surface_eq)

        # Facteurs selon seuils
        s_factor = self._get_surface_factor(surface_eq)
        km_factor = self._get_km_factor(distance_km)

        logger.info(f"   Facteur surface: {s_factor} ({'petit' if surface_eq < self.tarifs['surface_seuil'] else 'grand'} bâtiment)")
        logger.info(f"   Facteur km: {km_factor} ({'proche' if distance_km < self.tarifs['km_seuil'] else 'loin'})")

        # Calcul des composantes
        s_price = surface_eq * s_factor
        km_price = distance_km * km_factor

        # Prix unitaire CECB
        cecb_price = round(self.tarifs["base_price"] + km_price + s_price)
        logger.info(f"   Prix CECB: {cecb_price} CHF ({self.tarifs['base_price']} + {km_price:.2f} + {s_price:.2f})")

        # Si CECB Plus demandé
        if is_plus:
            cecb_plus_price = min(
                self.tarifs["plus_price_max"],
                round(cecb_price * self.tarifs["plus_factor"])
            )
            logger.info(f"   Prix CECB Plus: {cecb_plus_price} CHF (max {self.tarifs['plus_price_max']} CHF)")
            return cecb_plus_price

        return cecb_price

    def calculate_deadline_surcharge(self, deadline_type: str) -> Tuple[float, str]:
        """
        Calcule le supplément selon le délai

        Args:
            deadline_type: Type de délai ("Normal", "Express (+135 CHF)", "Urgent (+270 CHF)")

        Returns:
            Tuple (montant du supplément, label du délai)
        """
        mapping = {
            "Normal": (self.tarifs.get("forfait_normal", 0), "Normal"),
            "Express (+135 CHF)": (self.tarifs.get("forfait_express", 135), "Express"),
            "Urgent (+270 CHF)": (self.tarifs.get("forfait_urgent", 270), "Urgent")
        }

        surcharge, label = mapping.get(deadline_type, (0, "Normal"))
        logger.info(f"   Forfait exécution: {surcharge} CHF ({label})")
        return surcharge, label

    # ==========================================
    # CALCUL COMPLET
    # ==========================================

    def calculate_quote_pricing(self, building_data: dict, form_data: dict) -> dict:
        """
        Calcule tous les prix pour un devis

        Args:
            building_data: Données du bâtiment (egid, garea, gastw, etc.)
            form_data: Données du formulaire

        Returns:
            Dict contenant:
                - cecb_unit_price: Prix unitaire CECB
                - cecb_plus_unit_price: Prix unitaire CECB Plus (si applicable)
                - forfait_execution: Supplément délai
                - delai_label: Label du délai
                - distance_km: Distance calculée
                - s_eq: Surface équivalente
                - et_eq: Étages équivalents
        """
        logger.info(f"\n💰 Calcul des prix:")

        # 1. Calculer les étages équivalents
        # Utiliser le nombre d'étages du formulaire (modifiable par l'utilisateur)
        # Si absent, utiliser la valeur du RegBL
        nombre_etages = form_data.get("nombre_etages")
        if nombre_etages is not None:
            # Convertir en entier si c'est une chaîne
            gastw = int(nombre_etages) if isinstance(nombre_etages, str) else nombre_etages
            logger.info(f"   🔧 Nombre d'étages: {gastw} (du formulaire)")
        else:
            # Fallback sur la valeur du RegBL
            gastw = building_data.get('gastw', 2)
            logger.info(f"   🔧 Nombre d'étages: {gastw} (du RegBL)")

        et_eq = self.calculate_equivalent_floors(
            gastw,
            form_data.get("sous_sol", "Non chauffé ou inexistant"),
            form_data.get("combles", "Non chauffé ou inexistant")
        )

        # 2. Calculer la surface équivalente
        s_eq = self.calculate_equivalent_surface(et_eq, building_data['garea'])

        # 3. Calculer la distance
        adresse_batiment = form_data.get("rue_batiment", form_data["rue_facturation"])
        npa_batiment = form_data.get("npa_batiment", form_data["npa_facturation"])
        localite_batiment = form_data.get("localite_batiment", form_data["localite_facturation"])
        destination = f"{adresse_batiment}, {npa_batiment} {localite_batiment}, Suisse"

        distance_km = self.calculate_distance_google_maps(self.eta_consult_address, destination)

        # 4. Calculer les prix CECB et CECB Plus
        cecb_price = self.calculate_cecb_price(distance_km, s_eq, is_plus=False)
        cecb_plus_price = self.calculate_cecb_price(distance_km, s_eq, is_plus=True)

        # 5. Calculer le forfait exécution
        forfait_execution, delai_label = self.calculate_deadline_surcharge(
            form_data.get("delai", "Normal")
        )

        return {
            "cecb_unit_price": cecb_price,
            "cecb_plus_unit_price": cecb_plus_price,
            "forfait_execution": forfait_execution,
            "delai_label": delai_label,
            "distance_km": distance_km,
            "s_eq": s_eq,
            "et_eq": et_eq
        }

    # ==========================================
    # MÉTHODES PRIVÉES
    # ==========================================

    def _get_surface_factor(self, surface_eq: float) -> float:
        """Retourne le facteur surface selon le seuil"""
        if surface_eq < self.tarifs["surface_seuil"]:
            return self.tarifs["surface_factor_petit"]
        return self.tarifs["surface_factor_grand"]

    def _get_km_factor(self, distance_km: float) -> float:
        """Retourne le facteur kilométrique selon le seuil"""
        if distance_km < self.tarifs["km_seuil"]:
            return self.tarifs["km_factor_proche"]
        return self.tarifs["km_factor_loin"]

    def _parse_sous_sol_combles(self, value: str) -> float:
        """Parse la valeur du select sous-sol/combles vers un coefficient"""
        mapping = {
            "Non chauffé ou inexistant": 0,
            "Partiellement chauffé 50%": 0.5,
            "Chauffé 30%": 0.3,
            "Chauffé": 1
        }
        return mapping.get(value, 0)

    def calculate_distance_google_maps(self, origin: str, destination: str) -> float:
        """
        Calcule la distance en km entre deux adresses via Google Maps Distance Matrix API

        Args:
            origin: Adresse de départ
            destination: Adresse de destination

        Returns:
            Distance en km (0 si erreur)
        """
        if not self.google_maps_api_key:
            logger.warning("⚠️  Google Maps API key manquante - distance = 0 km")
            return 0

        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            "origins": origin,
            "destinations": destination,
            "mode": "driving",
            "key": self.google_maps_api_key
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "OK":
                logger.warning(f"⚠️  Google Maps API erreur: {data.get('status')}")
                return 0

            if not data.get("rows") or not data["rows"][0].get("elements"):
                logger.warning(f"⚠️  Aucune donnée de distance disponible")
                return 0

            element = data["rows"][0]["elements"][0]

            if element.get("status") != "OK":
                logger.warning(f"⚠️  Impossible de calculer la distance: {element.get('status')}")
                return 0

            # Distance en mètres, convertir en km
            distance_m = element.get("distance", {}).get("value", 0)
            distance_km = round(distance_m / 1000, 2)

            logger.info(f"   Distance Google Maps: {distance_km} km")
            return distance_km

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Erreur API Google Maps: {e}")
            return 0
