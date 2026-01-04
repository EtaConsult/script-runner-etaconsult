# -*- coding: utf-8 -*-
"""
Script de vérification rapide de la configuration
"""

import os
import sys

print("=" * 60)
print("🔍 Vérification de la configuration")
print("=" * 60)

# 1. Vérifier que config.py existe
print("\n1️⃣  Vérification du fichier config.py...")
if os.path.exists('config.py'):
    print("   ✅ config.py existe")
else:
    print("   ❌ config.py n'existe pas")
    print("   📋 Copiez config.py.example vers config.py :")
    print("      copy config.py.example config.py")
    sys.exit(1)

# 2. Importer config
print("\n2️⃣  Import de la configuration...")
try:
    import config
    print("   ✅ config.py importé avec succès")
except Exception as e:
    print(f"   ❌ Erreur lors de l'import : {e}")
    sys.exit(1)

# 3. Vérifier le token Bexio
print("\n3️⃣  Vérification du token Bexio...")
if hasattr(config, 'BEXIO_API_TOKEN'):
    token = config.BEXIO_API_TOKEN
    if token and token != "votre_token_bexio_ici":
        print(f"   ✅ Token Bexio renseigné ({len(token)} caractères)")
        print(f"      Aperçu: {token[:10]}...{token[-10:]}")
    else:
        print("   ❌ Token Bexio non renseigné ou valeur par défaut")
        print("   📋 Modifiez config.py et renseignez votre token Bexio")
        sys.exit(1)
else:
    print("   ❌ BEXIO_API_TOKEN non trouvé dans config.py")
    sys.exit(1)

# 4. Vérifier les autres paramètres
print("\n4️⃣  Vérification des autres paramètres...")
params_ok = True

if hasattr(config, 'TARIFS'):
    print("   ✅ TARIFS définis")
else:
    print("   ⚠️  TARIFS non définis (normal si vous utilisez tarifs.json)")

if hasattr(config, 'BEXIO_IDS'):
    print("   ✅ BEXIO_IDS définis")
else:
    print("   ❌ BEXIO_IDS manquants")
    params_ok = False

if hasattr(config, 'TEXTES'):
    print("   ✅ TEXTES définis")
else:
    print("   ⚠️  TEXTES non définis")

# 5. Vérifier que requests est installé
print("\n5️⃣  Vérification du module requests...")
try:
    import requests
    print(f"   ✅ requests installé (version {requests.__version__})")
except ImportError:
    print("   ❌ requests non installé")
    print("   📋 Installez avec : pip install requests")
    sys.exit(1)

# 6. Vérifier tarifs.json
print("\n6️⃣  Vérification de tarifs.json...")
if os.path.exists('tarifs.json'):
    print("   ✅ tarifs.json existe")
    try:
        import json
        with open('tarifs.json', 'r', encoding='utf-8') as f:
            tarifs = json.load(f)
            print(f"   ✅ tarifs.json valide ({len(tarifs)} paramètres)")
    except Exception as e:
        print(f"   ⚠️  Erreur de lecture : {e}")
else:
    print("   ⚠️  tarifs.json n'existe pas (utilise les valeurs de config.py)")

# 7. Test API Bexio (optionnel)
print("\n7️⃣  Test de connexion à l'API Bexio...")
test_api = input("   Voulez-vous tester la connexion à Bexio ? (o/n) : ")
if test_api.lower() == 'o':
    try:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {config.BEXIO_API_TOKEN}"
        }
        response = requests.get(
            f"{config.BEXIO_BASE_URL}/2.0/contact",
            headers=headers,
            params={"limit": 1},
            timeout=10
        )

        if response.status_code == 200:
            print("   ✅ Connexion API Bexio réussie !")
            print(f"      Status: {response.status_code}")
        else:
            print(f"   ❌ Erreur API Bexio: {response.status_code}")
            print(f"      Message: {response.text}")
            sys.exit(1)

    except Exception as e:
        print(f"   ❌ Erreur lors du test : {e}")
        sys.exit(1)
else:
    print("   ⏭️  Test API Bexio ignoré")

# Résumé final
print("\n" + "=" * 60)
if params_ok:
    print("✅ Configuration OK ! Vous pouvez démarrer l'application.")
    print("\n🚀 Pour lancer le serveur :")
    print("   python app.py")
    print("\n🌐 Puis ouvrir :")
    print("   http://localhost:5000/devis/nouveau")
else:
    print("⚠️  Configuration incomplète. Corrigez les erreurs ci-dessus.")

print("=" * 60)
