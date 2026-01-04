# 🚀 Refactorisation du script 202512_Creer_devis.py

**Date:** 2026-01-03
**Version:** 2.0
**Auteur:** Assistant Claude

---

## 📋 Résumé des améliorations

Le script `202512_Creer_devis.py` a été **complètement refactorisé** pour améliorer sa maintenabilité, sa robustesse et sa structure. Le code est passé de **786 lignes monolithiques à 334 lignes** grâce à une architecture modulaire.

---

## 🎯 Objectifs atteints

### 1. ✅ Textes légaux complets dans les devis

- **Clause de responsabilité CECB** ajoutée après les prestations incluses
- **Conditions de paiement avec acompte paramétrable** (via `pct_acompte` dans `tarifs.json`)
- **Message personnalisé** intégré proprement dans le devis (champ `message_personnalise`)

### 2. ✅ Architecture modulaire

Le code a été divisé en **9 modules spécialisés** :

#### **scripts/legal_texts.py**
- Tous les textes légaux et templates
- Fonction `get_conditions_paiement(pct_acompte)` pour texte paramétrable
- Fonction `format_custom_message(message)` pour messages personnalisés
- Fonction `get_complete_footer(pct_acompte)` pour footer complet

#### **scripts/validators.py**
- Validation robuste des données de formulaire
- Classe `ValidationError` personnalisée
- Fonctions de validation : `validate_building_data`, `validate_contact_data`, `validate_form_data`
- Fonctions de nettoyage : `sanitize_form_data`, `sanitize_string`

#### **scripts/config_manager.py**
- Classe `ConfigManager` pour gérer la configuration
- Chargement intelligent depuis `tarifs.json` et `textes.json`
- Fallback vers `config.py` si fichiers JSON absents
- Méthodes d'accès : `get_tarif()`, `get_texte()`, `get_bexio_api_token()`, etc.
- Validation de configuration avec `validate_config()`

#### **scripts/quote_calculator.py**
- Classe `QuoteCalculator` pour tous les calculs de prix
- Méthodes :
  - `calculate_cecb_price(distance_km, surface_eq, is_plus)` - Prix CECB/CECB Plus
  - `calculate_deadline_surcharge(deadline_type)` - Supplément délai
  - `calculate_equivalent_floors(gastw, sous_sol, combles)` - Étages équivalents
  - `calculate_equivalent_surface(et_eq, garea)` - Surface équivalente
  - `calculate_quote_pricing(building_data, form_data)` - Calcul complet
- Intégration Google Maps Distance Matrix API avec gestion d'erreurs

#### **scripts/bexio_client.py**
- Classe `BexioClient` avec gestion d'erreurs robuste
- Décorateur `@safe_api_call` pour gérer les exceptions HTTP
- Méthodes CRUD : `get()`, `post()`, `put()`, `delete()`
- Méthodes spécifiques : `create_contact()`, `create_quote()`, `create_contact_relation()`
- Logging détaillé de toutes les requêtes

#### **scripts/quote_position.py**
- Classe `QuotePosition` pour représenter une position de devis
- Classe `QuotePositionBuilder` pour créer les positions facilement
- Méthodes de construction :
  - `build_cecb_positions()` - Positions pour CECB
  - `build_cecb_plus_positions()` - Positions pour CECB Plus
  - `build_conseil_incitatif_positions()` - Positions pour Conseil Incitatif
- Conversion automatique au format Bexio avec `to_bexio_format()`

#### **scripts/geo_admin_client.py**
- Classe `GeoAdminClient` pour l'API geo.admin.ch
- **Système de cache LRU** avec `@lru_cache(maxsize=100)`
- Méthode `get_building_data_cached()` pour optimiser les performances
- Méthode `get_default_building_data()` pour données par défaut
- Gestion robuste des erreurs API

#### **scripts/contact_manager.py**
- Classe `ContactManager` pour gérer les contacts Bexio
- Support contacts Privé et Société avec personne associée
- Méthodes :
  - `get_or_create_contact(form_data)` - Point d'entrée principal
  - `_handle_private_contact()` - Gestion contact privé
  - `_handle_company_contact()` - Gestion entreprise + personne
  - `_ensure_contact_relation()` - Association entreprise-personne
- Recherche intelligente par email et nom

#### **scripts/202512_Creer_devis.py** (refactorisé)
- **334 lignes** au lieu de 786 (réduction de 58%)
- Architecture claire avec fonctions séparées :
  - `create_quote()` - Fonction principale
  - `create_bexio_quote()` - Création offre Bexio
  - `print_summary()` - Affichage résumé
- Validation des données en amont
- Gestion d'erreurs avec `ValidationError`
- Logging structuré

### 3. ✅ Configuration centralisée

- Fichier **tarifs.json** avec nouveau champ `pct_acompte` (paramétrable)
- Fichier **templates.json** avec tous les templates de textes
- Gestionnaire `ConfigManager` pour accès unifié

### 4. ✅ Système de cache

- Cache LRU pour les recherches de bâtiments geo.admin.ch
- Taille : 100 entrées max
- Méthode `clear_cache()` pour vider le cache
- Méthode `get_cache_info()` pour statistiques

### 5. ✅ Tests unitaires

- Fichier **tests/test_quote_calculator.py**
- **9 tests** couvrant :
  - Calcul prix CECB standard
  - Calcul prix CECB bâtiment loin/grand
  - Calcul prix CECB Plus
  - Test plafond CECB Plus (1989 CHF max)
  - Calcul étages équivalents
  - Calcul surface équivalente
  - Forfaits exécution (Normal, Express, Urgent)
- **Résultat:** 9/9 tests réussis ✅

### 6. ✅ Gestion d'erreurs robuste

- Exception personnalisée `ValidationError`
- Décorateur `@safe_api_call` pour les appels API
- Try/except à tous les niveaux critiques
- Messages d'erreur clairs et détaillés

### 7. ✅ Encodage UTF-8 complet

- Configuration UTF-8 forcée pour Windows dans tous les scripts
- Gestion des caractères spéciaux (é, è, à, ç, etc.)
- Support des emojis dans les logs

### 8. ✅ Logging amélioré

- Module `logging` standard Python
- Niveaux : INFO, WARNING, ERROR
- Format : `%(levelname)s - %(message)s`
- Logging dans tous les modules pour traçabilité

### 9. ✅ Interface utilisateur renommée

- **Page index.html** : "Script Runner" → "**Tableau de bord Êta Consult Sàrl**"
- Sous-titre : "Gestion des devis CECB et automatisation"

---

## 📂 Structure des fichiers

```
202512_Script_runner/
├── app.py                          # Serveur Flask
├── config.py                       # Configuration principale
├── tarifs.json                     # Tarifs (avec pct_acompte)
├── textes.json                     # Textes modifiables
├── templates.json                  # Templates de textes (NOUVEAU)
├── requirements.txt                # Dépendances
├── REFACTORING.md                  # Ce fichier
│
├── scripts/                        # Scripts Python
│   ├── 202512_Creer_devis.py      # Script principal (REFACTORISÉ)
│   ├── 202512_Offres_acceptees.py # Script offres
│   ├── 202512_Facture_payee.py    # Script factures
│   │
│   ├── bexio_client.py            # Client API Bexio (NOUVEAU)
│   ├── geo_admin_client.py        # Client API geo.admin (NOUVEAU)
│   ├── contact_manager.py         # Gestion contacts (NOUVEAU)
│   ├── quote_calculator.py        # Calcul prix (NOUVEAU)
│   ├── quote_position.py          # Positions devis (NOUVEAU)
│   ├── config_manager.py          # Gestion config (NOUVEAU)
│   ├── validators.py              # Validation (NOUVEAU)
│   └── legal_texts.py             # Textes légaux (NOUVEAU)
│
├── tests/                          # Tests unitaires (NOUVEAU)
│   └── test_quote_calculator.py   # Tests calculateur
│
├── templates/                      # Templates HTML
│   ├── index.html                 # Page principale (RENOMMÉE)
│   ├── form_devis_cecb.html       # Formulaire devis
│   ├── admin_tarifs.html          # Admin tarifs
│   └── admin_textes.html          # Admin textes
│
└── static/                         # Fichiers statiques
    └── style.css                   # Styles CSS
```

---

## 🔧 Utilisation

### Lancer l'application

```bash
cd "C:\Users\info\OneDrive\Documents_Eta Consult\18. Scripts\202512_Script_runner"
python app.py
```

Ouvrir dans le navigateur : **http://localhost:5000**

### Lancer les tests unitaires

```bash
python tests/test_quote_calculator.py
```

Résultat attendu :
```
============================================================
🧪 TESTS UNITAIRES - QuoteCalculator
============================================================
✅ 9 tests réussis, 0 tests échoués
```

### Créer un devis manuellement

```bash
cd scripts
python 202512_Creer_devis.py '{"type_contact": "Privé", "type_certificat": "CECB", ...}'
```

---

## 📈 Métriques de la refactorisation

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| **Lignes de code principal** | 786 | 334 | -58% |
| **Fichiers Python** | 1 | 9 | Modularité +800% |
| **Tests unitaires** | 0 | 9 | ✅ Couverture |
| **Gestion d'erreurs** | Basique | Robuste | ✅ ValidationError |
| **Cache** | Aucun | LRU (100) | ✅ Performance |
| **Logging** | Print | Module logging | ✅ Traçabilité |
| **Validation** | Partielle | Complète | ✅ Sécurité |

---

## 🎨 Nouveautés principales

### 1. Textes légaux automatiques dans les devis

Chaque devis contient maintenant :

1. **Position principale** (CECB, CECB Plus ou Conseil)
2. **Frais d'émission** (80 CHF)
3. **Forfait exécution** (si applicable)
4. **Prestations incluses** (texte détaillé)
5. **⭐ Clause de responsabilité CECB** (NOUVEAU)
6. **Prestations non-incluses** (si CECB simple)
7. **⭐ Message personnalisé** (si fourni) (NOUVEAU)
8. **⭐ Footer avec conditions de paiement** (acompte paramétrable) (NOUVEAU)

### 2. Pourcentage d'acompte paramétrable

Dans `tarifs.json` :
```json
{
  "pct_acompte": 30
}
```

Le footer généré :
```
Conditions de paiement : Acompte de 30% à la commande, solde à réception du rapport.

Source : Script Runner - Êta Consult Sàrl
```

### 3. Message personnalisé

Dans le formulaire de devis, ajoutez un champ `message_personnalise` :

```json
{
  "message_personnalise": "Merci de nous faire confiance pour ce projet important."
}
```

Le script intègre automatiquement :
```html
<strong>Message :</strong><br>Merci de nous faire confiance pour ce projet important.
```

---

## 🧪 Tests et validation

### Tous les tests passent

```bash
$ python tests/test_quote_calculator.py
============================================================
🧪 TESTS UNITAIRES - QuoteCalculator
============================================================
✅ Test 1: Calcul prix CECB standard - 814 CHF
✅ Test 2: Calcul prix CECB bâtiment loin et grand - 1035 CHF
✅ Test 3: Calcul prix CECB Plus - 1140 CHF
✅ Test 4: Test plafond CECB Plus (max 1989 CHF)
✅ Test 5: Calcul étages équivalents - 4.5
✅ Test 6: Calcul surface équivalente - 600 m²
✅ Test 7: Forfait exécution normal - 0 CHF
✅ Test 8: Forfait exécution express - 135 CHF
✅ Test 9: Forfait exécution urgent - 270 CHF
============================================================
📊 RÉSULTATS: 9 tests réussis, 0 tests échoués
============================================================
```

### Syntaxe Python validée

Tous les modules Python ont été validés avec `python -m py_compile` ✅

---

## 🚀 Prochaines étapes possibles

1. **Ajouter plus de tests unitaires** pour `validators.py`, `contact_manager.py`
2. **Créer un fichier de documentation API** pour chaque classe
3. **Ajouter des tests d'intégration** avec des données factices Bexio
4. **Implémenter un système de logs persistants** (fichier .log)
5. **Créer une interface d'administration** pour gérer `legal_texts.py`
6. **Ajouter support i18n** pour multilingue (FR/DE/IT)

---

## 📞 Support

Pour toute question sur la refactorisation :
- Consulter ce fichier `REFACTORING.md`
- Lire les docstrings de chaque fonction (format Google/NumPy)
- Consulter les tests dans `tests/test_quote_calculator.py`

---

**Fait avec ❤️ pour Êta Consult Sàrl**
