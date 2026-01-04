# -*- coding: utf-8 -*-
"""
Gestion des positions pour les devis Bexio
Encapsule la création et le formatage des positions de devis
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class QuotePosition:
    """
    Représente une position dans un devis Bexio

    Deux types de positions:
    - KbPositionCustom: Position avec prix (article, service)
    - KbPositionText: Position texte seul (description, prestations)
    """

    def __init__(
        self,
        text: str,
        amount: Optional[float] = None,
        unit_price: Optional[float] = None,
        tax_id: Optional[int] = None,
        unit_id: Optional[int] = None,
        position_type: str = "KbPositionCustom"
    ):
        """
        Initialise une position de devis

        Args:
            text: Texte de la position (description HTML supportée)
            amount: Quantité (obligatoire pour KbPositionCustom)
            unit_price: Prix unitaire en CHF (obligatoire pour KbPositionCustom)
            tax_id: ID de la taxe Bexio (obligatoire pour KbPositionCustom)
            unit_id: ID de l'unité Bexio (obligatoire pour KbPositionCustom)
            position_type: Type de position ("KbPositionCustom" ou "KbPositionText")
        """
        self.text = text
        self.amount = amount
        self.unit_price = unit_price
        self.tax_id = tax_id
        self.unit_id = unit_id
        self.position_type = position_type

        # Validation
        if position_type == "KbPositionCustom":
            if amount is None or unit_price is None or tax_id is None or unit_id is None:
                raise ValueError("KbPositionCustom nécessite amount, unit_price, tax_id et unit_id")

    def to_bexio_format(self) -> Dict[str, Any]:
        """
        Convertit la position en format API Bexio

        Returns:
            Dictionnaire formaté pour l'API Bexio
        """
        if self.position_type == "KbPositionText":
            return {
                "type": "KbPositionText",
                "text": self.text
            }

        return {
            "type": "KbPositionCustom",
            "text": self.text,
            "amount": str(self.amount),
            "unit_price": str(self.unit_price),
            "tax_id": self.tax_id,
            "unit_id": self.unit_id,
            "is_optional": False
        }

    @staticmethod
    def create_text_position(text: str) -> 'QuotePosition':
        """
        Créateur de position texte

        Args:
            text: Texte de la position

        Returns:
            QuotePosition de type texte
        """
        return QuotePosition(text=text, position_type="KbPositionText")

    @staticmethod
    def create_custom_position(
        text: str,
        amount: float,
        unit_price: float,
        tax_id: int,
        unit_id: int
    ) -> 'QuotePosition':
        """
        Créateur de position personnalisée avec prix

        Args:
            text: Description de la position
            amount: Quantité
            unit_price: Prix unitaire
            tax_id: ID taxe Bexio
            unit_id: ID unité Bexio

        Returns:
            QuotePosition de type custom
        """
        return QuotePosition(
            text=text,
            amount=amount,
            unit_price=unit_price,
            tax_id=tax_id,
            unit_id=unit_id,
            position_type="KbPositionCustom"
        )


class QuotePositionBuilder:
    """
    Builder pour créer facilement des positions de devis selon le type de certificat

    Cette classe simplifie la création des positions en encapsulant la logique
    de formatage et d'organisation des positions.
    """

    def __init__(self, bexio_ids: Dict[str, int], tarifs: Dict[str, Any]):
        """
        Initialise le builder

        Args:
            bexio_ids: Dictionnaire des IDs Bexio (tax_id, unit_id, etc.)
            tarifs: Dictionnaire des tarifs
        """
        self.bexio_ids = bexio_ids
        self.tarifs = tarifs

    def build_cecb_positions(
        self,
        building_data: dict,
        form_data: dict,
        pricing: dict,
        legal_texts: dict
    ) -> list:
        """
        Construit les positions pour un CECB standard

        Args:
            building_data: Données du bâtiment
            form_data: Données du formulaire
            pricing: Résultats du calcul de prix
            legal_texts: Textes légaux (prestations, responsabilité)

        Returns:
            Liste de QuotePosition
        """
        positions = []

        # 1. Position CECB principale
        cecb_text = self._format_cecb_main_text(building_data, form_data)
        positions.append(QuotePosition.create_custom_position(
            text=cecb_text,
            amount=1,
            unit_price=pricing["cecb_unit_price"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 2. Frais d'émission CECB
        positions.append(QuotePosition.create_custom_position(
            text="Frais d'émission du rapport CECB sur la plateforme (nouveaux tarifs à partir du 01.01.2026)",
            amount=1,
            unit_price=self.tarifs["frais_emission_cecb"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 3. Forfait exécution (si non nul)
        if pricing["forfait_execution"] > 0:
            positions.append(QuotePosition.create_custom_position(
                text=f"Forfait exécution {pricing['delai_label']}",
                amount=1,
                unit_price=pricing["forfait_execution"],
                tax_id=self.bexio_ids["tax_id"],
                unit_id=self.bexio_ids["unit_id"]
            ))

        # 4. Prestations incluses
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("prestations_incluses_cecb", "")
        ))

        # 5. Clause de responsabilité CECB
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("responsabilite_cecb", "")
        ))

        # 6. Prestations non-incluses
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("prestations_non_incluses_cecb", "")
        ))

        # 7. Message personnalisé (si fourni)
        if form_data.get("message_personnalise"):
            message_formatted = legal_texts.get("format_custom_message", lambda x: x)(
                form_data["message_personnalise"]
            )
            if message_formatted:
                positions.append(QuotePosition.create_text_position(message_formatted))

        return positions

    def build_cecb_plus_positions(
        self,
        building_data: dict,
        form_data: dict,
        pricing: dict,
        legal_texts: dict
    ) -> list:
        """
        Construit les positions pour un CECB Plus

        Args:
            building_data: Données du bâtiment
            form_data: Données du formulaire
            pricing: Résultats du calcul de prix
            legal_texts: Textes légaux

        Returns:
            Liste de QuotePosition
        """
        positions = []

        # 1. Position CECB principale
        cecb_text = self._format_cecb_main_text(building_data, form_data)
        positions.append(QuotePosition.create_custom_position(
            text=cecb_text,
            amount=1,
            unit_price=pricing["cecb_unit_price"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 2. Frais d'émission CECB
        positions.append(QuotePosition.create_custom_position(
            text="Frais d'émission du rapport CECB sur la plateforme (nouveaux tarifs à partir du 01.01.2026)",
            amount=1,
            unit_price=self.tarifs["frais_emission_cecb"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 3. Forfait exécution (si non nul)
        if pricing["forfait_execution"] > 0:
            positions.append(QuotePosition.create_custom_position(
                text=f"Forfait exécution {pricing['delai_label']}",
                amount=1,
                unit_price=pricing["forfait_execution"],
                tax_id=self.bexio_ids["tax_id"],
                unit_id=self.bexio_ids["unit_id"]
            ))

        # 4. Position CECB Plus
        cecb_plus_text = self._format_cecb_plus_text(form_data)
        positions.append(QuotePosition.create_custom_position(
            text=cecb_plus_text,
            amount=1,
            unit_price=pricing["cecb_plus_unit_price"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 5. Frais d'émission CECB Plus
        positions.append(QuotePosition.create_custom_position(
            text="Frais d'émission du rapport CECB Plus sur la plateforme (nouveaux tarifs à partir du 01.01.2026)",
            amount=1,
            unit_price=self.tarifs["frais_emission_cecb_plus"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 6. Conseil à la restitution du rapport CECB Plus
        positions.append(QuotePosition.create_custom_position(
            text="Conseils à la restitution du rapport CECB®Plus<br>- Lecture commentée du rapport de conseil",
            amount=1,
            unit_price=self.tarifs["conseil_restitution_cecb_plus"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 7. Demande de subvention
        positions.append(QuotePosition.create_custom_position(
            text="Demande de subvention par l'expert CECB selon les conditions d'éligibilité du Programme des Bâtiments : Mesure I",
            amount=1,
            unit_price=self.tarifs["demande_subvention_cecb_plus"],
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 8. Informations sur les subventions
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("subventions_cecb_plus", "")
        ))

        # 9. Prestations incluses CECB Plus
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("prestations_incluses_cecb_plus", "")
        ))

        # 10. Clause de responsabilité CECB
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("responsabilite_cecb", "")
        ))

        # 11. Prestations non-incluses CECB Plus
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("prestations_non_incluses_cecb_plus", "")
        ))

        # 12. Message personnalisé (si fourni)
        if form_data.get("message_personnalise"):
            message_formatted = legal_texts.get("format_custom_message", lambda x: x)(
                form_data["message_personnalise"]
            )
            if message_formatted:
                positions.append(QuotePosition.create_text_position(message_formatted))

        return positions

    def build_conseil_incitatif_positions(
        self,
        building_data: dict,
        form_data: dict,
        legal_texts: dict
    ) -> list:
        """
        Construit les positions pour un Conseil Incitatif

        Args:
            building_data: Données du bâtiment
            form_data: Données du formulaire
            legal_texts: Textes légaux

        Returns:
            Liste de QuotePosition
        """
        positions = []

        # 1. Position Conseil Incitatif (gratuit)
        conseil_text = self._format_conseil_incitatif_text(building_data, form_data)
        positions.append(QuotePosition.create_custom_position(
            text=conseil_text,
            amount=1,
            unit_price=self.tarifs.get("prix_conseil_incitatif", 0),
            tax_id=self.bexio_ids["tax_id"],
            unit_id=self.bexio_ids["unit_id"]
        ))

        # 2. Prestations incluses
        positions.append(QuotePosition.create_text_position(
            legal_texts.get("prestations_incluses_conseil", "")
        ))

        # 3. Message personnalisé (si fourni)
        if form_data.get("message_personnalise"):
            message_formatted = legal_texts.get("format_custom_message", lambda x: x)(
                form_data["message_personnalise"]
            )
            if message_formatted:
                positions.append(QuotePosition.create_text_position(message_formatted))

        return positions

    # ==========================================
    # MÉTHODES PRIVÉES DE FORMATAGE
    # ==========================================

    def _format_cecb_main_text(self, building_data: dict, form_data: dict) -> str:
        """Formate le texte de la position CECB principale"""
        adresse = form_data.get("rue_batiment", form_data["rue_facturation"])
        npa = form_data.get("npa_batiment", form_data["npa_facturation"])
        localite = form_data.get("localite_batiment", form_data["localite_facturation"])

        return f"""Etablissement d'un certificat CECB® :<br>- EGID n°{building_data['egid']}<br>- {adresse}, CH {npa}, {localite}<br>- {building_data['layer_name']} n°{building_data['gebnr']}<br>- Parcelle n°{building_data['lparz']}<br>- {building_data['gastw']} niveaux hors sol<br>- Surface au sol {building_data['garea']} m²<br>- Année de construction : {building_data['gbauj']}"""

    def _format_cecb_plus_text(self, form_data: dict) -> str:
        """Formate le texte de la position CECB Plus"""
        adresse = form_data.get("rue_batiment", form_data["rue_facturation"])
        npa = form_data.get("npa_batiment", form_data["npa_facturation"])
        localite = form_data.get("localite_batiment", form_data["localite_facturation"])

        return f"Etablissement d'un certificat CECB® Plus, en sus :<br>- {adresse}, CH {npa}, {localite}"

    def _format_conseil_incitatif_text(self, building_data: dict, form_data: dict) -> str:
        """Formate le texte de la position Conseil Incitatif"""
        adresse = form_data.get("rue_batiment", form_data["rue_facturation"])
        npa = form_data.get("npa_batiment", form_data["npa_facturation"])
        localite = form_data.get("localite_batiment", form_data["localite_facturation"])

        return f"Conseil incitatif Chauffez renouvelable® :<br>- EGID n°{building_data['egid']}<br>- {adresse}, CH {npa}, {localite}"
