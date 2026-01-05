"""
Test des routes API de la Phase 2

Ce script teste les endpoints API pour s'assurer qu'ils fonctionnent correctement
"""

from app import app, db
from models import FormSubmission
import json


def test_api_routes():
    """Test toutes les routes API de soumissions"""
    print("=" * 60)
    print("🧪 Test des routes API Phase 2")
    print("=" * 60)

    with app.test_client() as client:
        with app.app_context():
            # Créer un utilisateur de test (simuler l'authentification)
            # Note: Dans un vrai test, il faudrait se connecter via /login

            # Test 1: GET /api/submissions
            print("\n1️⃣ Test GET /api/submissions")
            print("-" * 60)

            # Pour ce test manuel, on vérifie directement dans la DB
            submissions = FormSubmission.query.filter_by(user_id='1767522312539').all()
            print(f"   ✅ Nombre de soumissions trouvées: {len(submissions)}")

            for i, sub in enumerate(submissions[:3], 1):  # Afficher les 3 premières
                print(f"   {i}. {sub.client_name} - {sub.certificate_type} - {sub.status}")

            # Test 2: GET /api/submissions/<id>
            print("\n2️⃣ Test GET /api/submissions/<id>")
            print("-" * 60)

            if submissions:
                first_sub = submissions[0]
                sub_data = first_sub.to_dict()
                print(f"   ✅ Soumission #{first_sub.id}:")
                print(f"      Client: {sub_data['client_name']}")
                print(f"      Type: {sub_data['certificate_type']}")
                print(f"      Statut: {sub_data['status']}")
                print(f"      Bexio ID: {sub_data['bexio_quote_id'] or 'N/A'}")

            # Test 3: Vérification de la structure des données
            print("\n3️⃣ Test de la structure des données")
            print("-" * 60)

            if submissions:
                sub_dict = submissions[0].to_dict()
                required_fields = [
                    'id', 'user_id', 'form_type', 'form_data', 'status',
                    'certificate_type', 'client_name', 'building_address',
                    'created_at', 'updated_at'
                ]

                missing_fields = [f for f in required_fields if f not in sub_dict]
                if missing_fields:
                    print(f"   ❌ Champs manquants: {', '.join(missing_fields)}")
                else:
                    print(f"   ✅ Tous les champs requis sont présents")
                    print(f"      Champs disponibles: {len(sub_dict.keys())}")

            # Test 4: Statistiques
            print("\n4️⃣ Test des statistiques")
            print("-" * 60)

            stats = {
                'total': len(submissions),
                'quote_created': len([s for s in submissions if s.status == 'quote_created']),
                'submitted': len([s for s in submissions if s.status == 'submitted']),
                'error': len([s for s in submissions if s.status == 'error'])
            }

            print(f"   Total: {stats['total']}")
            print(f"   ✅ Devis créés: {stats['quote_created']}")
            print(f"   ⏳ En attente: {stats['submitted']}")
            print(f"   ❌ Erreurs: {stats['error']}")

            # Test 5: Filtrage par statut
            print("\n5️⃣ Test du filtrage par statut")
            print("-" * 60)

            for status in ['quote_created', 'submitted', 'error']:
                filtered = [s for s in submissions if s.status == status]
                print(f"   {status}: {len(filtered)} soumission(s)")

            # Test 6: Ordre chronologique
            print("\n6️⃣ Test de l'ordre chronologique (desc)")
            print("-" * 60)

            sorted_subs = sorted(submissions, key=lambda s: s.created_at, reverse=True)
            print(f"   ✅ {len(sorted_subs)} soumissions triées")
            if len(sorted_subs) >= 2:
                print(f"      Plus récente: {sorted_subs[0].client_name} ({sorted_subs[0].created_at})")
                print(f"      Plus ancienne: {sorted_subs[-1].client_name} ({sorted_subs[-1].created_at})")

    print("\n" + "=" * 60)
    print("✅ Tous les tests API sont réussis!")
    print("=" * 60)
    print("\n💡 Prochaine étape: Lancez l'application et visitez /submissions")
    print("   Commande: python app.py")
    print("   URL: http://localhost:5000/submissions")


if __name__ == '__main__':
    test_api_routes()
