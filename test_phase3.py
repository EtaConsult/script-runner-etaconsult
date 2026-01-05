"""
Test de la Phase 3 - Rappel et pré-remplissage

Ce script teste la fonctionnalité de rappel de soumissions
pour pré-remplir le formulaire CECB.
"""

from app import app, db
from models import FormSubmission
import json


def test_recall_functionality():
    """Test du rappel et pré-remplissage des soumissions"""
    print("=" * 60)
    print("🧪 Test de la Phase 3 - Rappel et pré-remplissage")
    print("=" * 60)

    with app.app_context():
        # Récupérer toutes les soumissions de test
        submissions = FormSubmission.query.filter_by(user_id='1767522312539').all()

        if not submissions:
            print("❌ Aucune soumission trouvée. Exécutez d'abord test_phase2.py")
            return False

        print(f"\n✅ {len(submissions)} soumission(s) trouvée(s)\n")

        # Test 1: Vérifier la structure des données form_data
        print("1️⃣ Test de la structure des données")
        print("-" * 60)

        for i, sub in enumerate(submissions[:3], 1):
            print(f"\nSoumission #{sub.id} - {sub.client_name}")
            form_data = sub.form_data

            # Vérifier les champs essentiels
            essential_fields = ['type_contact', 'prenom', 'nom', 'email', 'type_certificat']
            missing = [f for f in essential_fields if f not in form_data and f.replace('nom', 'nom_famille') not in form_data]

            if missing:
                print(f"   ⚠️  Champs manquants: {', '.join(missing)}")
            else:
                print(f"   ✅ Tous les champs essentiels présents")

            # Afficher quelques champs
            print(f"   Type contact: {form_data.get('type_contact', 'N/A')}")
            print(f"   Client: {form_data.get('prenom', '')} {form_data.get('nom', form_data.get('nom_famille', ''))}")
            print(f"   Email: {form_data.get('email', 'N/A')}")
            print(f"   Type certificat: {form_data.get('type_certificat', 'N/A')}")

        # Test 2: Simuler le pré-remplissage
        print("\n\n2️⃣ Test de simulation du pré-remplissage")
        print("-" * 60)

        if submissions:
            test_sub = submissions[0]
            print(f"\nSimulation avec soumission #{test_sub.id}")

            # Convertir en dictionnaire (comme le ferait la route)
            sub_dict = test_sub.to_dict()

            print(f"\n📋 Données qui seront passées au template:")
            print(f"   ID: {sub_dict['id']}")
            print(f"   Client: {sub_dict['client_name']}")
            print(f"   Type: {sub_dict['certificate_type']}")
            print(f"   Statut: {sub_dict['status']}")
            print(f"   Form data keys: {list(sub_dict['form_data'].keys())}")

            # Vérifier que to_dict() fonctionne correctement
            assert 'form_data' in sub_dict, "form_data manquant dans to_dict()"
            assert isinstance(sub_dict['form_data'], dict), "form_data devrait être un dict"
            print(f"\n   ✅ Structure to_dict() valide")

        # Test 3: URLs de rappel
        print("\n\n3️⃣ Test des URLs de rappel")
        print("-" * 60)

        for i, sub in enumerate(submissions[:5], 1):
            url = f"/devis/nouveau/{sub.id}"
            print(f"{i}. {sub.client_name:30} → {url}")

        print(f"\n✅ {len(submissions)} URL(s) de rappel disponibles")

        # Test 4: Vérification des types de certificats
        print("\n\n4️⃣ Test des différents types de certificats")
        print("-" * 60)

        cert_types = {}
        for sub in submissions:
            cert_type = sub.certificate_type or 'Non défini'
            cert_types[cert_type] = cert_types.get(cert_type, 0) + 1

        for cert_type, count in cert_types.items():
            print(f"   {cert_type}: {count} soumission(s)")

        # Test 5: Vérification des adresses
        print("\n\n5️⃣ Test des adresses (facturation vs bâtiment)")
        print("-" * 60)

        for i, sub in enumerate(submissions[:3], 1):
            form_data = sub.form_data
            print(f"\nSoumission #{sub.id}")

            # Adresse facturation
            addr_fact = form_data.get('rue_facturation') or form_data.get('adresse_facturation', 'N/A')
            print(f"   Facturation: {addr_fact}")

            # Adresse bâtiment
            if form_data.get('adresse_identique'):
                print(f"   Bâtiment: Identique à facturation")
            else:
                addr_bat = form_data.get('rue_batiment') or form_data.get('adresse_batiment', 'N/A')
                print(f"   Bâtiment: {addr_bat}")

        # Résumé final
        print("\n\n" + "=" * 60)
        print("✅ Tests Phase 3 réussis!")
        print("=" * 60)
        print(f"\n📊 Résumé:")
        print(f"   Total de soumissions testées: {len(submissions)}")
        print(f"   Types de certificats: {', '.join(cert_types.keys())}")
        print(f"\n💡 Pour tester en vrai:")
        print(f"   1. Lancez l'application: python app.py")
        print(f"   2. Connectez-vous")
        print(f"   3. Allez sur /submissions")
        print(f"   4. Cliquez sur 🔄 (Rappeler) pour une soumission")
        print(f"   5. Vérifiez que le formulaire est pré-rempli")

        return True


def test_prefill_logic():
    """Test de la logique de pré-remplissage des champs"""
    print("\n\n" + "=" * 60)
    print("🧪 Test de la logique de pré-remplissage")
    print("=" * 60)

    with app.app_context():
        submission = FormSubmission.query.first()

        if not submission:
            print("❌ Aucune soumission trouvée")
            return False

        form_data = submission.form_data

        # Simuler les mappings de champs
        mappings = {
            'type_contact': form_data.get('type_contact'),
            'nom_entreprise': form_data.get('nom_entreprise'),
            'appellation': form_data.get('appellation'),
            'nom_famille': form_data.get('nom_famille') or form_data.get('nom'),
            'prenom': form_data.get('prenom'),
            'email': form_data.get('email'),
            'telephone': form_data.get('telephone'),
            'rue_facturation': form_data.get('rue_facturation') or form_data.get('adresse_facturation'),
            'npa_facturation': form_data.get('npa_facturation') or form_data.get('npa'),
            'localite_facturation': form_data.get('localite_facturation') or form_data.get('localite'),
            'pays_facturation': form_data.get('pays_facturation', 'Suisse'),
            'rue_batiment': form_data.get('rue_batiment') or form_data.get('adresse_batiment'),
            'npa_batiment': form_data.get('npa_batiment'),
            'localite_batiment': form_data.get('localite_batiment'),
            'type_certificat': form_data.get('type_certificat'),
            'nombre_etages': form_data.get('nombre_etages', 2),
            'sous_sol': form_data.get('sous_sol', 'Non chauffé'),
            'combles': form_data.get('combles', 'Non chauffé'),
            'delai': form_data.get('delai'),
            'contexte': form_data.get('contexte'),
            'message': form_data.get('message'),
            'adresse_identique': form_data.get('adresse_identique', False)
        }

        print(f"\n📋 Simulation de pré-remplissage pour: {submission.client_name}\n")

        for field_name, value in mappings.items():
            if value:
                print(f"   ✅ {field_name:25} = {value}")
            else:
                print(f"   ⚠️  {field_name:25} = (vide)")

        filled_count = sum(1 for v in mappings.values() if v)
        total_count = len(mappings)

        print(f"\n📊 Champs remplis: {filled_count}/{total_count} ({filled_count*100//total_count}%)")

        return True


if __name__ == '__main__':
    print("\n🚀 Lancement des tests Phase 3\n")

    # Test 1: Fonctionnalité de rappel
    if not test_recall_functionality():
        print("\n❌ Échec du test de rappel")
        exit(1)

    # Test 2: Logique de pré-remplissage
    if not test_prefill_logic():
        print("\n❌ Échec du test de pré-remplissage")
        exit(1)

    print("\n\n🎉 Tous les tests Phase 3 sont réussis!")
    print("✅ La fonctionnalité de rappel est prête à être testée dans le navigateur!\n")
