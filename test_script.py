# -*- coding: utf-8 -*-
"""
Script de test rapide pour vérifier que tout fonctionne
"""

import subprocess
import json

# Données de test minimales
test_data = {
    "type_contact": "Privé",
    "appellation": "M.",
    "nom_famille": "TestDebug",
    "prenom": "Script",
    "email": "script.test@example.com",
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
    "message": "Test automatique"
}

print("=" * 60)
print("🧪 Test du script de création de devis")
print("=" * 60)
print(f"📋 Données de test:")
print(json.dumps(test_data, indent=2, ensure_ascii=False))
print("=" * 60)

# Convertir en JSON string
json_data = json.dumps(test_data, ensure_ascii=False)

# Exécuter le script
print("\n🚀 Exécution du script...\n")

try:
    result = subprocess.run(
        ['python', 'scripts/202512_Creer_devis.py', json_data],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=60
    )

    print("=" * 60)
    print("📤 STDOUT:")
    print("=" * 60)
    print(result.stdout)

    if result.stderr:
        print("\n" + "=" * 60)
        print("⚠️  STDERR:")
        print("=" * 60)
        print(result.stderr)

    print("\n" + "=" * 60)
    print(f"🏁 Code de retour: {result.returncode}")
    print("=" * 60)

    if result.returncode == 0:
        print("\n✅ Test réussi !")
    else:
        print("\n❌ Test échoué !")
        print("\n💡 Vérifiez:")
        print("   1. Le fichier config.py existe et contient votre token Bexio")
        print("   2. Le module requests est installé (pip install requests)")
        print("   3. Les logs ci-dessus pour plus de détails")

except subprocess.TimeoutExpired:
    print("❌ Le script a dépassé le timeout de 60 secondes")
except FileNotFoundError:
    print("❌ Le script scripts/202512_Creer_devis.py n'a pas été trouvé")
    print("   Vérifiez que vous êtes dans le bon répertoire")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🔍 Pour plus de détails, consultez TEST_DEVIS.md")
print("=" * 60)
