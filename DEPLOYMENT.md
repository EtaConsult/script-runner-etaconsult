# Guide de déploiement - Êta Consult Script Runner

## 🎯 Workflow de développement

### Architecture
- **Développement local** : Windows (Claude Code)
- **Production** : PythonAnywhere (etaconsult.pythonanywhere.com)
- **Versioning** : GitHub (EtaConsult/script-runner-etaconsult)

---

## 📂 Structure des fichiers

### Fichiers versionnés (à pusher sur Git)
```
✅ app.py
✅ auth.py
✅ scripts/*.py
✅ templates/*.html
✅ static/*.css
✅ requirements.txt
✅ .gitignore
✅ README.md
✅ CHANGELOG.md
✅ DEPLOYMENT.md
✅ config.py.example
```

### Fichiers NON versionnés (sensibles)
```
❌ config.py          # Credentials API
❌ users.json         # Comptes utilisateurs
❌ tarifs.json        # Données métier
❌ textes.json        # Données métier
❌ .env               # Variables d'environnement
```

Ces fichiers sont listés dans `.gitignore` et ne doivent JAMAIS être committés.

---

## 🔄 Processus de déploiement complet

### ÉTAPE 1 : Développement local avec Claude Code

1. **Faire les modifications** dans les fichiers du projet
2. **Tester localement** si possible
3. **Documenter les changements** dans `CHANGELOG.md`

### ÉTAPE 2 : Commit et Push sur GitHub

**Commandes Git à exécuter** (dans le terminal Windows) :

```bash
# Se placer dans le répertoire du projet
cd "C:\Users\info\OneDrive\Documents_Eta Consult\18. Scripts\202512_Script_runner"

# Vérifier les modifications
git status

# Ajouter les fichiers modifiés
git add .

# Créer un commit avec un message descriptif
git commit -m "Description claire des modifications"

# Pousser vers GitHub
git push origin main
```

**Format des messages de commit** :
- `Fix: Description du bug corrigé`
- `Feature: Nouvelle fonctionnalité`
- `Update: Mise à jour d'une fonctionnalité`
- `Refactor: Réorganisation du code`
- `Docs: Mise à jour documentation`

### ÉTAPE 3 : Déploiement sur PythonAnywhere

**Se connecter à PythonAnywhere** : https://www.pythonanywhere.com/login/

**Dans la console Bash PythonAnywhere** :

```bash
# Se placer dans le répertoire
cd ~/script-runner-etaconsult

# Récupérer les dernières modifications depuis GitHub
git pull

# Si des dépendances ont été ajoutées dans requirements.txt
source venv/bin/activate
pip install -r requirements.txt --break-system-packages
```

**Recharger l'application** :
- Dashboard > Web > Bouton vert **"Reload etaconsult.pythonanywhere.com"**

### ÉTAPE 4 : Vérification

- Tester l'application sur https://etaconsult.pythonanywhere.com
- Vérifier les logs d'erreur si nécessaire : Dashboard > Web > Error log

---

## 🔧 Modifications de configuration (config.py, tarifs.json, etc.)

Ces fichiers ne sont **PAS versionnés** car ils contiennent des données sensibles ou métier.

### Pour modifier config.py en production

**Sur PythonAnywhere, console Bash** :

```bash
cd ~/script-runner-etaconsult
nano config.py
# Faire les modifications
# Ctrl+O pour sauvegarder, Enter, Ctrl+X pour quitter
```

Puis **Reload l'app**.

### Pour modifier tarifs.json ou textes.json en production

Même procédure :

```bash
cd ~/script-runner-etaconsult
nano tarifs.json
# Modifications
# Ctrl+O, Enter, Ctrl+X
```

Puis **Reload l'app**.

---

## 📝 Template de commit complet

Après avoir fait des modifications avec Claude Code, exécuter :

```bash
cd "C:\Users\info\OneDrive\Documents_Eta Consult\18. Scripts\202512_Script_runner"

# Vérifier ce qui a changé
git status
git diff

# Ajouter les fichiers
git add scripts/202512_Creer_devis.py  # (exemple)
git add CHANGELOG.md

# Commit
git commit -m "Fix: Calcul dynamique facteur CECB Plus selon surface équivalente

- Remplace facteur fixe 1.5 par calcul dynamique
- Facteurs: 3.69 (<160m²), 2.29 (160-750m²), 1.79 (>750m²)
- Test: S_eq=314m² donne facteur=2.29 (OK)"

# Push
git push origin main
```

---

## 🚨 Points d'attention critiques

### 1. Ne JAMAIS committer les fichiers sensibles

Avant chaque commit, vérifier :
```bash
git status
```

Si `config.py`, `users.json`, `tarifs.json` ou `textes.json` apparaissent, **NE PAS les ajouter** !

### 2. Fix proxy PythonAnywhere

Tout appel API externe dans les scripts doit inclure ce fix en début de fichier :

```python
import os
# Désactiver le proxy PythonAnywhere
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
```

Exemple : `scripts/config_manager.py` ligne 15-17

### 3. Recharger l'app après chaque déploiement

**Dashboard > Web > Reload** est OBLIGATOIRE, sinon Python garde l'ancienne version en cache.

### 4. IDs Bexio spécifiques

En production, `config.py` contient :
```python
BEXIO_IDS = {
    "currency_id": 1,
    "language_id": 2,
    "mwst_type": 0,
    "user_id": 1,
    "tax_id": 28  # Spécifique au compte Bexio
}
```

Ces valeurs peuvent différer entre environnements (dev/prod).

---

## 📊 Checklist de déploiement

Avant chaque déploiement, vérifier :

- [ ] Modifications testées localement (si possible)
- [ ] CHANGELOG.md mis à jour
- [ ] Aucun fichier sensible dans `git status`
- [ ] Message de commit descriptif
- [ ] Git push réussi
- [ ] Git pull sur PythonAnywhere réussi
- [ ] App rechargée sur PythonAnywhere
- [ ] Tests fonctionnels sur https://etaconsult.pythonanywhere.com
- [ ] Logs d'erreur vérifiés

---

## 🆘 En cas de problème

### L'app ne démarre plus

1. Vérifier les logs : Dashboard > Web > Error log
2. Vérifier le fichier WSGI : Dashboard > Web > WSGI configuration file
3. Tester Python manuellement :
   ```bash
   cd ~/script-runner-etaconsult
   python3 -c "from app import app; print('OK')"
   ```

### Erreur "Module not found"

Dépendance manquante :
```bash
cd ~/script-runner-etaconsult
source venv/bin/activate
pip install nom_du_module --break-system-packages
```

### Erreur de connexion API Bexio

Vérifier que le fix proxy est présent dans le fichier concerné.

### Changements Git non pris en compte

Forcer le reload de Python :
```bash
cd ~/script-runner-etaconsult
touch app.py
```
Puis Dashboard > Web > Reload

---

## 📞 Support

- **Documentation PythonAnywhere** : https://help.pythonanywhere.com
- **Logs de l'application** : Dashboard > Web > Error log / Server log
- **Forums PythonAnywhere** : https://www.pythonanywhere.com/forums/

---

**Date de création** : 2025-01-04  
**Dernière mise à jour** : 2025-01-04  
**Version de l'app** : 1.0.0
