# Guide de Déploiement - PythonAnywhere

Ce guide explique comment déployer votre tableau de bord sur PythonAnywhere (compte gratuit).

L'application sera accessible via : `https://votre-username.pythonanywhere.com`

## Prérequis

1. Un compte PythonAnywhere gratuit (Beginner)
2. Le code source de l'application

---

## Étape 1 : Créer un compte PythonAnywhere

1. Aller sur https://www.pythonanywhere.com
2. Cliquer sur **"Pricing & signup"**
3. Choisir le plan **"Beginner"** (gratuit)
4. Créer votre compte avec email et mot de passe
5. Confirmer votre email

---

## Étape 2 : Télécharger le code sur PythonAnywhere

### Option A : Via GitHub (Recommandé)

1. **Sur votre machine locale**, créer un repository GitHub :
   ```bash
   cd "C:\Users\info\OneDrive\Documents_Eta Consult\18. Scripts\202512_Script_runner"
   git init
   git add .
   git commit -m "Initial commit - Script Runner avec authentification"
   ```

2. Créer un nouveau repository sur GitHub (https://github.com/new)
   - Nom : `script-runner-etaconsult`
   - Privé ou Public selon vos besoins

3. Pousser le code :
   ```bash
   git remote add origin https://github.com/votre-username/script-runner-etaconsult.git
   git branch -M main
   git push -u origin main
   ```

4. **Sur PythonAnywhere**, dans le Dashboard > Consoles > Bash :
   ```bash
   git clone https://github.com/votre-username/script-runner-etaconsult.git
   cd script-runner-etaconsult
   ```

### Option B : Upload manuel

1. Dashboard > Files
2. Créer un dossier `script-runner`
3. Uploader tous les fichiers manuellement

---

## Étape 3 : Créer un environnement virtuel et installer les dépendances

Dans la console Bash PythonAnywhere :

```bash
cd ~/script-runner-etaconsult  # ou ~/script-runner
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Étape 4 : Configuration de la clé secrète

**IMPORTANT** : Changer la clé secrète en production !

1. Éditer `app.py`
2. Remplacer :
   ```python
   app.config['SECRET_KEY'] = 'votre-cle-secrete-a-changer-en-production-2025'
   ```

   Par une clé aléatoire générée. Dans la console Python :
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

---

## Étape 5 : Configurer la Web App

1. Dashboard > Web
2. Cliquer sur **"Add a new web app"**
3. Choisir :
   - **Domain** : Si compte gratuit → `votre-username.pythonanywhere.com`
   - **Framework** : Manual configuration
   - **Python version** : Python 3.10

4. Configuration :
   - **Source code** : `/home/votre-username/script-runner-etaconsult`
   - **Working directory** : `/home/votre-username/script-runner-etaconsult`
   - **Virtualenv** : `/home/votre-username/script-runner-etaconsult/venv`

5. Éditer le fichier WSGI :
   - Cliquer sur le lien du fichier WSGI (ex: `/var/www/votre_username_pythonanywhere_com_wsgi.py`)
   - Remplacer tout le contenu par :

   ```python
   import sys
   import os

   # Ajouter le chemin vers votre application
   path = '/home/votre-username/script-runner-etaconsult'
   if path not in sys.path:
       sys.path.insert(0, path)

   # Importer votre application Flask
   from app import app as application
   ```

6. Cliquer sur **Reload** en haut de la page

---

## Étape 6 : Activer HTTPS (SSL)

1. Dashboard > Web
2. Section **"Security"**
3. Cliquer sur **"Force HTTPS"** (activé par défaut)
4. PythonAnywhere fournit automatiquement un certificat SSL gratuit

Votre site sera accessible via : `https://votre-username.pythonanywhere.com`

---

## Étape 7 : Fichiers de configuration importants

### `.gitignore` (à créer avant de push sur GitHub)

```
# Fichiers sensibles - NE PAS COMMITER
config.py
users.json
*.pyc
__pycache__/

# Environnement virtuel
venv/
env/

# Logs
*.log

# OS
.DS_Store
Thumbs.db
```

### `config.py.example`

Votre fichier `config.py.example` doit contenir :
- Les structures des credentials sans les vraies valeurs
- Instructions pour créer `config.py`

**IMPORTANT** : Sur PythonAnywhere, créer `config.py` manuellement avec vos vraies credentials API.

---

## Étape 8 : Premier démarrage et création des utilisateurs

1. Accéder à votre site : `https://votre-username.pythonanywhere.com`
2. Première connexion avec l'admin par défaut :
   - Email : `admin@etaconsult.org`
   - Mot de passe : `admin123`

3. **IMMÉDIATEMENT** après la première connexion :
   - Aller dans 👥 Utilisateurs
   - Modifier le compte admin
   - Changer le mot de passe par un mot de passe fort

4. Créer vos utilisateurs :
   - Admins : accès complet
   - Utilisateurs : pas d'accès aux tests, textes, tarifs, gestion utilisateurs

---

## Étape 9 : Mise à jour de l'application

### Via GitHub

1. **Sur votre machine locale**, faire les modifications
2. Commiter et pusher :
   ```bash
   git add .
   git commit -m "Description des modifications"
   git push
   ```

3. **Sur PythonAnywhere**, dans la console Bash :
   ```bash
   cd ~/script-runner-etaconsult
   git pull
   ```

4. Dashboard > Web > Reload

### Upload manuel

1. Dashboard > Files
2. Remplacer les fichiers modifiés
3. Dashboard > Web > Reload

---

## Gestion des utilisateurs

### Rôles disponibles

| Rôle | Accès |
|------|-------|
| **admin** | Accès complet : scripts, devis, tests, tarifs, textes, gestion utilisateurs |
| **user** | Accès limité : scripts, devis uniquement (pas de tests, admin, modifications) |

### Créer un utilisateur

1. Se connecter en tant qu'admin
2. Aller dans **👥 Utilisateurs**
3. Cliquer sur **+ Nouvel Utilisateur**
4. Remplir :
   - Email
   - Mot de passe (min 6 caractères)
   - Rôle (admin ou user)

### Modifier un utilisateur

1. **👥 Utilisateurs** > **✏️ Modifier**
2. Changer email, mot de passe ou rôle
3. Sauvegarder

### Supprimer un utilisateur

1. **👥 Utilisateurs** > **🗑️ Supprimer**
2. Confirmer la suppression
3. **Note** : Impossible de supprimer son propre compte

---

## Sécurité - Points importants

### 1. Clé secrète Flask
- **TOUJOURS** changer `SECRET_KEY` en production
- Utiliser une clé aléatoire longue (32+ caractères)

### 2. Credentials API
- **NE JAMAIS** commiter `config.py` dans Git
- Utiliser `.gitignore` pour exclure les fichiers sensibles
- Sur PythonAnywhere, créer `config.py` manuellement

### 3. Mots de passe
- Changer le mot de passe admin par défaut **immédiatement**
- Utiliser des mots de passe forts (12+ caractères, majuscules, chiffres, symboles)
- Les mots de passe sont hachés avec scrypt (sécurisé)

### 4. HTTPS
- **TOUJOURS** activer HTTPS en production
- PythonAnywhere fournit des certificats Let's Encrypt gratuits

### 5. Fichier users.json
- Contient les comptes utilisateurs (emails + mots de passe hachés)
- **NE PAS** commiter dans Git
- Faire des backups réguliers

---

## Dépannage

### L'application ne démarre pas
1. Vérifier les logs : Dashboard > Web > Error log
2. Vérifier que toutes les dépendances sont installées
3. Vérifier les chemins dans le fichier WSGI

### Erreur 404
1. Vérifier que le fichier WSGI pointe vers le bon dossier
2. Vérifier que `from app import app` fonctionne dans la console Python

### Erreur "Secret key not set"
1. Vérifier que `app.config['SECRET_KEY']` est défini dans `app.py`

### Erreur de connexion
1. Vérifier que `users.json` existe
2. Vérifier les credentials (email/mot de passe)
3. Effacer les cookies du navigateur

---

## Coûts

**Plan actuel : PythonAnywhere Beginner (GRATUIT)**

| Caractéristique | Inclus |
|-----------------|--------|
| URL | `username.pythonanywhere.com` |
| HTTPS/SSL | ✅ Gratuit |
| Trafic | 100 000 hits/jour |
| RAM | 512 MB |
| Espace disque | 512 MB |
| Consoles | Bash, Python, etc. |

**Limitations** :
- URL fixe (pas de domaine personnalisé)
- Ressources limitées (suffisant pour usage interne)
- Application dort après 3 mois d'inactivité (se réveille au premier accès)

**Pour upgrader vers un domaine personnalisé** (optionnel, voir section ci-dessous) :
- Web Developer : 5$/mois
- Permet `dashboard.etaconsult.org` au lieu de `username.pythonanywhere.com`

---

## Support

### Documentation PythonAnywhere
- Help : https://help.pythonanywhere.com
- Forums : https://www.pythonanywhere.com/forums/

### Logs et debugging
- Error log : Dashboard > Web > Error log
- Server log : Dashboard > Web > Server log
- Console Bash : Dashboard > Consoles > Bash

---

## Checklist finale

Avant la mise en production :

- [ ] ✅ Compte PythonAnywhere créé
- [ ] ✅ Code uploadé (GitHub ou manuel)
- [ ] ✅ Environnement virtuel créé et dépendances installées
- [ ] ✅ Clé secrète Flask changée
- [ ] ✅ config.py créé sur PythonAnywhere avec vraies credentials
- [ ] ✅ WSGI configuré correctement
- [ ] ✅ Web app créée et Reload effectué
- [ ] ✅ HTTPS activé (par défaut)
- [ ] ✅ Site accessible via `https://username.pythonanywhere.com`
- [ ] ✅ Mot de passe admin changé après première connexion
- [ ] ✅ Utilisateurs créés avec rôles appropriés
- [ ] ✅ Tests effectués (login, scripts, permissions)

---

## (Optionnel) Configuration d'un sous-domaine personnalisé

Si plus tard vous souhaitez utiliser `dashboard.etaconsult.org` au lieu de `username.pythonanywhere.com` :

### Prérequis
- Compte **Web Developer** PythonAnywhere (5$/mois minimum)
- Accès à la gestion DNS de etaconsult.org

### Étape 1 : Upgrader le compte PythonAnywhere
1. Dashboard > Account
2. Passer au plan **Web Developer** (5$/mois)

### Étape 2 : Configuration DNS
1. Aller dans la gestion DNS de etaconsult.org (chez votre registrar)
2. Créer un enregistrement CNAME :
   - **Type** : CNAME
   - **Nom** : `dashboard` (ou `scripts`, `admin`, etc.)
   - **Valeur** : `votre-username.pythonanywhere.com.`
   - **TTL** : 3600 (ou automatique)

Exemples de sous-domaines possibles :
- `dashboard.etaconsult.org` → Tableau de bord
- `scripts.etaconsult.org` → Script runner
- `admin.etaconsult.org` → Administration

### Étape 3 : Configuration sur PythonAnywhere
1. Dashboard > Web > Web app section
2. Section **"Custom domains"**
3. Cliquer sur **"Add a new custom domain"**
4. Entrer : `dashboard.etaconsult.org`
5. PythonAnywhere vérifiera automatiquement le DNS (peut prendre 24-48h pour propagation)

### Étape 4 : HTTPS pour le domaine personnalisé
1. Une fois le domaine validé
2. Dashboard > Web > Security
3. Cliquer sur **"Force HTTPS"**
4. PythonAnywhere générera automatiquement un certificat Let's Encrypt

**Note** : Le certificat SSL pour le domaine personnalisé est également gratuit avec Let's Encrypt.

### Vérification DNS
Pour vérifier la propagation DNS : https://www.whatsmydns.net

---

**Fait avec ❤️ pour Êta Consult Sàrl**

Date de création : 2025-01-04
Date de mise à jour : 2025-01-04
