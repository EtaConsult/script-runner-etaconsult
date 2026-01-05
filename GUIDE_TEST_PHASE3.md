# Guide de test - Phase 3 : Rappel et pré-remplissage

## Préparation

### 1. Lancer l'application

```bash
cd "C:\Users\info\OneDrive\Documents_Eta Consult\18. Scripts\202512_Script_runner"
python app.py
```

L'application devrait démarrer sur `http://localhost:5000` ou `http://127.0.0.1:5000`

### 2. Se connecter

- Ouvrir le navigateur
- Aller sur `http://localhost:5000`
- Se connecter avec vos identifiants

---

## Tests à effectuer

### ✅ Test 1 : Vérifier le bouton Rappeler

**Objectif** : S'assurer que le bouton 🔄 est visible et fonctionnel

**Étapes:**
1. Cliquer sur "📋 Mes soumissions" dans le header
2. Vérifier que la page affiche les soumissions

**Résultat attendu:**
- La table affiche 6 soumissions (créées par test_phase2.py)
- Chaque ligne a 3 boutons : 🔄 (Rappeler), 👁️ (Voir), 🗑️ (Supprimer)
- Le bouton 🔄 est de couleur cyan/bleu clair

**Capture d'écran suggérée:** Table avec les 3 boutons visibles

---

### ✅ Test 2 : Rappeler une soumission simple (CECB)

**Objectif** : Tester le pré-remplissage basique

**Étapes:**
1. Sur la page /submissions, trouver la soumission "Marie Dupont" (type CECB)
2. Cliquer sur le bouton 🔄 (Rappeler)
3. Observer le formulaire qui s'ouvre

**Résultat attendu:**
- Le formulaire s'ouvre à `/devis/nouveau/2`
- Dans les logs (panneau de droite), message :
  - `🔄 Pré-remplissage du formulaire...`
  - `✅ Formulaire pré-rempli avec les données de "Marie Dupont"`
  - `📋 Type: CECB | Créé le: 31.12.2025`
- Les champs suivants sont pré-remplis :
  - Type de contact: "Privé"
  - Prénom: "Marie"
  - Nom: "Dupont"
  - Email: "marie.dupont@example.com"
  - Téléphone: "+41 21 123 45 67"
  - Type de certificat: "CECB"
  - Adresse du bâtiment: "Route de l'Hôpital 16b, 1180 Rolle"
  - NPA: "1180"
  - Localité: "Rolle"

**Captures d'écran:**
1. Message de confirmation dans les logs
2. Champs pré-remplis (section 1 - Coordonnées)
3. Champs pré-remplis (section 3 - Bâtiment)

---

### ✅ Test 3 : Rappeler une soumission Société (CECB Plus)

**Objectif** : Tester le pré-remplissage pour un contact entreprise

**Étapes:**
1. Retour sur /submissions
2. Trouver la soumission "Jean Martin" (CECB Plus)
3. Cliquer sur 🔄

**Résultat attendu:**
- Type de contact: "Société"
- Le champ "Nom de l'entreprise" devient visible
- Nom entreprise: "ABC Immobilier SA"
- Prénom: "Jean"
- Nom: "Martin"
- Email: "j.martin@abc-immo.ch"
- Type de certificat: "CECB Plus"
- Adresse: "Chemin des Vignes 42, 1009 Pully"

**Note:** Vérifier que le champ entreprise apparaît bien quand type_contact = "societe"

---

### ✅ Test 4 : Rappeler Conseil Incitatif

**Objectif** : Vérifier que le type Conseil Incitatif fonctionne

**Étapes:**
1. Retour sur /submissions
2. Trouver "Sophie Leclerc" (Conseil Incitatif, statut En attente)
3. Cliquer sur 🔄

**Résultat attendu:**
- Type de contact: "Privé"
- Client: "Sophie Leclerc"
- Type de certificat: "Conseil Incitatif"
- Adresse: "Avenue du Général-Guisan 8, 1800 Vevey"
- Le champ "Délai" devrait être caché (spécifique à Conseil Incitatif)

---

### ✅ Test 5 : Modifier et créer un nouveau devis

**Objectif** : Vérifier qu'on peut modifier les données pré-remplies

**Étapes:**
1. Rappeler n'importe quelle soumission
2. Modifier quelques champs :
   - Changer le prénom de "Marie" à "Marie-Claire"
   - Changer le téléphone
   - Ajouter un message dans le champ "Message optionnel"
3. **NE PAS** soumettre le formulaire (pour éviter de créer un vrai devis Bexio)

**Résultat attendu:**
- Tous les champs peuvent être modifiés
- Les modifications sont bien prises en compte
- Le formulaire reste fonctionnel

**Alternative (si vous voulez tester la soumission complète):**
- Soumettre le formulaire
- Vérifier qu'un nouveau devis est créé dans Bexio
- Vérifier qu'une nouvelle soumission apparaît dans /submissions

---

### ✅ Test 6 : Accès direct via URL

**Objectif** : Tester l'accès direct par URL

**Étapes:**
1. Dans la barre d'adresse, taper manuellement :
   - `http://localhost:5000/devis/nouveau/1`
2. Appuyer sur Entrée

**Résultat attendu:**
- Le formulaire s'ouvre avec les données de la soumission #1 (Jean Dupont)
- Pré-remplissage automatique fonctionne

---

### ✅ Test 7 : Sécurité - Accès refusé

**Objectif** : Vérifier qu'on ne peut pas accéder aux soumissions d'autres utilisateurs

**Étapes:**
1. Essayer d'accéder à une soumission qui n'existe pas :
   - `http://localhost:5000/devis/nouveau/999`

**Résultat attendu:**
- Message flash en haut de la page : "Soumission non trouvée ou accès refusé"
- Le formulaire s'affiche mais VIDE (pas de pré-remplissage)

---

### ✅ Test 8 : Différents navigateurs

**Objectif** : Tester la compatibilité multi-navigateurs

**Navigateurs à tester:**
- Chrome
- Firefox
- Edge
- Safari (si disponible)

**Test simple:**
1. Ouvrir /submissions
2. Cliquer sur 🔄 pour une soumission
3. Vérifier que le pré-remplissage fonctionne

**Résultat attendu:**
- Fonctionne sur tous les navigateurs modernes
- Pas d'erreur JavaScript dans la console

---

### ✅ Test 9 : Console développeur

**Objectif** : Vérifier qu'il n'y a pas d'erreurs JavaScript

**Étapes:**
1. Ouvrir les outils développeur (F12)
2. Aller dans l'onglet "Console"
3. Rappeler une soumission
4. Observer les messages dans la console

**Résultat attendu:**
- Message : `🔄 Pré-remplissage du formulaire avec: {Object}`
- L'objet contient toutes les données du formulaire
- **Pas d'erreur rouge** dans la console

---

### ✅ Test 10 : Performance

**Objectif** : Vérifier que le chargement est rapide

**Étapes:**
1. Rappeler une soumission
2. Observer le temps de chargement
3. Utiliser l'onglet "Network" des DevTools si nécessaire

**Résultat attendu:**
- La page se charge en moins de 1 seconde
- Le pré-remplissage se fait en moins de 1 seconde après le chargement
- Total : < 2 secondes pour avoir le formulaire complètement pré-rempli

---

## Checklist rapide

Cocher au fur et à mesure :

- [ ] Test 1 : Bouton Rappeler visible
- [ ] Test 2 : Pré-remplissage CECB (Marie Dupont)
- [ ] Test 3 : Pré-remplissage Société (Jean Martin)
- [ ] Test 4 : Pré-remplissage Conseil Incitatif (Sophie Leclerc)
- [ ] Test 5 : Modification des champs
- [ ] Test 6 : Accès direct via URL
- [ ] Test 7 : Sécurité (soumission inexistante)
- [ ] Test 8 : Compatibilité navigateurs
- [ ] Test 9 : Pas d'erreur console
- [ ] Test 10 : Performance acceptable

---

## Problèmes connus et solutions

### Le formulaire ne se pré-remplit pas

**Symptômes:**
- Le formulaire s'ouvre vide
- Pas de message dans les logs

**Causes possibles:**
1. JavaScript désactivé
2. Erreur dans la console
3. Délai de 500ms pas respecté

**Solution:**
- Ouvrir la console (F12)
- Vérifier les erreurs
- Vérifier que `submissionData` est bien défini

---

### Certains champs restent vides

**Symptômes:**
- Quelques champs ne sont pas pré-remplis
- La plupart des champs fonctionnent

**Causes possibles:**
1. Données manquantes dans la soumission d'origine
2. Nom de champ différent

**Solution:**
- Normal si les données n'étaient pas renseignées à l'origine
- Vérifier dans la console : `submissionData.form_data`

---

### Le bouton 🔄 n'apparaît pas

**Symptômes:**
- Seulement 2 boutons (👁️ et 🗑️)

**Cause:**
- Le fichier submissions.html n'a pas été mis à jour

**Solution:**
- Relancer l'application
- Vider le cache du navigateur (Ctrl+F5)

---

## Données de test disponibles

Après avoir exécuté `test_phase2.py`, vous avez ces soumissions :

| ID | Client | Type | Statut | Lien Bexio |
|----|--------|------|--------|-----------|
| 1 | Jean Dupont | CECB | Créé | A-0123 |
| 2 | Marie Dupont | CECB | Créé | A-0123 |
| 3 | Jean Martin | CECB Plus | Créé | A-0124 |
| 4 | Sophie Leclerc | Conseil Incitatif | En attente | - |
| 5 | Luc Perret | CECB | Erreur | - |
| 6 | Claire Dubois | CECB Plus | Créé | A-0125 |

Utilisez ces soumissions pour vos tests !

---

## Support

Si vous rencontrez un problème :

1. **Vérifier la console JavaScript** (F12 → Console)
2. **Vérifier les logs Flask** (terminal où app.py tourne)
3. **Re-exécuter les tests** :
   ```bash
   python test_phase3.py
   ```

---

**Bon test ! 🚀**
