# -*- coding: utf-8 -*-
"""
Textes légaux et templates pour les devis CECB
Tous les textes modifiables pour les offres Bexio
"""

# ==========================================
# CLAUSES LÉGALES
# ==========================================

RESPONSABILITE_CECB = """<strong>Informations importantes et clause de non-responsabilité :</strong><br><br>Les classes CECB sont basées sur une méthode standardisée et simplifiée d'estimation des besoins énergétiques des bâtiments, appuyés sur des calculs types. La valeur déterminée ne doit pas être entendue comme une valeur absolue et sert uniquement d'indication à des fins de comparaison avec d'autres bâtiments.<br><br>Toute responsabilité découlant des déclarations du CECB est exclue. (chapitre 11.1 du règlement d'utilisation)."""

# ==========================================
# CONDITIONS DE PAIEMENT
# ==========================================

def get_conditions_paiement(pct_acompte: int = 30) -> str:
    """
    Retourne les conditions de paiement avec le pourcentage d'acompte paramétrable

    Args:
        pct_acompte: Pourcentage d'acompte (par défaut 30%)

    Returns:
        Texte formaté des conditions de paiement
    """
    return f"Conditions de paiement : Acompte de {pct_acompte}% à la commande, solde à réception du rapport."


# ==========================================
# PRESTATIONS INCLUSES
# ==========================================

PRESTATIONS_INCLUSES_CECB = """Notre offre de services prévoit les prestations suivantes :<br><br><strong>Etablissement d'un CECB</strong><br>- Déplacement et visite du bâtiment pour relevés des indications nécessaires<br>- Analyse et compilation des documents reçus (factures, relevés de consommations, plans, …)<br>- Calcul et saisie de la SRE (selon affectations)<br>- Calcul, saisie et description des surfaces des éléments de l'enveloppe (façades, vitrages, …)<br>- Estimation et saisie des coefficients de transmission thermique (valeurs U) des éléments de l'enveloppe thermique de l'état initial<br>- Identification et saisie des ponts thermiques de l'état initial<br>- Estimation des surfaces de l'enveloppe et de la surface de référence énergétique<br>- Plausibilité : Comparaison et affinage du calcul par rapport aux consommations réelles<br>- Etablissement du Certificat énergétique cantonal du bâtiment (CECB) pour l'état actuel (pour une seule émission)<br><br><strong>Données à fournir par le client</strong><br>- Accès aux bâtiments (locaux communs et au moins un appartement)<br>- Plans du bâtiment en format PDF (vues en plan, coupes et élévations)<br>- Données de consommation du bâtiment sur les trois dernières années (chauffage et électricité)<br><br>La rémunération comprend tous les services fournis par Êta Consult Sàrl (y compris les dépenses et les frais de déplacement)<br><br>Si des services supplémentaires sont demandés au-delà de cette portée, les honoraires de Êta Consult Sàrl seront basés sur les taux horaires suivants :<br>- Chef de projet : 155 CHF HT (Catégorie C)<br><br>Les accès aux bâtiments sont à garantir en coordination avec nos disponibilités."""

PRESTATIONS_NON_INCLUSES_CECB = """<strong>Prestations non-incluses :</strong><br>- Rapport CECB® Plus<br>- Conseil Incitatif Chauffez Renouvelable®"""

PRESTATIONS_INCLUSES_CECB_PLUS = """Notre offre de services prévoit les prestations suivantes :<br><br><strong>Etablissement d'un CECB et CECB® Plus</strong><br>- Déplacement et visite du bâtiment pour relevés des indications nécessaires<br>- Analyse et compilation des documents reçus (factures, relevés de consommations, plans, …)<br>- Calcul et saisie de la SRE (selon affectations)<br>- Calcul, saisie et description des surfaces des éléments de l'enveloppe (façades, vitrages, …)<br>- Estimation et saisie des coefficients de transmission thermique (valeurs U) des éléments de l'enveloppe thermique de l'état initial<br>- Identification et saisie des ponts thermiques de l'état initial<br>- Estimation des surfaces de l'enveloppe et de la surface de référence énergétique<br>- Plausibilité : Comparaison et affinage du calcul par rapport aux consommations réelles<br>- Etablissement du Certificat énergétique cantonal du bâtiment (CECB) pour l'état actuel (pour une seule émission)<br>- Etablissement du rapport CECB® Plus avec variantes de rénovation chiffrées<br><br><strong>Données à fournir par le client</strong><br>- Accès aux bâtiments (locaux communs et au moins un appartement)<br>- Plans du bâtiment en format PDF (vues en plan, coupes et élévations)<br>- Données de consommation du bâtiment sur les trois dernières années (chauffage et électricité)<br><br>La rémunération comprend tous les services fournis par Êta Consult Sàrl (y compris les dépenses et les frais de déplacement)<br><br>Si des services supplémentaires sont demandés au-delà de cette portée, les honoraires de Êta Consult Sàrl seront basés sur les taux horaires suivants :<br>- Chef de projet : 155 CHF HT (Catégorie C)<br><br>Les accès aux bâtiments sont à garantir en coordination avec nos disponibilités."""

PRESTATIONS_NON_INCLUSES_CECB_PLUS = """<strong>Prestations non-incluses :</strong><br>- Conseil Incitatif Chauffez Renouvelable®"""

PRESTATIONS_INCLUSES_CONSEIL = """<strong>Prestations incluses :</strong><br>- Conseil personnalisé sur les solutions de chauffage renouvelable<br>- Visite sur site<br>- Etablissement de la checklist Chauffez Renouvelable®<br>- Recommandations adaptées à votre bâtiment"""

# ==========================================
# SUBVENTIONS CECB PLUS
# ==========================================

SUBVENTIONS_CECB_PLUS = """<strong>Subventions cantonales (Canton de Vaud)</strong><br><br>Le Canton de Vaud propose une subvention aux propriétaires de bâtiments construits avant 2000 pour l'établissement d'un Certificat énergétique cantonal des bâtiments Plus (CECB Plus). Cette dernière n'est pas intégrée à la présente offre d'honoraires.<br><br>L'aide financière est fixée selon les principes suivants :<br>- Habitat individuel: 1000 fr.<br>- Habitat collectif: 1500 fr.<br><br>Sont considérées comme habitations individuelles des constructions comprenant au maximum deux logements.<br><br><strong>IMPORTANT :</strong> La demande doit être impérativement remise avant le début de la prestation. Une subvention ne peut être accordée pour une prestation en cours (art. 24 loi du 17 novembre 1999 sur les subventions)."""


# ==========================================
# FORMATAGE MESSAGE PERSONNALISÉ
# ==========================================

def format_custom_message(message: str) -> str:
    """
    Formate le message personnalisé pour intégration dans le devis

    Args:
        message: Message personnalisé du client

    Returns:
        Message formaté en HTML ou chaîne vide si pas de message
    """
    if not message or message.strip() == "":
        return ""

    return f"""<strong>Message :</strong><br>{message}"""


# ==========================================
# TEMPLATES DE POSITIONS
# ==========================================

# Template pour CECB principal
TEMPLATE_CECB_PRINCIPAL = """Etablissement d'un certificat CECB® :
- EGID n°{egid}
- {address}
- {layer_name} n°{gebnr}
- Parcelle n°{lparz}
- {floors} niveaux hors sol
- Surface au sol {surface} m²
- Année de construction : {year}"""

# Template pour CECB Plus
TEMPLATE_CECB_PLUS = """Etablissement d'un certificat CECB® Plus, en sus :
- {address}"""

# Template pour Conseil Incitatif
TEMPLATE_CONSEIL_INCITATIF = """Conseil incitatif Chauffez renouvelable® :
- EGID n°{egid}
- {address}"""

# Template pour frais d'émission
TEMPLATE_FRAIS_EMISSION = "Frais d'émission du rapport CECB sur la plateforme (nouveaux tarifs à partir du 01.01.2026)"

# Template pour forfait exécution
TEMPLATE_FORFAIT_EXECUTION = "Forfait exécution {delai_label}"


# ==========================================
# FOOTER
# ==========================================

FOOTER_SOURCE = "Source : Script Runner - Êta Consult Sàrl"


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_complete_footer(pct_acompte: int = 30) -> str:
    """
    Retourne le footer complet avec conditions de paiement et source

    Args:
        pct_acompte: Pourcentage d'acompte (par défaut 30%)

    Returns:
        Footer complet formaté en HTML
    """
    conditions = get_conditions_paiement(pct_acompte)
    return f"{conditions}<br><br>{FOOTER_SOURCE}"
