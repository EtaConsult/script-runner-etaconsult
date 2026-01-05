# -*- coding: utf-8 -*-
"""
Script Offre Acceptee - Eta Consult Sarl
Lance ce script apres avoir accepte une offre dans Bexio.
"""

import os
import re
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import shutil
import base64

# ============================================
# CONFIGURATION
# ============================================

BEXIO_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkVTNTYXFLOHF1c25rakl4WEFsbE1EZk0zakRLYkJneDd3dlVVMHBsaUhFIn0.eyJleHAiOjE3ODI1MTYzMjIsImlhdCI6MTc2NjcwNTE0MCwianRpIjoiZjZkMjk2YzktOWNhNi00ZTc3LWE5NWQtMzhjZmY3NDA5NTI2IiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmJleGlvLmNvbS9yZWFsbXMvYmV4aW8iLCJzdWIiOiI2MWIzMDNmMi1jMGMxLTQwMzgtYTM0YS0zOTc4ODRhNjc1ZjUiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJiZXhpb19wYXRfcHJvdmlkZXIiLCJzaWQiOiIzMDdiZjVhMS03NWNkLTQwYzUtYTY4Zi1iYWRlNmEwZmE2YWQiLCJzY29wZSI6Im9wZW5pZCBhY2NvdW50aW5nIGtiX2RlbGl2ZXJ5X3Nob3cgYXJjaGl2ZV9lZGl0IGJhbmtfcGF5bWVudF9zaG93IHByb2plY3RfZWRpdCBhY2NvdW50aW5nX3NldHRpbmdzX2VkaXQga2JfY3JlZGl0X3ZvdWNoZXJfc2hvdyBhcmNoaXZlX3NldHRpbmdzX2VkaXQga2Jfb2ZmZXJfZWRpdCBmaWxlIHByb2plY3Rfc2hvdyBjb21wYW55X3Byb2ZpbGUga2JfYmlsbF9zaG93IGNvbnRhY3RfZWRpdCBub3RlX3Nob3cga2JfZGVsaXZlcnlfZWRpdCBrYl9leHBlbnNlX3Nob3cgcGF5cm9sbF9wYXlzdHViX3Nob3cgcGF5cm9sbF9lbXBsb3llZV9zaG93IGtiX2FydGljbGVfb3JkZXJfZWRpdCBhcnRpY2xlX2VkaXQga2JfaW52b2ljZV9lZGl0IG9mZmxpbmVfYWNjZXNzIGtiX29yZGVyX3Nob3cga2JfYXJ0aWNsZV9vcmRlcl9zaG93IHBheXJvbGxfdGltZV9hY2NvdW50X2VkaXQgcGF5cm9sbF90aW1lX2FjY291bnRfc2hvdyBzdG9ja19lZGl0IHBheXJvbGxfYWJzZW5jZV9zaG93IGVtYWlsIGtiX29yZGVyX2VkaXQgcGF5cm9sbF9lbXBsb3llZV9lZGl0IHJldm9jYWJsZSBrYl9jcmVkaXRfdm91Y2hlcl9lZGl0IGJhbmtfcGF5bWVudF9lZGl0IG1vbml0b3JpbmdfZWRpdCB0YXNrX2VkaXQgbGVhZF9lZGl0IGFjY291bnRpbmdfc2V0dGluZ3Nfc2hvdyBhcmNoaXZlX3Nob3cga2JfYmlsbF9lZGl0IG1vbml0b3Jpbmdfc2hvdyB0ZWNobmljYWwgbGVhZF9zaG93IHRhc2tfc2hvdyBhcnRpY2xlX3Nob3cgZmluYW5jZV9yZXBvcnRzIGFyY2hpdmVfc2V0dGluZ3Nfc2hvdyBrYl9pbnZvaWNlX3Nob3cgc3Vic2NyaXB0aW9uX2FuZF9wZXJtaXNzaW9ucyBrYl9vZmZlcl9zaG93IHBheXJvbGxfYWJzZW5jZV9lZGl0IGJhbmtfYWNjb3VudF9zaG93IG5vdGVfZWRpdCBrYl9leHBlbnNlX2VkaXQgcHJvZmlsZSBjb250YWN0X3Nob3ciLCJsb2dpbl9pZCI6IjYxYjMwM2YyLWMwYzEtNDAzOC1hMzRhLTM5Nzg4NGE2NzVmNSIsImNvbXBhbnlfaWQiOiJrZ2Voc3QxYm1qZm8iLCJ1c2VyX2lkIjozNzAyOTgsImNvbXBhbnlfdXNlcl9pZCI6MX0.E8F0_yxz8j5Y24LRCTORfwkenz5m4H0hfXfuumKc-1xECnwOD-q7SVknLxAd_CDBOV2pHdcJokjkFLJ_oQsHQcmM3Uh2C-5UJzapSx0seZjaUfV9i2X6xwlFtmxoz3CZEwO-2jDNKUPoJaXvjXIN9A33l60n8mtP-nrrd13qABlU4Em_mAl-yg22UnxK-pLIfI9Eu8T_U3hMhLKM3LEWrNk_9ym9bwlSHdeyCPnfF0PLZlG_OCw2c-V5c-4IRI0-bR-t9eTW_Dmg6F7dZFjuv4vmZu8pTBb9xEJokQ8FBtLRRuwVv_hTO-AI2g9qRViIrNi6MDjtAgRiVd0T0miyuw"
NOTION_TOKEN = "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"
NOTION_DATABASE_ID = "217e930a-734b-8043-b41a-db294622dc14"

# Chemins locaux OneDrive
DOSSIERS_ACTIFS = Path(r"C:\Users\info\OneDrive\Documents_Eta Consult\12. Dossiers actifs")
DOSSIER_MODELES = Path(r"C:\Users\info\OneDrive\Documents_Eta Consult\MODELE")

# ============================================
# FONCTIONS BEXIO
# ============================================

def get_offre(numero_offre):
    """Recupere les details d'une offre Bexio"""
    url = f"https://api.bexio.com/2.0/kb_offer/{numero_offre}"
    headers = {
        "Authorization": f"Bearer {BEXIO_TOKEN}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_offre_pdf(numero_offre):
    """Recupere le PDF d'une offre en base64"""
    url = f"https://api.bexio.com/2.0/kb_offer/{numero_offre}/pdf"
    headers = {
        "Authorization": f"Bearer {BEXIO_TOKEN}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data.get("content", "")

# ============================================
# PARSING ADRESSE
# ============================================

def parse_titre_offre(titre):
    """
    Parse le titre de l'offre.
    Format attendu: "Type - Rue n, NPA, Localite"
    Exemple: "CECB - Rue du Lac 15, 1000, Lausanne"
    """
    pattern = r"(?P<type>[^-]+)\s*-\s*(?P<rue>[^,]+),\s*(?P<npa>\d+),\s*(?P<localite>.+)"
    match = re.match(pattern, titre.strip())
    if match:
        return {
            "type": match.group("type").strip(),
            "rue": match.group("rue").strip(),
            "npa": match.group("npa").strip(),
            "localite": match.group("localite").strip()
        }
    else:
        print(f"[!] Impossible de parser le titre: {titre}")
        return None

# ============================================
# CREATION DOSSIERS
# ============================================

def creer_structure_dossiers(rue, localite):
    """Cree la structure complete des dossiers projet"""
    
    date_prefix = datetime.now().strftime("%Y%m")
    nom_dossier = f"{date_prefix}_{rue}_{localite}"
    
    dossier_principal = DOSSIERS_ACTIFS / nom_dossier
    
    sous_dossiers = [
        "1. Admin",
        "1. Admin/11. Offre",
        "1. Admin/12. Facture",
        "2. Documents du MO",
        "2. Documents du MO/21. Plans",
        "2. Documents du MO/22. Consommations",
        "3. CAO",
        "4. Lesosai",
        "5. Rapport",
        "5. Rapport/51. Documents de travail",
        "5. Rapport/52. SRE",
        "5. Rapport/53. Annexes",
        "5. Rapport/54. CECB",
        "5. Rapport/55. CECB Plus",
        datetime.now().strftime("%Y%m%d"),
    ]
    
    print(f"\n[DOSSIER] Creation: {nom_dossier}")
    dossier_principal.mkdir(exist_ok=True)
    
    for sous_dossier in sous_dossiers:
        chemin = dossier_principal / sous_dossier
        chemin.mkdir(parents=True, exist_ok=True)
        print(f"   [OK] {sous_dossier}")
    
    return dossier_principal

# ============================================
# COPIE TEMPLATES
# ============================================

def copier_templates(dossier_projet, rue, localite):
    """Copie et renomme les fichiers templates"""
    
    nom_fichier = f"{rue}_{localite}"
    
    templates = [
        ("Rue n_Localite.3dm", "3. CAO", f"{nom_fichier}.3dm"),
        ("Rue n_Localite.gh", "3. CAO", f"{nom_fichier}.gh"),
        ("Rue n_Localite.bld", "4. Lesosai", f"{nom_fichier}.bld"),
    ]
    
    print(f"\n[TEMPLATES] Copie:")
    for template, destination, nouveau_nom in templates:
        source = DOSSIER_MODELES / template
        dest = dossier_projet / destination / nouveau_nom
        
        if source.exists():
            shutil.copy2(source, dest)
            print(f"   [OK] {template} -> {destination}/{nouveau_nom}")
        else:
            print(f"   [!] Template non trouve: {template}")

# ============================================
# GEO.ADMIN.CH & RegBL
# ============================================

def get_coordonnees(rue, npa, localite):
    """Recupere les coordonnees LV95 via geo.admin.ch"""
    search_text = f"{rue} {npa} {localite}"
    url = "https://api3.geo.admin.ch/rest/services/api/SearchServer"
    params = {
        "searchText": search_text,
        "lang": "fr",
        "type": "locations"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("results"):
        result = data["results"][0]["attrs"]
        x_lv95 = result["y"] + 2000000
        y_lv95 = result["x"] + 1000000
        return x_lv95, y_lv95
    return None, None

def get_regbl(x_lv95, y_lv95):
    """Recupere les donnees RegBL pour des coordonnees donnees"""
    
    xmin, ymin = x_lv95 - 50, y_lv95 - 50
    xmax, ymax = x_lv95 + 50, y_lv95 + 50
    
    url = "https://api3.geo.admin.ch/rest/services/api/MapServer/identify"
    params = {
        "geometry": f"{x_lv95},{y_lv95}",
        "geometryType": "esriGeometryPoint",
        "layers": "all:ch.bfs.gebaeude_wohnungs_register",
        "sr": "2056",
        "geometryFormat": "geojson",
        "returnGeometry": "false",
        "mapExtent": f"{xmin},{ymin},{xmax},{ymax}",
        "imageDisplay": "400,300,96",
        "tolerance": "10"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("results"):
        return data["results"][0].get("properties", {})
    return {}

def generer_rapport_regbl(regbl_data, dossier_projet, rue, localite):
    """Genere un fichier texte avec les donnees RegBL"""
    
    contenu = f"""INFORMATIONS REGBL - {rue}, {localite}
{'='*50}
Genere le: {datetime.now().strftime("%d.%m.%Y %H:%M")}

IDENTIFICATION
--------------
EGID: {regbl_data.get('egid', 'N/A')}
EGRID: {regbl_data.get('egrid', 'N/A')}
Adresse: {regbl_data.get('strname_deinr', 'N/A')}
NPA: {regbl_data.get('dplz4', 'N/A')}
Localite: {regbl_data.get('ggdename', 'N/A')}
Canton: {regbl_data.get('gdekt', 'N/A')}

CARACTERISTIQUES DU BATIMENT
----------------------------
Annee de construction: {regbl_data.get('gbauj', 'N/A')}
Surface au sol: {regbl_data.get('garea', 'N/A')} m2
Volume: {regbl_data.get('gvol', 'N/A')} m3
Nombre de logements: {regbl_data.get('ganzwhg', 'N/A')}
Categorie: {regbl_data.get('gkat', 'N/A')}
Classe: {regbl_data.get('gklas', 'N/A')}
N parcelle: {regbl_data.get('lparz', 'N/A')}

CHAUFFAGE
---------
Systeme 1: {regbl_data.get('gwaerzh1', 'N/A')} (energie: {regbl_data.get('genh1', 'N/A')})
Systeme 2: {regbl_data.get('gwaerzh2', 'N/A')} (energie: {regbl_data.get('genh2', 'N/A')})

EAU CHAUDE
----------
Systeme 1: {regbl_data.get('gwaerzw1', 'N/A')} (energie: {regbl_data.get('genw1', 'N/A')})
Systeme 2: {regbl_data.get('gwaerzw2', 'N/A')} (energie: {regbl_data.get('genw2', 'N/A')})
"""
    
    fichier = dossier_projet / "5. Rapport" / "53. Annexes" / f"{rue}_{localite}_RegBL.txt"
    fichier.write_text(contenu, encoding="utf-8")
    print(f"\n[REGBL] Rapport cree: {fichier.name}")
    return fichier

# ============================================
# NOTION
# ============================================

def creer_page_notion(rue, localite, montant_offre, type_projet="CECB"):
    """Cree une page dans la base de donnees Notion"""
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Nom": {
                "title": [{"text": {"content": f"{rue} {localite}"}}]
            },
            "Type": {
                "select": {"name": type_projet}
            },
            "Localisation": {
                "rich_text": [{"text": {"content": localite}}]
            },
            "Offre": {
                "number": float(montant_offre) if montant_offre else 0
            },
            "Dessinateur": {
                "status": {"name": "Pas commencé"}
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    # Debug
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"[OK] Page Notion creee: {rue} {localite}")
        return response.json()
    else:
        print(f"[!] Erreur Notion: {response.text}")
        return None

# ============================================
# SCRIPT PRINCIPAL
# ============================================

def main():
    print("=" * 50)
    print("  OFFRE ACCEPTEE - Eta Consult Sarl")
    print("=" * 50)
    
    # Prendre le numero d'offre en argument ou le demander
    if len(sys.argv) > 1:
        numero_offre = sys.argv[1].strip()
    else:
        numero_offre = input("\nNumero d'offre Bexio: ").strip()
    
    if not numero_offre:
        print("[X] Numero d'offre requis!")
        print("Usage: python script.py <numero_offre>")
        sys.exit(1)
    
    try:
        # 1. Recuperer l'offre
        print(f"\n[BEXIO] Recuperation de l'offre {numero_offre}...")
        offre = get_offre(numero_offre)
        
        titre = offre.get("title", "")
        document_nr = offre.get("document_nr", "")
        montant = offre.get("total", 0)
        
        print(f"   Titre: {titre}")
        print(f"   Montant: {montant} CHF")
        
        # 2. Parser le titre
        infos = parse_titre_offre(titre)
        if not infos:
            print("[X] Impossible de continuer sans les infos d'adresse")
            input("\nAppuie sur Entree pour fermer...")
            return
        
        rue = infos["rue"]
        npa = infos["npa"]
        localite = infos["localite"]
        type_projet = infos["type"]
        
        # 3. Creer les dossiers
        dossier_projet = creer_structure_dossiers(rue, localite)
        
        # 4. Copier les templates
        copier_templates(dossier_projet, rue, localite)
        
        # 5. Telecharger et sauvegarder le PDF de l'offre
        print(f"\n[PDF] Telechargement...")
        try:
            pdf_base64 = get_offre_pdf(numero_offre)
            if pdf_base64:
                pdf_bytes = base64.b64decode(pdf_base64)
                pdf_path = dossier_projet / "1. Admin" / "11. Offre" / f"{document_nr}.pdf"
                pdf_path.write_bytes(pdf_bytes)
                print(f"   [OK] PDF sauvegarde: {document_nr}.pdf")
        except Exception as e:
            print(f"   [!] Erreur PDF: {e}")
        
        # 6. Recuperer coordonnees et RegBL
        print(f"\n[GEO] Recherche geographique...")
        x, y = get_coordonnees(rue, npa, localite)
        
        if x and y:
            print(f"   Coordonnees: {x}, {y}")
            regbl = get_regbl(x, y)
            
            if regbl:
                print(f"   EGID: {regbl.get('egid', 'N/A')}")
                print(f"   Annee: {regbl.get('gbauj', 'N/A')}")
                generer_rapport_regbl(regbl, dossier_projet, rue, localite)
            else:
                print("   [!] Pas de donnees RegBL trouvees")
        else:
            print("   [!] Coordonnees non trouvees")
        
        # 7. Creer la page Notion
        print(f"\n[NOTION] Creation page...")
        creer_page_notion(rue, localite, montant, type_projet)
        
        # Resume
        print("\n" + "=" * 50)
        print("[OK] TERMINE!")
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
