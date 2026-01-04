# -*- coding: utf-8 -*-
"""
Système d'authentification pour Script Runner
Gestion des utilisateurs avec Flask-Login
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime

USERS_FILE = 'users.json'

# ==========================================
# CLASSE USER POUR FLASK-LOGIN
# ==========================================

class User(UserMixin):
    """Classe utilisateur pour Flask-Login"""

    def __init__(self, id, email, password_hash, role='user', created_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'admin' ou 'user'
        self.created_at = created_at or datetime.now().isoformat()

    def check_password(self, password):
        """Vérifie si le mot de passe est correct"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        """Vérifie si l'utilisateur est admin"""
        return self.role == 'admin'

    def to_dict(self):
        """Convertit l'utilisateur en dictionnaire pour sauvegarde"""
        return {
            'id': self.id,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'created_at': self.created_at
        }

    @staticmethod
    def from_dict(data):
        """Crée un utilisateur depuis un dictionnaire"""
        return User(
            id=data['id'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=data.get('role', 'user'),
            created_at=data.get('created_at')
        )


# ==========================================
# GESTION DES UTILISATEURS (FICHIER JSON)
# ==========================================

def load_users():
    """Charge tous les utilisateurs depuis users.json"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
                return {user_id: User.from_dict(user_data)
                       for user_id, user_data in users_data.items()}
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement des utilisateurs: {e}")
            return {}
    return {}


def save_users(users):
    """Sauvegarde tous les utilisateurs dans users.json"""
    try:
        users_data = {user_id: user.to_dict()
                     for user_id, user in users.items()}
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des utilisateurs: {e}")
        return False


def get_user_by_id(user_id):
    """Récupère un utilisateur par son ID"""
    users = load_users()
    return users.get(user_id)


def get_user_by_email(email):
    """Récupère un utilisateur par son email"""
    users = load_users()
    for user in users.values():
        if user.email.lower() == email.lower():
            return user
    return None


def create_user(email, password, role='user'):
    """Crée un nouveau utilisateur"""
    users = load_users()

    # Vérifier si l'email existe déjà
    if get_user_by_email(email):
        return None, "Un utilisateur avec cet email existe déjà"

    # Générer un ID unique (timestamp)
    user_id = str(int(datetime.now().timestamp() * 1000))

    # Créer l'utilisateur
    password_hash = generate_password_hash(password)
    user = User(id=user_id, email=email, password_hash=password_hash, role=role)

    # Sauvegarder
    users[user_id] = user
    if save_users(users):
        return user, None
    else:
        return None, "Erreur lors de la sauvegarde"


def update_user(user_id, email=None, password=None, role=None):
    """Met à jour un utilisateur existant"""
    users = load_users()

    if user_id not in users:
        return False, "Utilisateur non trouvé"

    user = users[user_id]

    # Mettre à jour les champs
    if email:
        # Vérifier si le nouvel email n'est pas déjà utilisé
        existing = get_user_by_email(email)
        if existing and existing.id != user_id:
            return False, "Cet email est déjà utilisé"
        user.email = email

    if password:
        user.password_hash = generate_password_hash(password)

    if role:
        user.role = role

    # Sauvegarder
    users[user_id] = user
    if save_users(users):
        return True, None
    else:
        return False, "Erreur lors de la sauvegarde"


def delete_user(user_id):
    """Supprime un utilisateur"""
    users = load_users()

    if user_id not in users:
        return False, "Utilisateur non trouvé"

    del users[user_id]

    if save_users(users):
        return True, None
    else:
        return False, "Erreur lors de la sauvegarde"


def get_all_users():
    """Récupère tous les utilisateurs (pour l'admin)"""
    users = load_users()
    return list(users.values())


def create_default_admin():
    """Crée un utilisateur admin par défaut si aucun utilisateur n'existe"""
    users = load_users()

    if len(users) == 0:
        print("📝 Création d'un utilisateur admin par défaut...")
        user, error = create_user(
            email='admin@etaconsult.org',
            password='admin123',  # À CHANGER !
            role='admin'
        )

        if user:
            print("✅ Utilisateur admin créé avec succès")
            print("   Email: admin@etaconsult.org")
            print("   Mot de passe: admin123")
            print("   ⚠️  CHANGEZ CE MOT DE PASSE DÈS LA PREMIÈRE CONNEXION !")
            return user
        else:
            print(f"❌ Erreur lors de la création de l'admin: {error}")
            return None

    return None
