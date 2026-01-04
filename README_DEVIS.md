# Guide d'installation - Système de Devis CECB

Ce guide explique comment installer et configurer le nouveau système de création automatique de devis CECB dans Bexio.

## Nouveautés ajoutées

### 1. Script de création de devis (`scripts/202512_Creer_devis.py`)
- Création automatique de devis CECB, CECB Plus et Conseil Incitatif
- Gestion intelligente des contacts (Privé vs Entreprise avec personne associée)
- Récupération automatique des données du bâtiment via geo.admin.ch
- Calcul automatique des prix selon formule tarifaire personnalisable
- Création de l'offre dans Bexio avec positions détaillées

### 2. Formulaire web (`templates/form_devis_cecb.html`)
- Interface moderne et responsive avec panneau de logs en temps réel
- **Autocomplétion d'adresse avec Google Places API** (évite les erreurs de saisie)
- Validation des champs en temps réel
- Copie automatique adresse facturation → bâtiment
- Affichage conditionnel selon le type de contact
- Logs d'exécution affichés en direct (comme le script runner principal)

### 3. Interface d'administration des tarifs (`templates/admin_tarifs.html`)
- Modification facile de tous les paramètres tarifaires
- Sauvegarde dans `tarifs.json`
- Réinitialisation aux valeurs par défaut

### 4. Nouvelles routes Flask
- `/devis/nouveau` - Formulaire de création de devis
- `/admin/tarifs` - Administration des tarifs

## Installation

### Étape 1 : Installer les dépendances

```bash
pip install requests
```

Les dépendances nécessaires sont :
- Flask (déjà installé)
- requests (pour les appels API Bexio et geo.admin.ch)

### Étape 2 : Configurer les credentials API

1. **Copier le fichier de configuration exemple :**
   ```bash
   copy config.py.example config.py
   ```

2. **Éditer `config.py` et remplir vos credentials :**
   ```python
   BEXIO_API_TOKEN = "votre_token_bexio_ici"
   GOOGLE_MAPS_API_KEY = "votre_cle_google_ici"  # Pour l'autocomplétion d'adresse
   ```

   **Pour obtenir votre token Bexio :**
   - Connectez-vous sur https://office.bexio.com
   - Allez dans Settings → Integrations → API
   - Créez un nouveau token avec les droits :
     - `contact_show` (lecture contacts)
     - `contact_edit` (création/modification contacts)
     - `kb_offer_show` (lecture offres)
     - `kb_offer_edit` (création offres)

   **Pour obtenir votre clé Google Maps API :**
   - Consultez le guide détaillé : `GOOGLE_API_KEY.md`
   - En résumé :
     1. Créer un projet sur [Google Cloud Console](https://console.cloud.google.com/)
     2. Activer "Places API" et "Maps JavaScript API"
     3. Créer une clé API
     4. **40 000 requêtes/mois gratuites** (largement suffisant pour un usage normal)
   - **Note :** Si vous laissez ce champ vide, l'autocomplétion sera désactivée mais le formulaire fonctionnera quand même

3. **IMPORTANT : Ne jamais commiter `config.py` dans Git !**
   Le fichier `.gitignore` est déjà configuré pour l'exclure.

### Étape 3 : Vérifier les tarifs par défaut

Le fichier `tarifs.json` contient les tarifs par défaut :
- Prix de base CECB : 500 CHF
- Facteurs kilométriques et de surface
- Prix CECB Plus, forfaits délai, etc.

Vous pouvez les modifier via l'interface web `/admin/tarifs` après le démarrage.

### Étape 4 : Démarrer l'application

```bash
python app.py
```

Ouvrir dans le navigateur : **http://localhost:5000**

## Utilisation

### Créer un nouveau devis

1. **Via l'interface principale :**
   - Cliquer sur le bouton "Créer Devis CECB"
   - Remplir le formulaire
   - Cliquer sur "Créer le devis"

2. **URL directe :**
   - Ouvrir http://localhost:5000/devis/nouveau

### Modifier les tarifs

1. **Accéder à l'interface d'administration :**
   - http://localhost:5000/admin/tarifs

2. **Modifier les valeurs :**
   - Prix de base
   - Facteurs kilométriques (proche/loin + seuil)
   - Facteurs de surface (petit/grand + seuil)
   - CECB Plus (multiplicateur + prix max)
   - Frais fixes (émission CECB, conseil incitatif)
   - Forfaits délai (normal/express/urgent)

3. **Sauvegarder :**
   - Cliquer sur "Sauvegarder"
   - Les nouveaux tarifs seront utilisés pour tous les devis futurs

4. **Réinitialiser :**
   - Cliquer sur "Réinitialiser" pour revenir aux valeurs par défaut

## Fonctionnement

### Gestion des contacts Bexio

#### Contact Privé
Le script recherche d'abord le contact par email. S'il n'existe pas, il le crée :
```
Contact Privé
├─ Nom : {nom_famille}
├─ Prénom : {prenom}
├─ Email : {email}
└─ Adresse : {adresse_facturation}
```

#### Contact Entreprise
Le script crée ou récupère :
1. L'entreprise (contact_type_id = 2)
2. La personne de contact (contact_type_id = 1)
3. L'association entre les deux (contact_relation)

```
Entreprise
├─ Nom : {nom_entreprise}
└─ Adresse : {adresse_facturation}

Personne associée
├─ Nom : {nom_famille}
├─ Prénom : {prenom}
└─ Email : {email}

→ Les deux sont liés dans Bexio
```

### Calcul des prix

#### Formule CECB

```python
# Étages équivalents
Et_eq = Et_sous_sol + Et_combles + gastw (niveaux hors-sol)

# Surface équivalente
S_eq = Et_eq × garea (surface au sol)

# Facteurs selon seuils
S_factor = 0.6 si S_eq < 750 m², sinon 0.5
km_factor = 0.9 si distance < 25 km, sinon 0.7

# Prix
CECB_Unit_Price = 500 + (distance × km_factor) + (S_eq × S_factor)
```

#### CECB Plus

```python
CECB_Plus_Unit_Price = min(1989, CECB_Unit_Price × 1.4)
```

#### Conseil Incitatif
Gratuit (0 CHF)

### Récupération des données du bâtiment

Le script interroge l'API geo.admin.ch :
```
GET https://api3.geo.admin.ch/rest/services/api/SearchServer
    ?searchText={adresse}, {npa} {localite}
    &lang=fr
    &type=locations

Récupère :
- EGID (identifiant du bâtiment)
- garea (surface au sol en m²)
- gastw (nombre de niveaux hors-sol)
- gbauj (année de construction)
- gebnr (numéro de bâtiment)
- lparz (numéro de parcelle)
- coords (lat, lon)
```

### Structure de l'offre Bexio

L'offre créée contient :
- **Titre** : `{type_certificat} - {adresse_batiment}, {npa}, {localite}`
- **Contact** : ID du contact (+ personne associée si entreprise)
- **Positions** :
  - Position CECB avec détails du bâtiment
  - Frais d'émission CECB (80 CHF)
  - Forfait exécution (selon délai choisi)
  - Position CECB Plus (si applicable)
  - Textes informatifs (prestations incluses/non-incluses)

## Tests

### Scénarios de test recommandés

#### Test 1 : Contact privé nouveau
```json
{
  "type_contact": "Privé",
  "appellation": "Mme",
  "nom_famille": "Test",
  "prenom": "Alice",
  "email": "alice.test@example.com",
  "rue_facturation": "Rue de Test 1",
  "npa_facturation": "1180",
  "localite_facturation": "Rolle",
  "type_certificat": "CECB"
}
```

#### Test 2 : Contact entreprise nouveau
```json
{
  "type_contact": "Société",
  "nom_entreprise": "Test Immo SA",
  "appellation": "M.",
  "nom_famille": "Dupont",
  "prenom": "Jean",
  "email": "j.dupont@testimmo.ch",
  "rue_facturation": "Avenue de Test 10",
  "npa_facturation": "1003",
  "localite_facturation": "Lausanne",
  "type_certificat": "CECB Plus"
}
```

#### Test 3 : Conseil Incitatif
```json
{
  "type_contact": "Privé",
  "type_certificat": "Conseil Incitatif",
  ...
}
```

### Vérifications après chaque test

1. **Dans Bexio :**
   - Le contact a bien été créé/trouvé
   - L'offre est créée avec le bon numéro
   - Les positions sont correctes
   - Le total HT correspond au calcul
   - Si entreprise : la personne est bien associée

2. **Dans les logs du script :**
   - Aucune erreur
   - Les données du bâtiment ont été trouvées
   - Les calculs de prix sont corrects
   - La distance depuis Rolle est calculée

## Dépannage

### Erreur "config.py non trouvé"
→ Copier `config.py.example` vers `config.py` et remplir les credentials

### Erreur API Bexio
→ Vérifier que le token Bexio est valide et a les bons droits

### Bâtiment non trouvé sur geo.admin.ch
→ Le script utilise des valeurs par défaut (EGID = N/A, surface = 100 m², etc.)
→ Vous pouvez continuer, mais vérifiez les données dans l'offre créée

### Contact en double dans Bexio
→ Le script recherche par email, si l'email diffère, un nouveau contact sera créé
→ Vérifiez l'email du contact existant dans Bexio

### Tarifs incorrects
→ Modifier les tarifs via `/admin/tarifs`
→ Ou éditer directement `tarifs.json`

## Structure des fichiers

```
script-runner/
├── app.py                          # Application Flask (modifiée)
├── config.py.example               # Template de configuration
├── config.py                       # Configuration (à créer, non commité)
├── tarifs.json                     # Tarifs modifiables
├── .gitignore                      # Exclusions Git
├── README.md                       # Documentation principale
├── README_DEVIS.md                 # Ce fichier
├── requirements.txt                # Dépendances Python
├── scripts/
│   ├── 202512_Offres_acceptees.py
│   ├── 202512_Facture_payee.py
│   └── 202512_Creer_devis.py      # Nouveau script
├── templates/
│   ├── index.html
│   ├── form_devis_cecb.html       # Nouveau formulaire
│   └── admin_tarifs.html          # Nouvelle interface admin
└── static/
    └── style.css
```

## Personnalisation

### Modifier les textes des offres

Éditer `config.py` :
```python
TEXTES = {
    "footer_acompte": "Vos conditions de paiement personnalisées",
    "prestations_incluses_cecb": "Vos prestations...",
    ...
}
```

### Modifier les IDs Bexio

Si vos IDs diffèrent (unités, taxes, etc.), modifier dans `config.py` :
```python
BEXIO_IDS = {
    "unit_id": 3,      # 3 = "ens"
    "tax_id": 28,      # 28 = TVA 8.1%
    ...
}
```

## Support

Pour toute question ou bug :
- Consulter les logs dans le terminal où tourne `app.py`
- Vérifier les erreurs retournées par le formulaire web
- Tester le script manuellement : `python scripts/202512_Creer_devis.py '{...json...}'`

---

**Fait avec ❤️ pour Êta Consult Sàrl**
