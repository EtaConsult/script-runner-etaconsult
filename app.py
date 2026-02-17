# -*- coding: utf-8 -*-
"""
Application Flask pour exécuter des scripts Python localement
Évolutif : ajoute facilement de nouveaux scripts
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import subprocess
import os
import json
import sys
import re
import copy
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Importer le système d'authentification
from auth import (User, get_user_by_id, get_user_by_email, create_default_admin,
                 get_all_users, create_user, update_user, delete_user)

# Configurer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Récupérer la clé Google Maps depuis les variables d'environnement
GOOGLE_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

app = Flask(__name__)
CORS(app)  # Active CORS pour toutes les routes

# Configuration de la clé secrète pour les sessions
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-change-in-production')

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///script_runner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importer et initialiser la base de données
from models import db, FormSubmission
db.init_app(app)

# Créer les tables au démarrage si elles n'existent pas
with app.app_context():
    db.create_all()

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirection si non authentifié
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Charge un utilisateur depuis son ID (requis par Flask-Login)"""
    return get_user_by_id(user_id)


# ==========================================
# DÉCORATEUR POUR VÉRIFIER LE RÔLE ADMIN
# ==========================================
def admin_required(f):
    """Décorateur pour restreindre l'accès aux admins uniquement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Accès refusé. Vous devez être administrateur.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# GESTION DES TARIFS
# ==========================================
TARIFS_FILE = 'tarifs.json'

def load_tarifs():
    """Charge les tarifs depuis tarifs.json"""
    if os.path.exists(TARIFS_FILE):
        try:
            with open(TARIFS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement des tarifs: {e}")

    # Tarifs par défaut
    return {
        "base_price": 500,
        "km_factor_proche": 0.9,
        "km_factor_loin": 0.7,
        "km_seuil": 25,
        "surface_factor_petit": 0.6,
        "surface_factor_grand": 0.5,
        "surface_seuil": 750,
        "plus_factor_petit": 3.69,
        "plus_factor_moyen": 2.29,
        "plus_factor_grand": 1.79,
        "plus_seuil_petit": 160,
        "plus_seuil_grand": 750,
        "plus_price_max": 1989,
        "frais_emission_cecb": 80,
        "prix_conseil_incitatif": 0,
        "forfait_normal": 0,
        "forfait_express": 135,
        "forfait_urgent": 270
    }

def save_tarifs(tarifs):
    """Sauvegarde les tarifs dans tarifs.json"""
    try:
        with open(TARIFS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tarifs, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des tarifs: {e}")
        return False

# ==========================================
# GESTION DES TEXTES
# ==========================================
TEXTES_FILE = 'textes.json'

def load_textes():
    """Charge les textes depuis textes.json ou config.py"""
    if os.path.exists(TEXTES_FILE):
        try:
            with open(TEXTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Erreur lors du chargement des textes: {e}")

    # Textes par défaut depuis config.py
    try:
        import config
        return config.TEXTES
    except:
        return {
            "footer_acompte": "Conditions de paiement : Acompte de 30% à la commande, solde à réception du rapport.",
            "prestations_incluses_cecb": "Prestations incluses :<br>- Visite sur site et relevé<br>- Etablissement du CECB®<br>- Rapport de 8 à 12 pages",
            "prestations_non_incluses_cecb": "Prestations non-incluses :<br>- Rapport CECB® Plus<br>- Conseil Chauffez Renouvelable®",
            "prestations_incluses_cecb_plus": "Prestations incluses :<br>- Visite sur site et relevé<br>- Etablissement du CECB® et CECB® Plus<br>- Rapport de 15 à 25 pages<br>- Variantes de rénovation chiffrées",
            "prestations_non_incluses_cecb_plus": "Prestations non-incluses :<br>- Conseil Incitatif Chauffez Renouvelable®",
            "prestations_incluses_conseil": "Prestations incluses :<br>- Conseil personnalisé sur les solutions de chauffage renouvelable<br>- Visite sur site si nécessaire<br>- Recommandations adaptées à votre bâtiment"
        }

def save_textes(textes):
    """Sauvegarde les textes dans textes.json et met à jour config.py"""
    try:
        # Sauvegarder dans textes.json
        with open(TEXTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(textes, f, indent=2, ensure_ascii=False)

        # Mettre à jour config.py
        config_path = 'config.py'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remplacer la section TEXTES dans config.py
            import re
            textes_str = "TEXTES = {\n"
            for key, value in textes.items():
                # Échapper les guillemets dans le texte
                escaped_value = value.replace('"""', '\\"\\"\\"')
                textes_str += f'    "{key}": """{escaped_value}""",\n'
            textes_str += "}"

            # Remplacer la section TEXTES
            pattern = r'TEXTES = \{[^}]*\}'
            new_content = re.sub(pattern, textes_str, content, flags=re.DOTALL)

            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde des textes: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==========================================
# CONFIGURATION DES SCRIPTS
# ==========================================
# Pour ajouter un nouveau script :
# 1. Ajoute ton script dans le dossier 'scripts/'
# 2. Ajoute une entrée dans SCRIPTS ci-dessous
# ==========================================

SCRIPTS = {
    # ---- Tes scripts Bexio ----
    'offres_acceptees': {
        'name': 'Offre Acceptée',
        'file': '202512_Offres_acceptees.py',
        'description': 'Traiter une offre Bexio acceptée',
        'description_detaillee': '''1. Récupère l'offre depuis Bexio
2. Parse le titre pour extraire rue, localité, type de projet
3. Crée la structure de dossiers sur le serveur
4. Copie les templates Rhino/Grasshopper
5. Télécharge et sauvegarde le PDF dans 1. Admin/11. Offre/
6. Récupère les coordonnées géographiques (geo.admin.ch)
7. Récupère les données RegBL du bâtiment
8. Génère un rapport RegBL dans 5. Rapport/53. Annexes/
9. Crée une page Notion avec les informations du projet''',
        'category': 'Bexio',
        'args': ['numero_offre']
    },
    'facture_payee': {
        'name': 'Facture Payée',
        'file': '202512_Facture_payee.py',
        'description': 'Marquer une facture comme payée et archiver le PDF',
        'description_detaillee': '''1. Récupère la facture depuis Bexio
2. Parse le titre pour extraire rue et localité
3. Trouve le dossier projet correspondant sur le serveur
4. Télécharge et sauvegarde le PDF dans 1. Admin/12. Facture/
5. Marque la facture comme payée dans Bexio
6. Marque la facture comme payée dans Notion (coche la propriété "Payé")''',
        'category': 'Bexio',
        'args': ['numero_facture']
    },
    'creer_devis': {
        'name': 'Créer Devis CECB',
        'file': '202512_Creer_devis.py',
        'description': 'Créer un devis CECB, CECB Plus ou Conseil Incitatif',
        'description_detaillee': '''1. Récupère les données du formulaire
2. Recherche/crée le contact dans Bexio
3. Récupère les données du bâtiment (geo.admin.ch + RegBL)
4. Calcule le prix selon la formule tarifaire
5. Crée l'offre dans Bexio avec les positions
6. Envoie une notification''',
        'category': 'Bexio',
        'args': ['form_data'],
        'has_form': True,
        'form_template': 'form_devis_cecb.html'
    },
}


# ==========================================
# ROUTES D'AUTHENTIFICATION
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False) == 'on'

        if not email or not password:
            flash('Veuillez remplir tous les champs', 'danger')
            return render_template('login.html')

        user = get_user_by_email(email)

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Bienvenue {user.email} !', 'success')

            # Rediriger vers la page demandée ou l'accueil
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email ou mot de passe incorrect', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))


# ==========================================
# FONCTIONS UTILITAIRES POUR PARSING
# ==========================================

def extract_quote_id_from_output(output):
    """
    Extraire l'ID du devis depuis la sortie du script

    Cherche le pattern "ID: 12345" dans la sortie logger
    (voir scripts/202512_Creer_devis.py ligne 243)

    Args:
        output (str): Sortie stdout du script Python

    Returns:
        str|None: L'ID du devis ou None si non trouvé
    """
    match = re.search(r'ID:\s*(\d+)', output)
    return match.group(1) if match else None


def extract_document_nr_from_output(output):
    """
    Extraire le numéro de document depuis la sortie du script

    Cherche le pattern "Numéro: A-0123" dans la sortie logger
    (voir scripts/202512_Creer_devis.py ligne 244)

    Args:
        output (str): Sortie stdout du script Python

    Returns:
        str|None: Le numéro de document ou None si non trouvé
    """
    match = re.search(r'Numéro:\s*([A-Z0-9-]+)', output)
    return match.group(1) if match else None


# ==========================================
# ROUTES PRINCIPALES
# ==========================================

@app.route('/')
@login_required
def index():
    """Page principale avec tous les boutons"""
    return render_template('index.html', scripts=SCRIPTS)


@app.route('/run_script', methods=['POST'])
@login_required
def run_script():
    """Exécute un script et retourne le résultat"""
    data = request.json
    script_id = data.get('script_id')
    args = data.get('args', {})

    if script_id not in SCRIPTS:
        return jsonify({
            'success': False,
            'error': f'Script {script_id} non trouvé'
        }), 404

    script_config = SCRIPTS[script_id]
    script_path = os.path.join('scripts', script_config['file'])

    if not os.path.exists(script_path):
        return jsonify({
            'success': False,
            'error': f'Fichier {script_path} non trouvé'
        }), 404

    # Sauvegarder la soumission AVANT l'exécution pour les devis CECB
    submission = None
    if script_id == 'creer_devis':
        try:
            form_data_json = args.get('form_data', '{}')
            form_data = json.loads(form_data_json) if isinstance(form_data_json, str) else form_data_json

            # Créer la soumission avec les métadonnées

            # Déterminer le nom du client (société ou personne)
            if form_data.get('type_contact') == 'Société':
                client_name = form_data.get('nom_entreprise', '') or form_data.get('nom_societe', '')
            else:
                prenom = form_data.get('prenom', '')
                nom_famille = form_data.get('nom_famille', '') or form_data.get('nom', '')
                client_name = f"{prenom} {nom_famille}".strip()

            # Déterminer l'adresse du bâtiment
            building_address = (
                form_data.get('adresse_batiment') or
                form_data.get('rue_batiment') or
                ''
            )

            submission = FormSubmission(
                user_id=current_user.id,
                form_type='devis_cecb',
                form_data=form_data,
                certificate_type=form_data.get('type_certificat', ''),
                client_name=client_name,
                building_address=building_address,
                status='submitted'
            )
            db.session.add(submission)
            db.session.commit()
        except Exception as e:
            # En cas d'erreur de sauvegarde, logger mais continuer l'exécution
            print(f"⚠️  Erreur lors de la sauvegarde de la soumission: {str(e)}")

    try:
        # Prépare la commande et l'entrée stdin
        cmd = ['python', script_path]
        stdin_data = None

        if 'args' in script_config:
            for arg_name in script_config['args']:
                if arg_name in args:
                    if arg_name == 'form_data':
                        # Passer les données JSON via stdin (évite les problèmes d'encodage Windows cp1252)
                        stdin_data = args[arg_name]
                    else:
                        cmd.append(args[arg_name])

        # Environnement avec PYTHONUTF8=1 pour forcer UTF-8 dans le subprocess
        env = copy.copy(os.environ)
        env['PYTHONUTF8'] = '1'

        # Exécute le script avec encodage UTF-8
        start_time = datetime.now()
        result = subprocess.run(
            cmd,
            input=stdin_data,
            capture_output=True,
            text=True,
            encoding='utf-8',  # Force UTF-8 pour gérer les caractères spéciaux
            errors='replace',  # Remplace les caractères non décodables
            env=env,
            timeout=300  # Timeout de 5 minutes
        )
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Mettre à jour la soumission avec le résultat
        if submission:
            try:
                if result.returncode == 0:
                    # Succès : extraire l'ID et le numéro de document
                    quote_id = extract_quote_id_from_output(result.stdout)
                    document_nr = extract_document_nr_from_output(result.stdout)

                    submission.status = 'quote_created'
                    submission.bexio_quote_id = quote_id
                    submission.bexio_document_nr = document_nr
                else:
                    # Échec : sauvegarder l'erreur
                    submission.status = 'error'
                    submission.error_message = result.stderr[:500] if result.stderr else 'Erreur inconnue'

                db.session.commit()
            except Exception as e:
                print(f"⚠️  Erreur lors de la mise à jour de la soumission: {str(e)}")
                db.session.rollback()

        return jsonify({
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'duration': f'{duration:.2f}s',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

    except subprocess.TimeoutExpired:
        # Timeout : mettre à jour la soumission
        if submission:
            try:
                submission.status = 'error'
                submission.error_message = 'Timeout: le script a dépassé le temps d\'exécution maximal (5 min)'
                db.session.commit()
            except Exception:
                db.session.rollback()

        return jsonify({
            'success': False,
            'error': 'Le script a dépassé le temps d\'exécution maximal (5 min)'
        }), 408

    except Exception as e:
        # Erreur générale : mettre à jour la soumission
        if submission:
            try:
                submission.status = 'error'
                submission.error_message = str(e)[:500]
                db.session.commit()
            except Exception:
                db.session.rollback()

        return jsonify({
            'success': False,
            'error': f'Erreur lors de l\'exécution : {str(e)}'
        }), 500


@app.route('/list_scripts')
@login_required
def list_scripts():
    """Liste tous les scripts disponibles (pour debugging)"""
    return jsonify(SCRIPTS)


@app.route('/devis/nouveau')
@app.route('/devis/nouveau/<int:submission_id>')
@login_required
def nouveau_devis(submission_id=None):
    """Affiche le formulaire de création de devis CECB

    Args:
        submission_id (int, optional): ID d'une soumission à rappeler pour pré-remplissage
    """
    submission_data = None

    # Si un submission_id est fourni, charger les données
    if submission_id:
        submission = FormSubmission.query.filter_by(
            id=submission_id,
            user_id=current_user.id
        ).first()

        if submission:
            submission_data = submission.to_dict()
        else:
            flash('Soumission non trouvée ou accès refusé', 'warning')

    return render_template(
        'form_devis_cecb.html',
        google_api_key=GOOGLE_API_KEY,
        submission_data=submission_data
    )


# ==========================================
# ROUTES API SOUMISSIONS (Phase 2)
# ==========================================

@app.route('/api/submissions', methods=['GET'])
@login_required
def list_submissions():
    """Liste les soumissions de l'utilisateur connecté"""
    try:
        # Récupérer toutes les soumissions de l'utilisateur, triées par date (plus récentes en premier)
        submissions = FormSubmission.query.filter_by(
            user_id=current_user.id
        ).order_by(
            FormSubmission.created_at.desc()
        ).all()

        # Convertir en dictionnaires
        submissions_data = [sub.to_dict() for sub in submissions]

        return jsonify({
            'success': True,
            'submissions': submissions_data,
            'count': len(submissions_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la récupération des soumissions: {str(e)}'
        }), 500


@app.route('/api/submissions/<int:submission_id>', methods=['GET'])
@login_required
def get_submission(submission_id):
    """Récupère une soumission spécifique"""
    try:
        submission = FormSubmission.query.filter_by(
            id=submission_id,
            user_id=current_user.id
        ).first()

        if not submission:
            return jsonify({
                'success': False,
                'error': 'Soumission non trouvée ou accès refusé'
            }), 404

        return jsonify({
            'success': True,
            'submission': submission.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la récupération: {str(e)}'
        }), 500


@app.route('/api/submissions/<int:submission_id>', methods=['DELETE'])
@login_required
def delete_submission(submission_id):
    """Supprime une soumission"""
    try:
        submission = FormSubmission.query.filter_by(
            id=submission_id,
            user_id=current_user.id
        ).first()

        if not submission:
            return jsonify({
                'success': False,
                'error': 'Soumission non trouvée ou accès refusé'
            }), 404

        db.session.delete(submission)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Soumission supprimée avec succès'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Erreur lors de la suppression: {str(e)}'
        }), 500


@app.route('/submissions')
@login_required
def submissions_page():
    """Page HTML listant les soumissions de l'utilisateur"""
    return render_template('submissions.html')


@app.route('/tests')
@login_required
@admin_required
def tests():
    """Affiche la page de liens de test avec formulaires pré-remplis"""
    return render_template('test_links.html')


@app.route('/admin/tarifs', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_tarifs():
    """Page d'administration des tarifs"""
    if request.method == 'POST':
        # Sauvegarder les nouveaux tarifs
        try:
            tarifs = request.json
            if save_tarifs(tarifs):
                return jsonify({
                    'success': True,
                    'message': 'Tarifs sauvegardés avec succès'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Erreur lors de la sauvegarde'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erreur: {str(e)}'
            }), 500

    # GET: Afficher le formulaire
    tarifs = load_tarifs()
    return render_template('admin_tarifs.html', tarifs=tarifs)


@app.route('/admin/textes', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_textes():
    """Page d'administration des textes"""
    if request.method == 'POST':
        # Sauvegarder les nouveaux textes
        try:
            textes = request.json
            if save_textes(textes):
                return jsonify({
                    'success': True,
                    'message': 'Textes sauvegardés avec succès'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Erreur lors de la sauvegarde'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erreur: {str(e)}'
            }), 500

    # GET: Afficher le formulaire
    textes = load_textes()
    return render_template('admin_textes.html', textes=textes)


@app.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def admin_users():
    """Page d'administration des utilisateurs"""
    users = get_all_users()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/create', methods=['POST'])
@login_required
@admin_required
def admin_users_create():
    """Créer un nouvel utilisateur"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')

        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email et mot de passe requis'
            }), 400

        user, error = create_user(email, password, role)

        if user:
            return jsonify({
                'success': True,
                'message': f'Utilisateur {email} créé avec succès',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'created_at': user.created_at
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': error
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500


@app.route('/admin/users/update/<user_id>', methods=['POST'])
@login_required
@admin_required
def admin_users_update(user_id):
    """Mettre à jour un utilisateur"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        success, error = update_user(user_id, email, password, role)

        if success:
            return jsonify({
                'success': True,
                'message': 'Utilisateur mis à jour avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': error
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500


@app.route('/admin/users/delete/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def admin_users_delete(user_id):
    """Supprimer un utilisateur"""
    try:
        # Empêcher la suppression de son propre compte
        if user_id == current_user.id:
            return jsonify({
                'success': False,
                'error': 'Vous ne pouvez pas supprimer votre propre compte'
            }), 400

        success, error = delete_user(user_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Utilisateur supprimé avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': error
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur: {str(e)}'
        }), 500


@app.route('/api/building_data', methods=['POST'])
@login_required
def get_building_data():
    """
    Récupère les données du bâtiment depuis geo.admin.ch
    Utilisé pour pré-remplir le formulaire avec les données du RegBL
    """
    try:
        data = request.json
        adresse = data.get('adresse', '')
        npa = data.get('npa', '')
        localite = data.get('localite', '')

        if not adresse or not npa or not localite:
            return jsonify({
                'success': False,
                'error': 'Adresse, NPA et localité requis'
            }), 400

        # Importer le module geo_admin_client
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
        from geo_admin_client import GeoAdminClient

        # Récupérer les données du bâtiment
        building_data = GeoAdminClient.get_building_data_cached(adresse, npa, localite)

        if building_data:
            return jsonify({
                'success': True,
                'data': {
                    'egid': building_data.get('egid'),
                    'gastw': building_data.get('gastw', 2),  # Nombre d'étages
                    'garea': building_data.get('garea'),      # Surface au sol
                    'gbauj': building_data.get('gbauj'),      # Année construction
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Bâtiment non trouvé dans le RegBL'
            })

    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données du bâtiment: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Erreur serveur: {str(e)}'
        }), 500


@app.route('/api/tarifs', methods=['GET'])
@login_required
def api_tarifs():
    """Retourne les tarifs actuels en JSON (utilisé par le panneau tarifs du formulaire)"""
    tarifs = load_tarifs()
    return jsonify(tarifs)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Script Runner - Application démarrée")
    print("="*60)
    print(f"📍 URL: http://localhost:5000")
    print(f"📂 Scripts disponibles: {len(SCRIPTS)}")
    print("="*60 + "\n")

    # Créer l'utilisateur admin par défaut si nécessaire
    create_default_admin()

    app.run(debug=True, host='localhost', port=5000)
