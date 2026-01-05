"""
Test de la Phase 2 - Page de liste des soumissions

Ce script crée plusieurs soumissions de test pour vérifier l'affichage
et le fonctionnement de la page /submissions
"""

from app import app, db
from models import FormSubmission
from datetime import datetime, timedelta


def create_test_submissions():
    """Crée plusieurs soumissions de test avec différents statuts"""
    print("=" * 60)
    print("🧪 Création de soumissions de test pour Phase 2")
    print("=" * 60)

    with app.app_context():
        # Nettoyer les anciennes soumissions de test (optionnel)
        # FormSubmission.query.delete()
        # db.session.commit()

        test_submissions = [
            {
                'user_id': '1767522312539',
                'form_type': 'devis_cecb',
                'form_data': {
                    'type_contact': 'prive',
                    'prenom': 'Marie',
                    'nom': 'Dupont',
                    'email': 'marie.dupont@example.com',
                    'telephone': '+41 21 123 45 67',
                    'type_certificat': 'CECB',
                    'adresse_batiment': 'Route de l\'Hôpital 16b, 1180 Rolle',
                    'npa': '1180',
                    'localite': 'Rolle'
                },
                'certificate_type': 'CECB',
                'client_name': 'Marie Dupont',
                'building_address': 'Route de l\'Hôpital 16b, 1180 Rolle',
                'status': 'quote_created',
                'bexio_quote_id': '12345',
                'bexio_document_nr': 'A-0123',
                'created_at': datetime.utcnow() - timedelta(days=5)
            },
            {
                'user_id': '1767522312539',
                'form_type': 'devis_cecb',
                'form_data': {
                    'type_contact': 'societe',
                    'nom_societe': 'ABC Immobilier SA',
                    'prenom': 'Jean',
                    'nom': 'Martin',
                    'email': 'j.martin@abc-immo.ch',
                    'telephone': '+41 22 555 66 77',
                    'type_certificat': 'CECB Plus',
                    'adresse_batiment': 'Chemin des Vignes 42, 1009 Pully',
                    'npa': '1009',
                    'localite': 'Pully'
                },
                'certificate_type': 'CECB Plus',
                'client_name': 'Jean Martin',
                'building_address': 'Chemin des Vignes 42, 1009 Pully',
                'status': 'quote_created',
                'bexio_quote_id': '12346',
                'bexio_document_nr': 'A-0124',
                'created_at': datetime.utcnow() - timedelta(days=3)
            },
            {
                'user_id': '1767522312539',
                'form_type': 'devis_cecb',
                'form_data': {
                    'type_contact': 'prive',
                    'prenom': 'Sophie',
                    'nom': 'Leclerc',
                    'email': 'sophie.leclerc@example.com',
                    'telephone': '+41 24 888 99 00',
                    'type_certificat': 'Conseil Incitatif',
                    'adresse_batiment': 'Avenue du Général-Guisan 8, 1800 Vevey',
                    'npa': '1800',
                    'localite': 'Vevey'
                },
                'certificate_type': 'Conseil Incitatif',
                'client_name': 'Sophie Leclerc',
                'building_address': 'Avenue du Général-Guisan 8, 1800 Vevey',
                'status': 'submitted',
                'created_at': datetime.utcnow() - timedelta(hours=2)
            },
            {
                'user_id': '1767522312539',
                'form_type': 'devis_cecb',
                'form_data': {
                    'type_contact': 'prive',
                    'prenom': 'Luc',
                    'nom': 'Perret',
                    'email': 'luc.perret@example.com',
                    'telephone': '+41 21 777 88 99',
                    'type_certificat': 'CECB',
                    'adresse_batiment': 'Rue de la Gare 15, 1110 Morges',
                    'npa': '1110',
                    'localite': 'Morges'
                },
                'certificate_type': 'CECB',
                'client_name': 'Luc Perret',
                'building_address': 'Rue de la Gare 15, 1110 Morges',
                'status': 'error',
                'error_message': 'Erreur de connexion à l\'API Bexio',
                'created_at': datetime.utcnow() - timedelta(days=1)
            },
            {
                'user_id': '1767522312539',
                'form_type': 'devis_cecb',
                'form_data': {
                    'type_contact': 'societe',
                    'nom_societe': 'Fiduciaire XYZ Sàrl',
                    'prenom': 'Claire',
                    'nom': 'Dubois',
                    'email': 'c.dubois@xyz-fiduciaire.ch',
                    'telephone': '+41 21 333 44 55',
                    'type_certificat': 'CECB Plus',
                    'adresse_batiment': 'Boulevard de Grancy 29, 1006 Lausanne',
                    'npa': '1006',
                    'localite': 'Lausanne'
                },
                'certificate_type': 'CECB Plus',
                'client_name': 'Claire Dubois',
                'building_address': 'Boulevard de Grancy 29, 1006 Lausanne',
                'status': 'quote_created',
                'bexio_quote_id': '12347',
                'bexio_document_nr': 'A-0125',
                'created_at': datetime.utcnow() - timedelta(hours=5)
            }
        ]

        created_count = 0
        for sub_data in test_submissions:
            try:
                submission = FormSubmission(**sub_data)
                db.session.add(submission)
                db.session.commit()
                created_count += 1
                status_icon = {
                    'quote_created': '✅',
                    'submitted': '⏳',
                    'error': '❌'
                }
                print(f"{status_icon.get(sub_data['status'], '•')} Soumission créée: {sub_data['client_name']} - {sub_data['status']}")
            except Exception as e:
                print(f"❌ Erreur pour {sub_data['client_name']}: {str(e)}")
                db.session.rollback()

        print("\n" + "=" * 60)
        print(f"✅ {created_count}/{len(test_submissions)} soumissions créées avec succès")
        print("=" * 60)

        # Afficher les statistiques
        all_subs = FormSubmission.query.filter_by(user_id='1767522312539').all()
        total = len(all_subs)
        created = len([s for s in all_subs if s.status == 'quote_created'])
        pending = len([s for s in all_subs if s.status == 'submitted'])
        errors = len([s for s in all_subs if s.status == 'error'])

        print(f"\n📊 Statistiques totales:")
        print(f"   Total: {total}")
        print(f"   Devis créés: {created}")
        print(f"   En attente: {pending}")
        print(f"   Erreurs: {errors}")
        print("\n✅ Vous pouvez maintenant tester la page /submissions dans votre navigateur!")


if __name__ == '__main__':
    create_test_submissions()
