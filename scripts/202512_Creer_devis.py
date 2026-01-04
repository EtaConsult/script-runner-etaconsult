# -*- coding: utf-8 -*-
"""
Script de création de devis CECB, CECB Plus et Conseil Incitatif dans Bexio
VERSION REFACTORISÉE - Architecture modulaire

Fonctionnalités :
- Recherche/création de contacts (Privé ou Société avec personne associée)
- Récupération des données du bâtiment (geo.admin.ch)
- Calcul automatique des prix selon formule tarifaire
- Création de l'offre dans Bexio avec positions détaillées
- Validation robuste des données
- Gestion d'erreurs complète
- Logging détaillé

Usage:
    python 202512_Creer_devis.py '{"type_contact": "Privé", ...}'
"""

import sys
import json
import logging
from datetime import datetime
from typing import Dict

# ==========================================
# CONFIGURATION DE L'ENCODAGE UTF-8
# ==========================================
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# ==========================================
# IMPORTS DES MODULES PERSONNALISÉS
# ==========================================
try:
    from config_manager import ConfigManager
    from bexio_client import BexioClient
    from geo_admin_client import GeoAdminClient
    from contact_manager import ContactManager
    from quote_calculator import QuoteCalculator
    from quote_position import QuotePositionBuilder
    from validators import validate_form_data, sanitize_form_data, ValidationError
    import legal_texts
except ImportError as e:
    logger.error(f"❌ ERREUR : Impossible d'importer les modules: {e}")
    logger.error("📋 Vérifiez que tous les fichiers Python sont présents dans le dossier scripts/")
    sys.exit(1)


# ==========================================
# FONCTION PRINCIPALE DE CRÉATION DE DEVIS
# ==========================================

def create_quote(form_data: Dict, config_mgr: ConfigManager) -> Dict:
    """
    Crée un devis CECB/CECB Plus/Conseil Incitatif

    Args:
        form_data: Données du formulaire
        config_mgr: Gestionnaire de configuration

    Returns:
        Devis créé

    Raises:
        ValidationError: Si les données sont invalides
        Exception: En cas d'erreur lors de la création
    """
    type_certificat = form_data["type_certificat"]
    logger.info(f"📋 Type de certificat: {type_certificat}")
    logger.info(f"👤 Contact: {form_data['prenom']} {form_data['nom_famille']}")

    # 1. Initialiser les clients
    logger.info(f"\n{'=' * 60}")
    logger.info("🔧 INITIALISATION DES CLIENTS")
    logger.info("=" * 60)

    bexio = BexioClient(config_mgr.get_bexio_api_token(), config_mgr.get_bexio_base_url())
    contact_mgr = ContactManager(bexio, {
        "CONTACT_TYPES": config_mgr.get_contact_types(),
        "SALUTATIONS": config_mgr.get_salutations(),
        "BEXIO_IDS": config_mgr.get_bexio_ids()
    })

    # 2. Gérer le contact
    logger.info(f"\n{'=' * 60}")
    logger.info("👥 GESTION DU CONTACT")
    logger.info("=" * 60)

    contact_ids = contact_mgr.get_or_create_contact(form_data)

    # 3. Récupérer les données du bâtiment
    logger.info(f"\n{'=' * 60}")
    logger.info("🏗️  RÉCUPÉRATION DONNÉES BÂTIMENT")
    logger.info("=" * 60)

    adresse_batiment = form_data.get("rue_batiment", form_data["rue_facturation"])
    npa_batiment = form_data.get("npa_batiment", form_data["npa_facturation"])
    localite_batiment = form_data.get("localite_batiment", form_data["localite_facturation"])

    # Utiliser le cache pour optimiser les performances
    building_data = GeoAdminClient.get_building_data_cached(
        adresse_batiment,
        npa_batiment,
        localite_batiment
    )

    if not building_data:
        building_data = GeoAdminClient.get_default_building_data()

    # 4. Calculer les prix (sauf pour Conseil Incitatif)
    pricing = None
    if type_certificat != "Conseil Incitatif":
        logger.info(f"\n{'=' * 60}")
        logger.info("💰 CALCUL DES PRIX")
        logger.info("=" * 60)

        calculator = QuoteCalculator(
            config_mgr.get_all_tarifs(),
            config_mgr.get_google_maps_api_key(),
            config_mgr.get_eta_consult_address()
        )

        pricing = calculator.calculate_quote_pricing(building_data, form_data)

    # 5. Créer l'offre dans Bexio
    logger.info(f"\n{'=' * 60}")
    logger.info("📄 CRÉATION DE L'OFFRE BEXIO")
    logger.info("=" * 60)

    quote = create_bexio_quote(
        bexio,
        form_data,
        contact_ids,
        building_data,
        pricing,
        config_mgr
    )

    # 6. Afficher le résumé
    print_summary(quote, contact_ids, pricing, type_certificat)

    return quote


def create_bexio_quote(
    bexio_client: BexioClient,
    form_data: Dict,
    contact_ids: Dict,
    building_data: Dict,
    pricing: Dict,
    config_mgr: ConfigManager
) -> Dict:
    """
    Crée l'offre dans Bexio avec toutes les positions

    Args:
        bexio_client: Client Bexio
        form_data: Données du formulaire
        contact_ids: IDs des contacts
        building_data: Données du bâtiment
        pricing: Résultats du calcul de prix (None pour Conseil Incitatif)
        config_mgr: Gestionnaire de configuration

    Returns:
        Offre créée
    """
    type_certificat = form_data["type_certificat"]
    adresse_batiment = form_data.get("rue_batiment", form_data["rue_facturation"])
    npa_batiment = form_data.get("npa_batiment", form_data["npa_facturation"])
    localite_batiment = form_data.get("localite_batiment", form_data["localite_facturation"])

    # Titre de l'offre
    title = f"{type_certificat} - {adresse_batiment}, {npa_batiment}, {localite_batiment}"

    # Créer les positions selon le type de certificat
    position_builder = QuotePositionBuilder(
        config_mgr.get_bexio_ids(),
        config_mgr.get_all_tarifs()
    )

    # Préparer les textes légaux avec le module legal_texts
    legal_texts_dict = {
        "prestations_incluses_cecb": legal_texts.PRESTATIONS_INCLUSES_CECB,
        "prestations_non_incluses_cecb": legal_texts.PRESTATIONS_NON_INCLUSES_CECB,
        "prestations_incluses_cecb_plus": legal_texts.PRESTATIONS_INCLUSES_CECB_PLUS,
        "prestations_non_incluses_cecb_plus": legal_texts.PRESTATIONS_NON_INCLUSES_CECB_PLUS,
        "prestations_incluses_conseil": legal_texts.PRESTATIONS_INCLUSES_CONSEIL,
        "responsabilite_cecb": legal_texts.RESPONSABILITE_CECB,
        "format_custom_message": legal_texts.format_custom_message
    }

    # Construire les positions selon le type
    if type_certificat == "CECB":
        positions_objects = position_builder.build_cecb_positions(
            building_data, form_data, pricing, legal_texts_dict
        )
    elif type_certificat == "CECB Plus":
        positions_objects = position_builder.build_cecb_plus_positions(
            building_data, form_data, pricing, legal_texts_dict
        )
    else:  # Conseil Incitatif
        positions_objects = position_builder.build_conseil_incitatif_positions(
            building_data, form_data, legal_texts_dict
        )

    # Convertir en format Bexio
    positions = [pos.to_bexio_format() for pos in positions_objects]

    # Récupérer le pourcentage d'acompte depuis les tarifs
    pct_acompte = config_mgr.get_tarif("pct_acompte", 30)

    # Payload de l'offre
    payload = {
        "contact_id": contact_ids["contact_id"],
        "user_id": config_mgr.get_bexio_ids()["user_id"],
        "title": title,
        "mwst_type": config_mgr.get_bexio_ids()["mwst_type"],
        "currency_id": config_mgr.get_bexio_ids()["currency_id"],
        "language_id": config_mgr.get_bexio_ids()["language_id"],
        "footer": legal_texts.get_complete_footer(pct_acompte),
        "positions": positions
    }

    # Ajouter contact_sub_id seulement s'il existe
    if contact_ids.get("contact_sub_id") is not None:
        payload["contact_sub_id"] = contact_ids["contact_sub_id"]

    # Créer l'offre
    quote = bexio_client.create_quote(payload)

    logger.info(f"✅ Offre créée avec succès !")
    logger.info(f"   ID: {quote.get('id')}")
    logger.info(f"   Numéro: {quote.get('document_nr')}")
    logger.info(f"   Titre: {title}")

    return quote


def print_summary(quote: Dict, contact_ids: Dict, pricing: Dict, type_certificat: str):
    """
    Affiche le résumé final de la création du devis

    Args:
        quote: Devis créé
        contact_ids: IDs des contacts
        pricing: Résultats du calcul de prix (None pour Conseil Incitatif)
        type_certificat: Type de certificat
    """
    logger.info(f"\n{'=' * 60}")
    logger.info("✅ SUCCÈS !")
    logger.info("=" * 60)
    logger.info(f"Offre #{quote.get('document_nr')} créée avec succès")
    logger.info(f"Contact ID: {contact_ids['contact_id']}")

    if contact_ids.get('contact_sub_id'):
        logger.info(f"Personne associée ID: {contact_ids['contact_sub_id']}")

    if pricing:
        # Calculer le total HT
        config_mgr = ConfigManager()
        total_ht = (
            pricing['cecb_unit_price'] +
            config_mgr.get_tarif('frais_emission_cecb', 80) +
            pricing['forfait_execution']
        )

        if type_certificat == "CECB Plus":
            total_ht += pricing['cecb_plus_unit_price']

        logger.info(f"Montant total HT estimé: {total_ht} CHF")

    logger.info("=" * 60)


# ==========================================
# MAIN
# ==========================================

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 Création de devis CECB/CECB Plus/Conseil Incitatif")
    print("=" * 60)

    # 1. Récupérer les données du formulaire
    if len(sys.argv) < 2:
        logger.error("❌ ERREUR : Données du formulaire manquantes")
        logger.error("Usage: python 202512_Creer_devis.py '{...json...}'")
        sys.exit(1)

    try:
        form_data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        logger.error(f"❌ ERREUR : Format JSON invalide: {e}")
        sys.exit(1)

    try:
        # 2. Initialiser le gestionnaire de configuration
        config_mgr = ConfigManager()
        config_mgr.validate_config()

        # 3. Nettoyer et valider les données du formulaire
        form_data = sanitize_form_data(form_data)
        validate_form_data(form_data)

        # 4. Créer le devis
        quote = create_quote(form_data, config_mgr)

        # Succès
        sys.exit(0)

    except ValidationError as e:
        logger.error(f"\n❌ ERREUR DE VALIDATION: {e}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
