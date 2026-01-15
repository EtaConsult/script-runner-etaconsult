# -*- coding: utf-8 -*-
"""
Script Facture Payée - Eta Consult Sàrl
Lance ce script après qu'une facture a été payée dans Bexio.
"""

import os
import re
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import base64
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env (remonte au dossier parent)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# ============================================
# CONFIGURATION (depuis variables d'environnement)
# ============================================

BEXIO_TOKEN = os.environ.get('BEXIO_TOKEN', '')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN', '')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID', '')

# ============================================
# CHEMINS MULTI-PLATEFORME
# ============================================
def get_default_path(env_var, windows_default, linux_default):
    """Retourne le chemin depuis la variable d'environnement ou la valeur par defaut selon la plateforme"""
    env_value = os.environ.get(env_var)
    if env_value:
        return Path(env_value)
    if sys.platform == "win32":
        return Path(windows_default)
    else:
        return Path(linux_default)

DOSSIERS_ACTIFS = get_default_path(
    "DOSSIERS_ACTIFS_PATH",
    r"C:\Users\info\OneDrive\Documents_Eta Consult\12. Dossiers actifs",
    "/home/etaconsult/dossiers_actifs"
)

# ============================================
# FONCTIONS BEXIO
# ============================================

def get_facture(numero_facture):
    """Récupère les détails d'une facture Bexio"""
    url = f"https://api.bexio.com/2.0/kb_invoice/{numero_facture}"
    headers = {
        "Authorization": f"Bearer {BEXIO_TOKEN}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_facture_pdf(numero_facture):
    """Récupère le PDF d'une facture en base64"""
    url = f"https://api.bexio.com/2.0/kb_invoice/{numero_facture}/pdf"
    headers = {
        "Authorization": f"Bearer {BEXIO_TOKEN}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get("content")

def marquer_facture_payee_bexio(numero_facture):
    """Marque la facture comme payée dans Bexio"""
    url = f"https://api.bexio.com/3.0/kb_invoices/{numero_facture}/mark_as_paid"
    headers = {
        "Authorization": f"Bearer {BEXIO_TOKEN}",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers)

    if response.status_code in [200, 201]:
        print(f"[OK] Facture marquée comme payée dans Bexio")
        return True
    else:
        print(f"[!] Erreur Bexio: {response.status_code} - {response.text}")
        return False

# ============================================
# FONCTIONS DE PARSING
# ============================================

def parse_titre_facture(titre):
    """
    Parse le titre de la facture pour extraire les informations
    Format attendu: "Type - Rue num, NPA, Localité"
    Exemple: "AMOen - Chem. du Treizou 21, 1270, Trélex"
    """
    pattern = r"^(.*?)\s*-\s*(.*?),\s*(\d{4}),\s*(.+)$"
    match = re.match(pattern, titre.strip())

    if match:
        type_projet = match.group(1).strip()
        rue = match.group(2).strip()
        npa = match.group(3).strip()
        localite = match.group(4).strip()

        return {
            "type": type_projet,
            "rue": rue,
            "npa": npa,
            "localite": localite
        }
    return None

# ============================================
# FONCTIONS DOSSIERS
# ============================================

def trouver_dossier_projet(rue, localite):
    """Cherche le dossier projet correspondant dans les dossiers actifs"""

    # Nettoyer les noms pour la recherche
    rue_clean = rue.replace(".", "").replace(",", "").strip()
    localite_clean = localite.strip()

    print(f"\n[RECHERCHE] Dossier pour: {rue}, {localite}")

    # Chercher dans tous les sous-dossiers de "Dossiers actifs"
    for dossier in DOSSIERS_ACTIFS.iterdir():
        if not dossier.is_dir():
            continue

        nom_dossier = dossier.name

        # Vérifier si le dossier contient la rue ET la localité
        if localite_clean.lower() in nom_dossier.lower():
            # Vérifier aussi la rue (partiellement)
            rue_parts = rue_clean.split()
            if any(part.lower() in nom_dossier.lower() for part in rue_parts if len(part) > 3):
                print(f"   [OK] Trouvé: {nom_dossier}")
                return dossier

    print(f"   [!] Dossier non trouvé")
    return None

# ============================================
# FONCTIONS NOTION
# ============================================

def chercher_page_notion(rue, localite):
    """Cherche une page dans Notion par son titre"""

    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Rechercher par titre contenant la localité
    data = {
        "filter": {
            "property": "Nom",
            "title": {
                "contains": localite
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    results = response.json().get("results", [])

    # Affiner la recherche en vérifiant rue ET localité
    # Nettoyer et normaliser les apostrophes
    rue_clean = rue.replace(".", "").replace(",", "").replace("'", " ").replace("'", " ").strip().lower()

    # Mots à ignorer (trop courants)
    mots_ignores = ["chem", "chemin", "rue", "route", "av", "avenue", "rte"]

    for page in results:
        titre = page["properties"]["Nom"]["title"][0]["text"]["content"] if page["properties"]["Nom"]["title"] else ""
        titre_clean = titre.replace(".", "").replace(",", "").replace("'", " ").replace("'", " ").strip().lower()

        # Vérifier que la localité ET au moins une partie significative de la rue sont présentes
        if localite.lower() in titre_clean:
            # Extraire les mots significatifs de la rue (> 2 lettres et pas dans la liste ignorée)
            rue_parts = [part for part in rue_clean.split() if len(part) > 2 and part not in mots_ignores]

            # Vérifier si au moins un mot significatif de la rue est présent dans le titre
            if any(part in titre_clean for part in rue_parts):
                print(f"   [DEBUG] Mots cherchés: {rue_parts}")
                print(f"   [DEBUG] Trouvé dans: {titre}")
                return page

    return None

def marquer_facture_payee(page_id):
    """Coche la propriété 'Payé' dans Notion"""

    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "properties": {
            "Payé": {
                "checkbox": True
            }
        }
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"[OK] Propriété 'Payé' cochée dans Notion")
        return True
    else:
        print(f"[!] Erreur Notion: {response.text}")
        return False

# ============================================
# SCRIPT PRINCIPAL
# ============================================

def main():
    print("=" * 50)
    print("  FACTURE PAYEE - Eta Consult Sàrl")
    print("=" * 50)

    # Prendre le numéro de facture en argument
    if len(sys.argv) > 1:
        numero_facture = sys.argv[1].strip()
    else:
        print("[X] Numéro de facture requis!")
        print("Usage: python script.py <numero_facture>")
        sys.exit(1)

    try:
        # 1. Récupérer la facture
        print(f"\n[BEXIO] Récupération de la facture {numero_facture}...")
        facture = get_facture(numero_facture)

        titre = facture.get("title", "")
        document_nr = facture.get("document_nr", "")
        montant = facture.get("total", 0)

        print(f"   Titre: {titre}")
        print(f"   Montant: {montant} CHF")
        print(f"   Référence: {document_nr}")

        # 2. Parser le titre
        infos = parse_titre_facture(titre)
        if not infos:
            print("[X] Impossible de parser le titre de la facture")
            print(f"    Format attendu: 'Type - Rue num, NPA, Localité'")
            sys.exit(1)

        rue = infos["rue"]
        localite = infos["localite"]

        # 3. Trouver le dossier projet
        dossier_projet = trouver_dossier_projet(rue, localite)
        if not dossier_projet:
            print("[X] Dossier projet introuvable sur le serveur")
            print(f"    Recherché: {rue}, {localite}")
            sys.exit(1)

        # 4. Télécharger et sauvegarder le PDF de la facture
        print(f"\n[PDF] Téléchargement de la facture...")
        try:
            pdf_base64 = get_facture_pdf(numero_facture)
            if pdf_base64:
                pdf_bytes = base64.b64decode(pdf_base64)

                # Créer le dossier facture s'il n'existe pas
                dossier_facture = dossier_projet / "1. Admin" / "12. Facture"
                dossier_facture.mkdir(parents=True, exist_ok=True)

                # Sauvegarder le PDF
                pdf_path = dossier_facture / f"{document_nr}.pdf"
                pdf_path.write_bytes(pdf_bytes)
                print(f"   [OK] PDF sauvegardé: {pdf_path}")
            else:
                print(f"   [!] PDF non disponible")
        except Exception as e:
            print(f"   [!] Erreur PDF: {e}")
            # On continue quand même pour marquer comme payé

        # 5. Marquer comme payée dans Bexio
        print(f"\n[BEXIO] Marquage de la facture comme payée...")
        marquer_facture_payee_bexio(numero_facture)

        # 6. Mettre à jour Notion
        print(f"\n[NOTION] Recherche de la page...")
        page = chercher_page_notion(rue, localite)

        if page:
            page_id = page["id"]
            titre_page = page["properties"]["Nom"]["title"][0]["text"]["content"] if page["properties"]["Nom"]["title"] else ""
            print(f"   [OK] Page trouvée: {titre_page}")

            marquer_facture_payee(page_id)
        else:
            print(f"   [!] Page Notion non trouvée pour {rue}, {localite}")

        # Résumé
        print("\n" + "=" * 50)
        print("[OK] TERMINÉ!")
        print(f"Facture: {document_nr}")
        print(f"Dossier: {dossier_projet}")
        print("=" * 50)
        sys.exit(0)

    except requests.exceptions.HTTPError as e:
        print(f"\n[X] Erreur API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
