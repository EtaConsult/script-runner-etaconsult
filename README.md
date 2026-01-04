# 🚀 Script Runner - Application Web Locale

Application Flask pour exécuter vos scripts Python via une interface web moderne et évolutive.

## 📋 Installation

### 1. Prérequis
```bash
python 3.8+
pip install flask
```

### 2. Structure du projet
```
script_runner/
├── app.py              # Serveur Flask
├── templates/
│   └── index.html      # Interface web
├── static/
│   └── style.css       # Styles
├── scripts/            # Vos scripts Python
│   ├── exemple_simple.py
│   └── exemple_avec_args.py
└── README.md
```

## 🚀 Utilisation

### Démarrer l'application
```bash
cd script_runner
python app.py
```

Ouvrir dans le navigateur : **http://localhost:5000**

### Arrêter l'application
Dans le terminal : `Ctrl + C`

## ➕ Ajouter un nouveau script

### Méthode simple (3 étapes)

**1. Créer ton script dans le dossier `scripts/`**

Exemple : `scripts/mon_script.py`
```python
def main():
    print("Mon script fonctionne !")

if __name__ == "__main__":
    main()
```

**2. Ajouter la configuration dans `app.py`**

Ouvrir `app.py` et ajouter dans le dictionnaire `SCRIPTS` :

```python
SCRIPTS = {
    # ... scripts existants ...
    
    'mon_script': {
        'name': 'Mon Super Script',
        'file': 'mon_script.py',
        'description': 'Description de ce que fait le script',
        'category': 'Mes Scripts'
    },
}
```

**3. Recharger la page** (l'app Flask se recharge automatiquement en mode debug)

✅ C'est tout ! Ton script apparaît maintenant dans l'interface.

## 📦 Exemples de configuration

### Script simple (sans arguments)
```python
'cecb_quick_edit': {
    'name': 'CECB Quick Edit',
    'file': 'CECB_QuickEdit.py',
    'description': 'Édition rapide des faces CECB dans Rhino',
    'category': 'CECB'
}
```

### Script avec arguments
```python
'analyse_batiment': {
    'name': 'Analyse Bâtiment',
    'file': 'analyse_batiment.py',
    'description': 'Analyse thermique d\'un bâtiment',
    'category': 'CECB',
    'args': ['chemin_fichier', 'zone_climatique']  # Arguments attendus
}
```

Le script doit accepter les arguments via `sys.argv` :
```python
import sys

def main():
    chemin = sys.argv[1]  # Premier argument
    zone = sys.argv[2]    # Deuxième argument
    # ... ton code ...

if __name__ == "__main__":
    main()
```

## 🎨 Catégories

Les scripts sont automatiquement groupés par catégorie. Exemples :
- `'CECB'` → Scripts de certification énergétique
- `'Rhino'` → Scripts de modélisation 3D
- `'Rapports'` → Génération de documents
- `'Utilitaires'` → Outils divers

## 📊 Fonctionnalités

✅ **Exécution en un clic** - Lance tes scripts directement depuis l'interface  
✅ **Logs en temps réel** - Vois le déroulement de chaque script  
✅ **Indicateurs de statut** - Suis l'état d'exécution (en cours, succès, erreur)  
✅ **Arguments dynamiques** - Entre des paramètres pour tes scripts  
✅ **Organisation par catégories** - Groupe tes scripts logiquement  
✅ **Design moderne** - Interface professionnelle et agréable  

## 🔧 Configuration avancée

### Changer le port
Dans `app.py`, ligne finale :
```python
app.run(debug=True, host='localhost', port=5000)  # Change 5000
```

### Timeout d'exécution
Par défaut : 5 minutes. Pour modifier, dans `app.py` :
```python
result = subprocess.run(
    cmd,
    timeout=300  # Modifie ici (en secondes)
)
```

### Désactiver le mode debug
Pour la production :
```python
app.run(debug=False, host='localhost', port=5000)
```

## 💡 Conseils

### Bonnes pratiques pour tes scripts

1. **Utilise `print()` pour les logs** - Ils apparaîtront dans l'interface
2. **Gère les erreurs** - Utilise try/except pour éviter les crashs
3. **Retourne un code de sortie** - `sys.exit(0)` pour succès, `sys.exit(1)` pour erreur
4. **Documente tes scripts** - Ajoute des descriptions claires

### Exemple de script robuste
```python
import sys

def main():
    try:
        print("🚀 Démarrage du script...")
        
        # Ton code ici
        resultat = faire_le_traitement()
        
        print(f"✅ Terminé : {resultat}")
        sys.exit(0)  # Succès
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)  # Échec

if __name__ == "__main__":
    main()
```

## 🎯 Cas d'usage

- **Scripts CECB** : Automatiser les certifications énergétiques
- **Scripts Rhino** : Lancer des processus 3D sans ouvrir Rhino
- **Génération de rapports** : Créer des PDFs, DOCX automatiquement
- **Traitement de données** : Analyser des fichiers Excel, CSV
- **Intégrations** : Connecter différents outils (Bexio, OneDrive...)

## 🐛 Dépannage

**Le script ne s'affiche pas**
- Vérifie que tu as bien ajouté la config dans `SCRIPTS`
- Vérifie que le fichier `.py` existe dans le dossier `scripts/`
- Recharge la page

**Le script ne s'exécute pas**
- Regarde les logs dans l'interface (panneau de droite)
- Vérifie les permissions du fichier
- Teste le script manuellement : `python scripts/mon_script.py`

**Erreur "Module not found"**
- Installe les dépendances : `pip install nom_du_module`
- Utilise un environnement virtuel si nécessaire

## 📞 Support

Pour toute question ou amélioration, n'hésite pas à modifier le code !  
C'est ton application, adapte-la à tes besoins.

---

**Fait avec ❤️ pour Êta Consult Sàrl**
