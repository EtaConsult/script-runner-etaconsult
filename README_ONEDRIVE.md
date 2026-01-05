# Configuration OneDrive API

Ce guide explique comment configurer l'API OneDrive (Microsoft Graph) pour permettre au script `202512_Offres_acceptees.py` de créer des dossiers et fichiers dans OneDrive depuis PythonAnywhere.

## 📋 Prérequis

- Un compte Microsoft (Office 365 ou compte personnel)
- Accès au [Azure Portal](https://portal.azure.com)

## 🔧 Étape 1 : Créer une application Azure

### 1.1 Accéder à Azure Portal

1. Allez sur [https://portal.azure.com](https://portal.azure.com)
2. Connectez-vous avec votre compte Microsoft
3. Dans la barre de recherche, tapez **"App registrations"** (Inscriptions d'applications)
4. Cliquez sur **"New registration"** (Nouvelle inscription)

### 1.2 Configurer l'application

Remplissez le formulaire :

- **Name** (Nom) : `Eta Consult Script Runner` (ou le nom de votre choix)
- **Supported account types** (Types de comptes pris en charge) :
  - Choisissez **"Accounts in this organizational directory only"** si compte Office 365
  - OU **"Accounts in any organizational directory and personal Microsoft accounts"** pour compte personnel
- **Redirect URI** : Laissez vide pour l'instant

Cliquez sur **"Register"** (Inscrire)

### 1.3 Récupérer les identifiants

Une fois l'application créée, vous verrez la page **"Overview"** :

1. **Application (client) ID** : Copiez cette valeur → `ONEDRIVE_CLIENT_ID`
2. **Directory (tenant) ID** : Copiez cette valeur → `ONEDRIVE_TENANT_ID`

## 🔑 Étape 2 : Créer un Client Secret

1. Dans le menu de gauche, cliquez sur **"Certificates & secrets"** (Certificats et secrets)
2. Sous **"Client secrets"**, cliquez sur **"New client secret"** (Nouveau secret client)
3. **Description** : `Script Runner Secret`
4. **Expires** : Choisissez la durée (recommandé : 24 mois)
5. Cliquez sur **"Add"** (Ajouter)
6. ⚠️ **IMPORTANT** : Copiez immédiatement la **Value** (Valeur) → `ONEDRIVE_CLIENT_SECRET`
   - Cette valeur ne sera plus visible après !

## 🔐 Étape 3 : Configurer les permissions

1. Dans le menu de gauche, cliquez sur **"API permissions"** (Autorisations de l'API)
2. Cliquez sur **"Add a permission"** (Ajouter une autorisation)
3. Sélectionnez **"Microsoft Graph"**
4. Choisissez **"Application permissions"** (Autorisations d'application)
5. Recherchez et ajoutez ces permissions :
   - `Files.ReadWrite.All` - Lire et écrire des fichiers dans tous les collections de sites
   - `Sites.ReadWrite.All` - Lire et écrire des éléments dans tous les collections de sites (optionnel)
6. Cliquez sur **"Add permissions"** (Ajouter les autorisations)
7. ⚠️ **IMPORTANT** : Cliquez sur **"Grant admin consent for [Your Organization]"** (Accorder le consentement administrateur)
   - Confirmez en cliquant **"Yes"**

## ⚙️ Étape 4 : Configurer config.py

Éditez le fichier `config.py` et remplacez :

```python
# OneDrive API (Microsoft Graph)
ONEDRIVE_CLIENT_ID = "votre-application-client-id"
ONEDRIVE_CLIENT_SECRET = "votre-client-secret-value"
ONEDRIVE_TENANT_ID = "votre-directory-tenant-id"  # Ou "common"
```

### Exemple :
```python
ONEDRIVE_CLIENT_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
ONEDRIVE_CLIENT_SECRET = "xYz~AbC123-dEf456_GhI789.jKl012"
ONEDRIVE_TENANT_ID = "9876fedc-ba98-7654-3210-fedcba987654"
```

## 📦 Étape 5 : Installer les dépendances

Sur PythonAnywhere, installez la bibliothèque MSAL :

```bash
pip install msal
```

## ✅ Étape 6 : Tester la connexion

Créez un script de test :

```python
from scripts.onedrive_client import OneDriveClient
from config import ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET, ONEDRIVE_TENANT_ID

# Créer le client
client = OneDriveClient(
    client_id=ONEDRIVE_CLIENT_ID,
    client_secret=ONEDRIVE_CLIENT_SECRET,
    tenant_id=ONEDRIVE_TENANT_ID
)

# Lister le contenu de la racine
items = client.list_folder_contents()
if items:
    print(f"✅ Connexion réussie ! {len(items)} éléments trouvés.")
    for item in items[:5]:  # Afficher les 5 premiers
        print(f"  - {item['name']}")
else:
    print("❌ Échec de la connexion")
```

## 🗂️ Structure OneDrive attendue

Le script s'attend à trouver cette structure dans votre OneDrive :

```
OneDrive/
├── Documents_Eta Consult/
│   ├── 12. Dossiers actifs/     (Dossiers de projets)
│   └── MODELE/                   (Fichiers templates)
│       ├── Rue n_Localite.3dm
│       ├── Rue n_Localite.gh
│       └── Rue n_Localite.bld
```

## 🔧 Dépannage

### Erreur : "AADSTS700016: Application not found"
- Vérifiez que `ONEDRIVE_CLIENT_ID` est correct
- Assurez-vous d'avoir bien créé l'application dans Azure Portal

### Erreur : "AADSTS7000215: Invalid client secret"
- Le `ONEDRIVE_CLIENT_SECRET` est incorrect ou expiré
- Créez un nouveau secret dans Azure Portal

### Erreur : "Insufficient privileges"
- Les permissions `Files.ReadWrite.All` n'ont pas été ajoutées
- OU le consentement administrateur n'a pas été accordé
- Retournez à l'Étape 3

### Erreur 401 Unauthorized
- Le token a expiré
- Redémarrez le script (un nouveau token sera généré automatiquement)

## 📚 Ressources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/api/overview)
- [OneDrive API Reference](https://learn.microsoft.com/en-us/graph/api/resources/onedrive)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)

## 🔒 Sécurité

⚠️ **NE JAMAIS** :
- Commiter `config.py` dans Git
- Partager vos credentials (Client ID, Secret, Token)
- Exposer votre Client Secret publiquement

✅ **TOUJOURS** :
- Garder `config.py` dans `.gitignore`
- Régénérer les secrets si compromis
- Utiliser des permissions minimales nécessaires
