# Comment obtenir une clé API Google Maps

L'autocomplétion d'adresse dans le formulaire de création de devis CECB utilise l'API Google Places Autocomplete. Pour l'activer, vous devez obtenir une clé API Google Maps.

## 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Connectez-vous avec votre compte Google
3. Cliquez sur "Sélectionner un projet" → "Nouveau projet"
4. Donnez un nom à votre projet (ex: "Eta Consult Scripts")
5. Cliquez sur "Créer"

## 2. Activer l'API Places

1. Dans le menu de gauche, allez dans **APIs & Services** → **Library**
2. Recherchez "**Places API**"
3. Cliquez sur "**Places API**" dans les résultats
4. Cliquez sur le bouton "**Enable**" (Activer)

Répétez cette opération pour :
- **Maps JavaScript API** (obligatoire)

## 3. Créer une clé API

1. Allez dans **APIs & Services** → **Credentials**
2. Cliquez sur "**+ CREATE CREDENTIALS**" → "**API key**"
3. Une clé API sera générée et affichée
4. **Copiez cette clé** (elle ressemble à : `AIzaSyB...xyz123`)

## 4. Sécuriser la clé API (recommandé)

1. Cliquez sur "**Restrict Key**" (ou sur le nom de la clé)
2. Dans "**Application restrictions**" :
   - Sélectionnez "**HTTP referrers (web sites)**"
   - Ajoutez : `http://localhost:5000/*`
3. Dans "**API restrictions**" :
   - Sélectionnez "**Restrict key**"
   - Cochez :
     - **Places API**
     - **Maps JavaScript API**
4. Cliquez sur "**Save**"

## 5. Ajouter la clé dans config.py

1. Ouvrez `config.py` (ou créez-le depuis `config.py.example`)
2. Remplacez la ligne :
   ```python
   GOOGLE_MAPS_API_KEY = ""
   ```
   par :
   ```python
   GOOGLE_MAPS_API_KEY = "AIzaSyB...votre_cle_ici"
   ```
3. Sauvegardez le fichier

## 6. Tester

1. Redémarrez le serveur Flask si nécessaire
2. Allez sur http://localhost:5000/devis/nouveau
3. Dans le champ "Adresse complète", commencez à taper une adresse suisse
4. Vous devriez voir apparaître des suggestions d'adresses

## Tarification Google Maps API

- **Gratuit** : 40 000 requêtes par mois incluses
- Pour un usage personnel ou une petite entreprise, cela devrait être largement suffisant
- Au-delà : environ 17 USD pour 1000 requêtes supplémentaires

Pour un usage moyen (10-20 devis par jour), vous resterez dans le quota gratuit.

## En cas de problème

### Erreur "This API project is not authorized to use this API"

1. Vérifiez que vous avez bien activé **Places API** et **Maps JavaScript API** dans votre projet
2. Attendez 2-3 minutes que l'activation soit effective
3. Rafraîchissez la page

### Erreur "RefererNotAllowedMapError"

1. Vérifiez les restrictions HTTP referrers
2. Assurez-vous d'avoir ajouté `http://localhost:5000/*`
3. Essayez de retirer temporairement les restrictions pour tester

### L'autocomplétion ne s'affiche pas

1. Ouvrez la console développeur (F12)
2. Vérifiez s'il y a des erreurs JavaScript
3. Vérifiez que la clé est bien copiée dans `config.py`
4. Vérifiez qu'il n'y a pas d'espaces avant/après la clé

## Alternative sans clé API

Si vous ne souhaitez pas utiliser l'API Google Maps :

1. Laissez `GOOGLE_MAPS_API_KEY = ""` dans config.py
2. L'autocomplétion sera désactivée, mais le formulaire fonctionnera normalement
3. Vous devrez simplement taper manuellement les adresses complètes

---

**Note :** Ne jamais commiter votre clé API dans Git ! Le fichier `config.py` est déjà dans `.gitignore`.
