# Migration vers l'API OneDrive - Guide complet

## 📦 Fichiers créés

### 1. Module OneDrive
- **Fichier** : `scripts/onedrive_client.py`
- **Description** : Module Python pour gérer l'API OneDrive (Microsoft Graph)
- **Fonctionnalités** :
  - Authentification via MSAL (Client Credentials Flow)
  - Création de dossiers
  - Upload de fichiers (bytes et texte)
  - Téléchargement de fichiers
  - Copie de fichiers
  - Listing de contenu

### 2. Configuration
- **Fichier** : `config.py`
- **Ajouts** :
  ```python
  ONEDRIVE_CLIENT_ID = "TO_BE_CONFIGURED"
  ONEDRIVE_CLIENT_SECRET = "TO_BE_CONFIGURED"
  ONEDRIVE_TENANT_ID = "common"
  ```

### 3. Documentation
- **Fichier** : `README_ONEDRIVE.md`
- **Contenu** : Instructions complètes pour configurer Azure App Registration

## 🔧 Modifications nécessaires dans 202512_Offres_acceptees.py

### Imports à ajouter (début du fichier)

```python
# Importer le client OneDrive
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.onedrive_client import OneDriveClient
from config import ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET, ONEDRIVE_TENANT_ID
```

### Remplacer les chemins locaux

**AVANT** (lignes 26-27):
```python
DOSSIERS_ACTIFS = Path(r"C:\Users\info\OneDrive\Documents_Eta Consult\12. Dossiers actifs")
DOSSIER_MODELES = Path(r"C:\Users\info\OneDrive\Documents_Eta Consult\MODELE")
```

**APRÈS**:
```python
# Chemins dans OneDrive (relatifs à la racine OneDrive)
DOSSIERS_ACTIFS_PATH = "/Documents_Eta Consult/12. Dossiers actifs"
DOSSIER_MODELES_PATH = "/Documents_Eta Consult/MODELE"

# Initialiser le client OneDrive
onedrive = OneDriveClient(
    client_id=ONEDRIVE_CLIENT_ID,
    client_secret=ONEDRIVE_CLIENT_SECRET,
    tenant_id=ONEDRIVE_TENANT_ID
)
```

### Fonction creer_structure_dossiers (lignes 83-117)

**AVANT**:
```python
def creer_structure_dossiers(rue, localite):
    date_prefix = datetime.now().strftime("%Y%m")
    nom_dossier = f"{date_prefix}_{rue}_{localite}"
    dossier_principal = DOSSIERS_ACTIFS / nom_dossier
    # ...
    dossier_principal.mkdir(exist_ok=True)
    for sous_dossier in sous_dossiers:
        chemin = dossier_principal / sous_dossier
        chemin.mkdir(parents=True, exist_ok=True)
```

**APRÈS**:
```python
def creer_structure_dossiers(rue, localite):
    date_prefix = datetime.now().strftime("%Y%m")
    nom_dossier = f"{date_prefix}_{rue}_{localite}"

    # Chemin complet dans OneDrive
    dossier_principal_path = f"{DOSSIERS_ACTIFS_PATH}/{nom_dossier}"

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

    print(f"\n[DOSSIER] Creation OneDrive: {nom_dossier}")

    # Créer le dossier principal
    onedrive.create_folder(nom_dossier, DOSSIERS_ACTIFS_PATH)

    # Créer tous les sous-dossiers
    for sous_dossier in sous_dossiers:
        full_path = f"{dossier_principal_path}/{sous_dossier}"
        parent_path = str(Path(full_path).parent).replace("\\", "/")
        folder_name = Path(sous_dossier).name

        onedrive.create_folder(folder_name, parent_path)
        print(f"   [OK] {sous_dossier}")

    return dossier_principal_path  # Retourne le chemin OneDrive
```

### Fonction copier_templates (lignes 123-143)

**AVANT**:
```python
def copier_templates(dossier_projet, rue, localite):
    nom_fichier = f"{rue}_{localite}"
    # ...
    for template, destination, nouveau_nom in templates:
        source = DOSSIER_MODELES / template
        dest = dossier_projet / destination / nouveau_nom
        if source.exists():
            shutil.copy2(source, dest)
```

**APRÈS**:
```python
def copier_templates(dossier_projet_path, rue, localite):
    nom_fichier = f"{rue}_{localite}"

    templates = [
        ("Rue n_Localite.3dm", "3. CAO", f"{nom_fichier}.3dm"),
        ("Rue n_Localite.gh", "3. CAO", f"{nom_fichier}.gh"),
        ("Rue n_Localite.bld", "4. Lesosai", f"{nom_fichier}.bld"),
    ]

    print(f"\n[TEMPLATES] Copie OneDrive:")
    for template, destination, nouveau_nom in templates:
        source_path = f"{DOSSIER_MODELES_PATH}/{template}"
        dest_path = f"{dossier_projet_path}/{destination}"

        # Copier le fichier via OneDrive API
        success = onedrive.copy_file(source_path, dest_path, nouveau_nom)

        if success:
            print(f"   [OK] {template} -> {destination}/{nouveau_nom}")
        else:
            print(f"   [!] Echec copie: {template}")
```

### Fonction generer_rapport_regbl (lignes 197-237)

**AVANT**:
```python
def generer_rapport_regbl(regbl_data, dossier_projet, rue, localite):
    contenu = f"""INFORMATIONS REGBL..."""
    fichier = dossier_projet / "5. Rapport" / "53. Annexes" / f"{rue}_{localite}_RegBL.txt"
    fichier.write_text(contenu, encoding="utf-8")
```

**APRÈS**:
```python
def generer_rapport_regbl(regbl_data, dossier_projet_path, rue, localite):
    contenu = f"""INFORMATIONS REGBL - {rue}, {localite}
{'='*50}
Genere le: {datetime.now().strftime("%d.%m.%Y %H:%M")}

IDENTIFICATION
--------------
EGID: {regbl_data.get('egid', 'N/A')}
...
"""

    # Upload vers OneDrive
    file_name = f"{rue}_{localite}_RegBL.txt"
    dest_path = f"{dossier_projet_path}/5. Rapport/53. Annexes"

    result = onedrive.upload_text_file(contenu, file_name, dest_path)

    if result:
        print(f"\n[REGBL] Rapport cree OneDrive: {file_name}")
    else:
        print(f"\n[REGBL] Erreur creation rapport")

    return file_name
```

### Sauvegarder le PDF (lignes 336-346)

**AVANT**:
```python
pdf_path = dossier_projet / "1. Admin" / "11. Offre" / f"{document_nr}.pdf"
pdf_path.write_bytes(pdf_bytes)
```

**APRÈS**:
```python
# Upload PDF vers OneDrive
pdf_filename = f"{document_nr}.pdf"
pdf_dest_path = f"{dossier_projet_path}/1. Admin/11. Offre"

result = onedrive.upload_file(pdf_bytes, pdf_filename, pdf_dest_path)

if result:
    print(f"   [OK] PDF sauvegarde OneDrive: {pdf_filename}")
else:
    print(f"   [!] Erreur upload PDF")
```

## 📋 Dépendances Python

Ajouter dans `requirements.txt` :

```
msal>=1.25.0
```

Installation sur PythonAnywhere :
```bash
pip install msal
```

## ✅ Checklist de migration

- [x] Créer `onedrive_client.py`
- [x] Ajouter credentials dans `config.py`
- [x] Créer `README_ONEDRIVE.md`
- [ ] Configurer Azure App Registration (suivre README_ONEDRIVE.md)
- [ ] Modifier `202512_Offres_acceptees.py`
- [ ] Tester sur PythonAnywhere
- [ ] Déployer en production

## 🧪 Test rapide

Avant de modifier le script principal, testez la connexion :

```python
from scripts.onedrive_client import OneDriveClient
from config import ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET, ONEDRIVE_TENANT_ID

client = OneDriveClient(
    client_id=ONEDRIVE_CLIENT_ID,
    client_secret=ONEDRIVE_CLIENT_SECRET,
    tenant_id=ONEDRIVE_TENANT_ID
)

# Test : créer un dossier
client.create_folder("TEST_SCRIPT", "/Documents_Eta Consult")

# Test : lister le contenu
items = client.list_folder_contents("/Documents_Eta Consult")
if items:
    print(f"✅ {len(items)} éléments trouvés")
```

## 📝 Notes importantes

1. **Chemins OneDrive** : Toujours utiliser `/` (slash), jamais `\` (backslash)
2. **Chemins relatifs** : Tous les chemins sont relatifs à la racine OneDrive de l'utilisateur
3. **Authentification** : Le token est automatiquement géré par MSAL (pas besoin de le renouveler manuellement)
4. **Erreurs** : Vérifier les logs pour comprendre les erreurs d'API

## 🔄 Rollback

En cas de problème, la version locale originale est sauvegardée dans :
- `scripts/202512_Offres_acceptees_LOCAL.py`

Pour revenir en arrière :
```bash
cp scripts/202512_Offres_acceptees_LOCAL.py scripts/202512_Offres_acceptees.py
```
