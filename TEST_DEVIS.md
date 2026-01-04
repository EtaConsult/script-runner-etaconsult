# Guide de Test et Débogage - Création de Devis CECB

## Étapes de vérification

### 1. Vérifier que config.py existe et contient le token

```bash
# Vérifier que le fichier existe
dir config.py

# Si non, créer depuis l'exemple
copy config.py.example config.py
```

Éditer `config.py` et vérifier :
```python
BEXIO_API_TOKEN = "votre_vrai_token_ici"  # Pas "votre_token_bexio_ici"
```

### 2. Tester le script en ligne de commande

Avant de tester via l'interface web, testons le script directement :

```bash
cd scripts
python 202512_Creer_devis.py
```

**Résultat attendu :**
```
❌ ERREUR : Données du formulaire manquantes
Usage: python 202512_Creer_devis.py '{...json...}'
```

C'est normal ! Cela confirme que le script est bien trouvé et qu'il attend des arguments.

### 3. Test avec données minimales

Créer un fichier `test_data.json` avec :

```json
{
  "type_contact": "Privé",
  "appellation": "M.",
  "nom_famille": "Test",
  "prenom": "Debug",
  "email": "debug.test@example.com",
  "telephone": "+41 79 000 00 00",
  "rue_facturation": "Rue Test 1",
  "npa_facturation": "1180",
  "localite_facturation": "Rolle",
  "pays_facturation": "Suisse",
  "rue_batiment": "Rue Test 1",
  "npa_batiment": "1180",
  "localite_batiment": "Rolle",
  "type_certificat": "CECB",
  "sous_sol": "Non chauffé ou inexistant",
  "combles": "Non chauffé ou inexistant",
  "delai": "Normal",
  "contexte": "Vente",
  "message": ""
}
```

Puis tester :
```bash
python scripts\202512_Creer_devis.py "{\"type_contact\":\"Privé\",\"nom_famille\":\"Test\",\"prenom\":\"Debug\",\"email\":\"debug@test.com\",\"rue_facturation\":\"Rue Test 1\",\"npa_facturation\":\"1180\",\"localite_facturation\":\"Rolle\",\"rue_batiment\":\"Rue Test 1\",\"npa_batiment\":\"1180\",\"localite_batiment\":\"Rolle\",\"type_certificat\":\"CECB\",\"appellation\":\"M.\",\"sous_sol\":\"Non chauffé ou inexistant\",\"combles\":\"Non chauffé ou inexistant\",\"delai\":\"Normal\",\"contexte\":\"Vente\"}"
```

**Résultats possibles :**

#### ✅ Cas 1 : Succès
```
============================================================
🚀 Création de devis CECB/CECB Plus/Conseil Incitatif
============================================================
📋 Type de certificat: CECB
👤 Contact: Debug Test
🏠 Bâtiment: Rue Test 1, 1180 Rolle
...
✅ SUCCÈS !
```

#### ❌ Cas 2 : Erreur config.py
```
❌ ERREUR : Fichier config.py non trouvé !
📋 Copiez config.py.example vers config.py et remplissez vos credentials
```
→ **Solution :** Copier et remplir config.py

#### ❌ Cas 3 : Erreur token Bexio
```
❌ Erreur GET /2.0/contact/search: 401 Unauthorized
```
→ **Solution :** Vérifier le token dans config.py

#### ❌ Cas 4 : Module requests manquant
```
ModuleNotFoundError: No module named 'requests'
```
→ **Solution :** `pip install requests`

### 4. Tester via l'interface web

1. **Démarrer le serveur :**
   ```bash
   python app.py
   ```

2. **Ouvrir la console développeur du navigateur :**
   - Chrome/Edge : F12 → onglet Console
   - Firefox : F12 → onglet Console

3. **Ouvrir le formulaire :**
   - http://localhost:5000/devis/nouveau

4. **Vérifier les logs dans la console :**
   ```
   ✅ Formulaire de création de devis chargé
   🌐 URL actuelle: http://localhost:5000/devis/nouveau
   ```

5. **Remplir le formulaire avec des données de test :**
   - Type : Privé
   - Nom : Test
   - Prénom : Debug
   - Email : debug@test.com
   - Adresse : Rue Test 1, 1180 Rolle
   - ☑️ Cocher "Identique à l'adresse de facturation"
   - Type certificat : CECB

6. **Cliquer sur "Créer le devis"**

7. **Observer dans la console du navigateur :**
   ```
   📤 Données envoyées au serveur: {type_contact: "Privé", ...}
   📥 Réponse du serveur: {success: true, stdout: "...", ...}
   ```

8. **Observer l'affichage de la page :**
   - ✅ En cas de succès : Section "Devis créé avec succès" avec logs
   - ❌ En cas d'erreur : Sections détaillées avec stdout, stderr, code de retour

## Erreurs courantes et solutions

### Erreur : "Rien ne se passe" quand je clique sur Créer

**Symptômes :**
- Le bouton ne réagit pas
- Pas de message d'erreur

**Solutions :**
1. Ouvrir F12 → Console et chercher des erreurs JavaScript
2. Vérifier que le serveur Flask tourne (voir le terminal)
3. Rafraîchir la page (Ctrl+F5)

### Erreur : "Failed to fetch" ou "NetworkError"

**Symptômes :**
```
❌ Erreur de communication
Message: Failed to fetch
```

**Solutions :**
1. Vérifier que Flask tourne : voir le terminal où vous avez lancé `python app.py`
2. Vérifier l'URL : doit être `http://localhost:5000`
3. Essayer de relancer Flask

### Erreur : "Script non trouvé"

**Symptômes :**
```
❌ Erreur lors de la création du devis
Message d'erreur: Script creer_devis non trouvé
```

**Solutions :**
1. Vérifier que le fichier existe : `scripts/202512_Creer_devis.py`
2. Vérifier que l'entrée existe dans app.py (SCRIPTS['creer_devis'])

### Erreur : Code de retour 1

**Symptômes :**
```
Code de retour: 1
```

**Solutions :**
1. Lire attentivement les logs dans "Sortie standard (stdout)"
2. Lire les erreurs dans "Erreurs (stderr)"
3. Cliquer sur "Afficher les données envoyées" pour voir ce qui a été envoyé
4. Cliquer sur "Afficher la réponse complète" pour voir tous les détails

### Erreur : Bâtiment non trouvé

**Symptômes :**
```
⚠️  Aucun bâtiment trouvé pour: Rue Test 1, 1180 Rolle
⚠️  Utilisation de données par défaut
```

**C'est normal !** Geo.admin ne trouve pas toujours tous les bâtiments.
Le script continue avec des données par défaut (EGID = N/A, surface = 100m², etc.)

### Erreur : Contact en double dans Bexio

**Symptômes :**
Le script crée un nouveau contact alors qu'il existe déjà

**Explication :**
Le script recherche par email exact. Si l'email est différent (même légèrement), il créera un nouveau contact.

**Solution :**
Utiliser exactement le même email que dans Bexio, ou accepter le doublon et le fusionner manuellement dans Bexio.

## Checklist de vérification complète

- [ ] Fichier `config.py` existe (copié depuis `config.py.example`)
- [ ] Token Bexio valide renseigné dans `config.py`
- [ ] Module `requests` installé (`pip install requests`)
- [ ] Serveur Flask démarré (`python app.py`)
- [ ] Console développeur ouverte (F12)
- [ ] Formulaire accessible à http://localhost:5000/devis/nouveau
- [ ] Logs visibles dans la console : "✅ Formulaire de création de devis chargé"
- [ ] Après soumission : logs "📤 Données envoyées" et "📥 Réponse du serveur"
- [ ] En cas d'erreur : sections debug visibles avec stdout/stderr

## Informations utiles pour le support

Si vous rencontrez un problème, collectez ces informations :

1. **Logs du terminal Flask** (copier tout le texte)
2. **Console du navigateur** (F12 → Console, copier les messages)
3. **Données envoyées** (cliquer sur "Afficher les données envoyées" dans l'erreur)
4. **Réponse complète** (cliquer sur "Afficher la réponse complète")
5. **Version Python** : `python --version`
6. **Modules installés** : `pip list | findstr -i "flask requests"`

## Test final complet

Voici un scénario de test complet :

```
1. Contact privé → CECB → Normal
   Résultat attendu : Offre créée avec 3 positions (CECB + Frais émission + Texte)

2. Contact privé → CECB Plus → Express
   Résultat attendu : Offre créée avec 5 positions (CECB + Frais + Express + CECB Plus + Texte)

3. Contact entreprise → CECB → Urgent
   Résultat attendu : Contact entreprise + personne associée + offre avec 4 positions

4. Contact privé → Conseil Incitatif
   Résultat attendu : Offre gratuite avec 2 positions (Conseil + Texte)
```

Chaque test devrait afficher dans les logs :
- ✅ Contact géré (créé ou trouvé)
- ✅ Données bâtiment récupérées (ou valeurs par défaut)
- ✅ Prix calculé (si applicable)
- ✅ Offre créée avec numéro d'offre

---

**En cas de problème persistant :** Consultez les logs détaillés dans la console et dans l'affichage du résultat de la page web.
