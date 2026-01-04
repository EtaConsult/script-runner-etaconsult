# Système d'Authentification - Documentation

Ce document décrit le système d'authentification implémenté dans l'application Script Runner.

## Vue d'ensemble

L'application utilise **Flask-Login** pour gérer l'authentification des utilisateurs avec deux niveaux d'accès :
- **Admin** : Accès complet à toutes les fonctionnalités
- **User** : Accès limité (lecture seule pour certaines sections)

## Architecture

### Fichiers principaux

| Fichier | Description |
|---------|-------------|
| `auth.py` | Gestion des utilisateurs (création, modification, suppression) |
| `users.json` | Base de données des utilisateurs (emails + mots de passe hachés) |
| `templates/login.html` | Page de connexion |
| `templates/admin_users.html` | Interface de gestion des utilisateurs |

### Structure de `users.json`

```json
{
  "1767522312539": {
    "id": "1767522312539",
    "email": "admin@etaconsult.org",
    "password_hash": "scrypt:32768:8:1$...",
    "role": "admin",
    "created_at": "2026-01-04T11:25:12.632862"
  }
}
```

## Niveaux d'accès

### Admin (role: "admin")

Accès complet :
- ✅ Exécution de tous les scripts
- ✅ Création de devis CECB
- ✅ Accès aux tests (`/tests`)
- ✅ Modification des tarifs (`/admin/tarifs`)
- ✅ Modification des textes (`/admin/textes`)
- ✅ Gestion des utilisateurs (`/admin/users`)
- ✅ Toutes les routes API

### Utilisateur (role: "user")

Accès limité :
- ✅ Exécution de tous les scripts
- ✅ Création de devis CECB
- ❌ Pas d'accès aux tests
- ❌ Pas de modification des tarifs
- ❌ Pas de modification des textes
- ❌ Pas de gestion des utilisateurs
- ✅ Routes API nécessaires (building_data, etc.)

## Utilisation

### Première connexion

1. Démarrer l'application : `python app.py`
2. Aller sur http://localhost:5000
3. Se connecter avec le compte admin par défaut :
   - **Email** : `admin@etaconsult.org`
   - **Mot de passe** : `admin123`

⚠️ **IMPORTANT** : Changez ce mot de passe dès la première connexion !

### Changer le mot de passe admin

1. Se connecter en tant qu'admin
2. Aller dans **👥 Utilisateurs**
3. Cliquer sur **✏️ Modifier** à côté de votre compte
4. Entrer un nouveau mot de passe fort
5. Sauvegarder

### Créer un utilisateur

1. Se connecter en tant qu'admin
2. Aller dans **👥 Utilisateurs**
3. Cliquer sur **+ Nouvel Utilisateur**
4. Remplir le formulaire :
   - Email (sera l'identifiant de connexion)
   - Mot de passe (minimum 6 caractères)
   - Rôle (admin ou user)
5. Cliquer sur **Créer**

### Modifier un utilisateur

1. **👥 Utilisateurs** > **✏️ Modifier**
2. Modifier :
   - Email
   - Mot de passe (laisser vide pour ne pas changer)
   - Rôle
3. Cliquer sur **Mettre à jour**

### Supprimer un utilisateur

1. **👥 Utilisateurs** > **🗑️ Supprimer**
2. Confirmer la suppression

⚠️ Impossible de supprimer son propre compte

## Sécurité

### Hachage des mots de passe

Les mots de passe sont hachés avec **Werkzeug scrypt** :
- Algorithme : scrypt
- Paramètres : `32768:8:1` (secure defaults)
- Les mots de passe en clair ne sont jamais stockés

### Secret Key Flask

La clé secrète est utilisée pour signer les sessions :
```python
app.config['SECRET_KEY'] = 'votre-cle-secrete-a-changer-en-production-2025'
```

⚠️ **EN PRODUCTION** : Générer une clé aléatoire forte
```python
import secrets
print(secrets.token_hex(32))
```

### Protection des routes

Toutes les routes (sauf `/login`) sont protégées :

```python
@app.route('/')
@login_required  # Nécessite d'être connecté
def index():
    ...

@app.route('/admin/users')
@login_required     # Nécessite d'être connecté
@admin_required     # Nécessite le rôle admin
def admin_users():
    ...
```

## API d'authentification

### Fonctions disponibles (auth.py)

| Fonction | Description |
|----------|-------------|
| `create_user(email, password, role)` | Crée un utilisateur |
| `get_user_by_id(user_id)` | Récupère un utilisateur par ID |
| `get_user_by_email(email)` | Récupère un utilisateur par email |
| `update_user(user_id, email, password, role)` | Met à jour un utilisateur |
| `delete_user(user_id)` | Supprime un utilisateur |
| `get_all_users()` | Liste tous les utilisateurs |
| `create_default_admin()` | Crée l'admin par défaut si aucun utilisateur |

### Routes d'authentification

| Route | Méthode | Accès | Description |
|-------|---------|-------|-------------|
| `/login` | GET, POST | Public | Page de connexion |
| `/logout` | GET | Connecté | Déconnexion |
| `/admin/users` | GET | Admin | Liste des utilisateurs |
| `/admin/users/create` | POST | Admin | Créer un utilisateur |
| `/admin/users/update/<id>` | POST | Admin | Modifier un utilisateur |
| `/admin/users/delete/<id>` | DELETE | Admin | Supprimer un utilisateur |

## Customisation

### Ajouter un nouveau rôle

1. Dans `auth.py`, modifier la classe `User` :
```python
def is_manager(self):
    return self.role == 'manager'
```

2. Créer un décorateur dans `app.py` :
```python
def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_manager():
            flash('Accès refusé. Rôle manager requis.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
```

3. Utiliser sur les routes :
```python
@app.route('/manager/dashboard')
@login_required
@manager_required
def manager_dashboard():
    ...
```

### Champs utilisateur supplémentaires

Modifier la classe `User` dans `auth.py` :

```python
class User(UserMixin):
    def __init__(self, id, email, password_hash, role='user',
                 created_at=None, first_name=None, last_name=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at or datetime.now().isoformat()
        self.first_name = first_name
        self.last_name = last_name
```

## Dépannage

### Problème : "Incorrect email or password"

**Solution** :
1. Vérifier que `users.json` existe
2. Vérifier l'email (respecte la casse)
3. Si le fichier est corrompu, supprimer `users.json` et redémarrer (crée un nouveau admin)

### Problème : Session expirée trop rapidement

**Solution** : Configurer la durée de session dans `app.py` :
```python
from datetime import timedelta

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=30)
```

### Problème : "Secret key not set"

**Solution** : Vérifier que `app.config['SECRET_KEY']` est défini dans `app.py`

### Problème : Impossible de créer un utilisateur

**Causes possibles** :
1. Email déjà existant → Changer l'email
2. Mot de passe trop court → Minimum 6 caractères
3. Problème d'écriture `users.json` → Vérifier les permissions

## Migration depuis une ancienne version

Si vous upgrader depuis une version sans authentification :

1. **Backup** : Sauvegarder votre application
2. **Installation** : `pip install Flask-Login`
3. **Fichiers** : Copier `auth.py` dans votre projet
4. **Modifications app.py** : Ajouter les imports et la configuration Flask-Login
5. **Routes** : Ajouter `@login_required` sur toutes les routes sensibles
6. **Templates** : Créer `login.html` et modifier `index.html`
7. **Premier démarrage** : L'admin sera créé automatiquement

## Checklist de sécurité

Avant la mise en production :

- [ ] ✅ Clé secrète Flask changée (générer avec `secrets.token_hex(32)`)
- [ ] ✅ Mot de passe admin changé
- [ ] ✅ HTTPS activé (Let's Encrypt sur PythonAnywhere)
- [ ] ✅ `users.json` exclu de Git (dans `.gitignore`)
- [ ] ✅ `config.py` exclu de Git (dans `.gitignore`)
- [ ] ✅ Permissions des fichiers vérifiées sur le serveur
- [ ] ✅ Logs de connexion surveillés
- [ ] ✅ Backup régulier de `users.json`

## Support

### Logs

Les erreurs d'authentification sont loggées dans la console :
```
⚠️  Erreur lors du chargement des utilisateurs: [error]
❌ Erreur lors de la sauvegarde des utilisateurs: [error]
```

### Documentation Flask-Login

- https://flask-login.readthedocs.io/

### Code source

- `auth.py` : Gestion des utilisateurs
- `app.py` : Routes et configuration
- `templates/login.html` : Interface de connexion
- `templates/admin_users.html` : Gestion utilisateurs

---

**Fait avec ❤️ pour Êta Consult Sàrl**

Date de création : 2025-01-04
Version : 1.0
