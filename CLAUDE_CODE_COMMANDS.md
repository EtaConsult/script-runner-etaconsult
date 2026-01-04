# Commandes Git pour Claude Code

Lorsque tu dois déployer des modifications, utilise cette séquence exacte :

## Séquence de déploiement

```bash
# 1. Vérifier les modifications
git status

# 2. Ajouter tous les fichiers modifiés (sauf config.py, users.json, tarifs.json, textes.json)
git add .

# 3. Si des fichiers sensibles apparaissent, les retirer
git reset HEAD config.py users.json tarifs.json textes.json

# 4. Créer le commit avec un message descriptif
git commit -m "TYPE: Description concise

- Détail 1
- Détail 2
- Impact utilisateur si applicable"

# 5. Pousser vers GitHub
git push origin main
```

## Format des messages

**TYPE peut être** :
- `Fix` : Correction de bug
- `Feature` : Nouvelle fonctionnalité
- `Update` : Mise à jour fonctionnalité existante
- `Refactor` : Réorganisation code sans changement fonctionnel
- `Docs` : Documentation uniquement

## Exemple complet

```bash
git add scripts/202512_Creer_devis.py CHANGELOG.md
git commit -m "Fix: Calcul dynamique facteur CECB Plus

- Facteur basé sur S_eq au lieu de valeur fixe
- Facteurs: 3.69/2.29/1.79 selon surface
- Impact: Prix CECB Plus plus précis"
git push origin main
```

## Après le push

**IMPORTANT** : Informer l'utilisateur de se connecter à PythonAnywhere pour :
1. `cd ~/script-runner-etaconsult`
2. `git pull`
3. Dashboard > Web > Reload

## Fichiers à NE JAMAIS committer

- config.py
- users.json
- tarifs.json
- textes.json
- .env
- __pycache__/
- *.pyc

## Vérification avant commit

Toujours exécuter avant de committer :

```bash
# Voir les fichiers qui seront committés
git status

# Si config.py, users.json, tarifs.json ou textes.json apparaissent
git reset HEAD [nom_du_fichier]
```

## Commandes utiles

```bash
# Annuler le dernier commit (garde les modifications)
git reset --soft HEAD~1

# Voir l'historique des commits
git log --oneline -10

# Voir les différences avant de committer
git diff

# Voir les différences d'un fichier spécifique
git diff chemin/vers/fichier.py
```

## En cas d'erreur

### Push refusé (rejected)

```bash
# Récupérer les modifications distantes
git pull origin main

# Résoudre les conflits si nécessaire
# Puis repousser
git push origin main
```

### Fichier sensible commité par erreur

**STOP !** Ne pas pousser !

```bash
# Retirer le fichier du dernier commit
git reset HEAD~1 chemin/vers/fichier_sensible.py

# Re-commit sans le fichier sensible
git add .
git commit -m "Message original"
```

Si déjà poussé → contacter immédiatement l'administrateur !

---

**Date de création** : 2025-01-04  
**Pour** : Claude Code automation  
**Projet** : Script Runner Êta Consult
