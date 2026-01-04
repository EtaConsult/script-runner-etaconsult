# -*- coding: utf-8 -*-
"""
Validation des données pour la création de devis CECB
Fonctions de validation et gestion d'erreurs robuste
"""

import logging
from typing import Optional, Dict, Any

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==========================================
# EXCEPTIONS PERSONNALISÉES
# ==========================================

class ValidationError(Exception):
    """Exception levée en cas d'erreur de validation"""
    pass


# ==========================================
# VALIDATION DES DONNÉES DE BÂTIMENT
# ==========================================

def validate_building_data(egid: Optional[str], address: str, surface: float) -> bool:
    """
    Valide les données du bâtiment

    Args:
        egid: Identifiant fédéral du bâtiment (peut être None)
        address: Adresse du bâtiment
        surface: Surface du bâtiment en m²

    Returns:
        True si les données sont valides

    Raises:
        ValidationError: Si les données sont invalides
    """
    # Validation de l'adresse
    if not address or not isinstance(address, str) or address.strip() == "":
        raise ValidationError("L'adresse du bâtiment est invalide ou manquante")

    # Validation de la surface
    if not isinstance(surface, (int, float)):
        raise ValidationError("La surface doit être un nombre")

    if surface <= 0:
        raise ValidationError(f"La surface doit être positive (reçu: {surface} m²)")

    if surface > 100000:
        logger.warning(f"Surface très élevée détectée: {surface} m²")

    # Validation de l'EGID (optionnel)
    if egid is not None and egid != 'N/A':
        if not isinstance(egid, str):
            egid = str(egid)

        if not egid.isdigit():
            raise ValidationError(f"L'EGID doit être numérique (reçu: {egid})")

        if len(egid) < 4 or len(egid) > 10:
            logger.warning(f"EGID avec longueur inhabituelle: {egid}")

    logger.info(f"✅ Validation bâtiment OK - EGID: {egid}, Surface: {surface} m²")
    return True


def validate_address_components(rue: str, npa: str, localite: str) -> bool:
    """
    Valide les composantes d'une adresse

    Args:
        rue: Rue et numéro
        npa: Code postal
        localite: Localité

    Returns:
        True si les composantes sont valides

    Raises:
        ValidationError: Si les composantes sont invalides
    """
    if not rue or rue.strip() == "":
        raise ValidationError("La rue est manquante")

    if not npa or npa.strip() == "":
        raise ValidationError("Le code postal est manquant")

    if not localite or localite.strip() == "":
        raise ValidationError("La localité est manquante")

    # Validation du NPA suisse (4 chiffres)
    npa_clean = npa.strip()
    if not npa_clean.isdigit() or len(npa_clean) != 4:
        raise ValidationError(f"Le code postal suisse doit contenir 4 chiffres (reçu: {npa})")

    return True


# ==========================================
# VALIDATION DES DONNÉES DE CONTACT
# ==========================================

def validate_contact_data(form_data: Dict[str, Any]) -> bool:
    """
    Valide les données d'un contact

    Args:
        form_data: Dictionnaire contenant les données du formulaire

    Returns:
        True si les données sont valides

    Raises:
        ValidationError: Si les données sont invalides
    """
    type_contact = form_data.get("type_contact")

    # Validation du type de contact
    if type_contact not in ["Privé", "Société"]:
        raise ValidationError(f"Type de contact invalide: {type_contact}")

    # Validation nom et prénom
    if not form_data.get("nom_famille") or form_data["nom_famille"].strip() == "":
        raise ValidationError("Le nom de famille est obligatoire")

    if not form_data.get("prenom") or form_data["prenom"].strip() == "":
        raise ValidationError("Le prénom est obligatoire")

    # Validation email (optionnel mais si fourni doit être valide)
    email = form_data.get("email", "").strip()
    if email and "@" not in email:
        raise ValidationError(f"Format d'email invalide: {email}")

    # Validation téléphone (optionnel)
    telephone = form_data.get("telephone", "").strip()
    if telephone and len(telephone) < 9:
        logger.warning(f"Numéro de téléphone potentiellement invalide: {telephone}")

    # Validation nom entreprise si type Société
    if type_contact == "Société":
        if not form_data.get("nom_entreprise") or form_data["nom_entreprise"].strip() == "":
            raise ValidationError("Le nom de l'entreprise est obligatoire pour un contact de type Société")

    # Validation adresse de facturation
    validate_address_components(
        form_data.get("rue_facturation", ""),
        form_data.get("npa_facturation", ""),
        form_data.get("localite_facturation", "")
    )

    logger.info(f"✅ Validation contact OK - {type_contact}: {form_data['prenom']} {form_data['nom_famille']}")
    return True


# ==========================================
# VALIDATION DES DONNÉES DE CERTIFICAT
# ==========================================

def validate_certificate_type(type_certificat: str) -> bool:
    """
    Valide le type de certificat

    Args:
        type_certificat: Type de certificat demandé

    Returns:
        True si le type est valide

    Raises:
        ValidationError: Si le type est invalide
    """
    valid_types = ["CECB", "CECB Plus", "Conseil Incitatif"]

    if type_certificat not in valid_types:
        raise ValidationError(f"Type de certificat invalide: {type_certificat}. Types valides: {', '.join(valid_types)}")

    return True


def validate_pricing_data(distance_km: float, surface_eq: float) -> bool:
    """
    Valide les données utilisées pour le calcul de prix

    Args:
        distance_km: Distance en kilomètres
        surface_eq: Surface équivalente en m²

    Returns:
        True si les données sont valides

    Raises:
        ValidationError: Si les données sont invalides
    """
    if distance_km < 0:
        raise ValidationError(f"La distance ne peut pas être négative (reçu: {distance_km} km)")

    if distance_km > 500:
        logger.warning(f"Distance très élevée détectée: {distance_km} km")

    if surface_eq <= 0:
        raise ValidationError(f"La surface équivalente doit être positive (reçu: {surface_eq} m²)")

    if surface_eq > 200000:
        logger.warning(f"Surface équivalente très élevée: {surface_eq} m²")

    return True


# ==========================================
# VALIDATION COMPLÈTE FORMULAIRE
# ==========================================

def validate_form_data(form_data: Dict[str, Any]) -> bool:
    """
    Valide toutes les données du formulaire

    Args:
        form_data: Dictionnaire contenant toutes les données du formulaire

    Returns:
        True si toutes les validations passent

    Raises:
        ValidationError: Si une validation échoue
    """
    logger.info("🔍 Validation complète du formulaire...")

    # Validation du type de certificat
    validate_certificate_type(form_data.get("type_certificat", ""))

    # Validation des données de contact
    validate_contact_data(form_data)

    # Validation de l'adresse du bâtiment
    adresse_batiment = form_data.get("rue_batiment", form_data.get("rue_facturation", ""))
    npa_batiment = form_data.get("npa_batiment", form_data.get("npa_facturation", ""))
    localite_batiment = form_data.get("localite_batiment", form_data.get("localite_facturation", ""))

    validate_address_components(adresse_batiment, npa_batiment, localite_batiment)

    logger.info("✅ Validation complète du formulaire OK")
    return True


# ==========================================
# UTILITAIRES DE NETTOYAGE
# ==========================================

def sanitize_string(value: str) -> str:
    """
    Nettoie une chaîne de caractères

    Args:
        value: Chaîne à nettoyer

    Returns:
        Chaîne nettoyée
    """
    if not value:
        return ""

    return value.strip()


def sanitize_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nettoie toutes les chaînes de caractères dans les données du formulaire

    Args:
        form_data: Données du formulaire

    Returns:
        Données nettoyées
    """
    cleaned = {}
    for key, value in form_data.items():
        if isinstance(value, str):
            cleaned[key] = sanitize_string(value)
        else:
            cleaned[key] = value

    return cleaned
