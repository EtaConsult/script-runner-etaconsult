# Changelog - Script Runner Êta Consult

Toutes les modifications notables du projet sont documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### À venir
- Intégration avec OneDrive pour stockage automatique des documents

---

## [1.1.0] - 2025-01-04

### Ajouté
- **Calcul dynamique du facteur CECB Plus** (`scripts/quote_calculator.py`)
  - Facteur basé sur la surface équivalente (S_eq) au lieu d'un facteur fixe
  - Facteur petit bâtiment : 3.69 (S_eq < 160 m²)
  - Facteur moyen bâtiment : 2.29 (160 m² ≤ S_eq < 750 m²)
  - Facteur grand bâtiment : 1.79 (S_eq ≥ 750 m²)
- **Interface d'administration des facteurs CECB Plus** (`templates/admin_tarifs.html`)
  - 6 nouveaux champs configurables (3 facteurs + 2 seuils + prix max)
  - Mise à jour dynamique via `/admin/tarifs`
- **Prestations non-incluses pour CECB Plus** (`scripts/quote_position.py`, `scripts/legal_texts.py`)
  - Ajout section "Conseil Incitatif Chauffez Renouvelable®" dans les devis CECB Plus
  - Champ éditable via `/admin/textes`
- **Méthode get_eta_consult_coords()** dans `scripts/config_manager.py`
  - Récupération des coordonnées GPS d'Êta Consult pour calculs de distance
- **Documentation des commandes Git** (`CLAUDE_CODE_COMMANDS.md`)
  - Guide de référence pour le développement avec Claude Code

### Modifié
- **`config.py.example`** : Version simplifiée avec structure claire
  - Ajout des constantes entreprise (adresse, coordonnées GPS)
  - Ajout CONTACT_TYPES et SALUTATIONS
  - Note explicative sur tarifs.json et textes.json
- **`app.py`** : Tarifs par défaut mis à jour avec nouveaux facteurs CECB Plus
- **`scripts/config_manager.py`** : Ajout désactivation proxy PythonAnywhere
- **`.gitignore`** : Ajout exclusion de `tarifs.json` et `textes.json`
- **`tarifs.json`** et **`textes.json`** : Retirés du versioning Git (fichiers métier sensibles)

### Corrigé
- Calcul prix CECB Plus : remplace le facteur fixe 1.5 par un calcul progressif
- Uniformisation des valeurs par défaut dans tous les fichiers de configuration

### Technique
- Les facteurs CECB Plus sont maintenant stockés dans `tarifs.json` (non versionné)
- Fallback sur valeurs par défaut si `tarifs.json` absent
- Logs améliorés affichant le facteur CECB Plus utilisé et la surface équivalente

---

## [1.0.0] - 2025-01-04

### Ajouté
- Déploiement initial sur PythonAnywhere (etaconsult.pythonanywhere.com)
- Système d'authentification avec gestion des utilisateurs (admin/user)
- Interface web pour création de devis CECB/CECB Plus
- Intégration API Bexio pour création automatique de contacts et devis
- Intégration geo.admin.ch pour données bâtiments suisses
- Calcul automatique des prix selon distance et surface
- Fix proxy PythonAnywhere dans `config_manager.py` pour appels API externes
- Documentation de déploiement (`DEPLOYMENT.md`)
- Guide des commandes Git pour Claude Code (`CLAUDE_CODE_COMMANDS.md`)

### Modifié
- `scripts/config_manager.py` : Ajout bypass proxy avec `NO_PROXY` et `no_proxy`
- `app.py` : Clé secrète Flask mise à jour pour production

### Configuration (fichiers non versionnés)
- `config.py` créé avec :
  - `BEXIO_API_TOKEN` pour API Bexio
  - `BEXIO_IDS` : tax_id=28, currency_id=1, language_id=2, mwst_type=0, user_id=1
  - Google Maps API (optionnel)
  - OneDrive API (optionnel)
- `users.json` créé avec compte admin : info@etaconsult.ch
- `tarifs.json` configuré avec grille tarifaire
- `textes.json` configuré avec templates de devis

### Technique
- Python 3.10
- Flask + Flask-Login pour authentification
- Intégration requests pour appels API
- Déploiement : PythonAnywhere (plan Hacker - 5$/mois)

### Notes de déploiement
- Compte PythonAnywhere upgradé pour accès illimité aux APIs externes
- URL publique : https://etaconsult.pythonanywhere.com
- Repository GitHub : https://github.com/EtaConsult/script-runner-etaconsult

### Sécurité
- Mots de passe hachés avec scrypt
- Clé secrète Flask unique générée
- Fichiers sensibles exclus du versioning (.gitignore)
- HTTPS activé par défaut (certificat Let's Encrypt)

---

## Format du changelog

### Types de changements
- **Ajouté** : nouvelles fonctionnalités
- **Modifié** : changements dans les fonctionnalités existantes
- **Déprécié** : fonctionnalités bientôt supprimées
- **Supprimé** : fonctionnalités supprimées
- **Corrigé** : corrections de bugs
- **Sécurité** : corrections de vulnérabilités

---

**Maintenu par** : Êta Consult Sàrl  
**Contact** : info@etaconsult.ch
