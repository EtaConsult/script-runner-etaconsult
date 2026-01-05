"""
Test de sauvegarde des soumissions de formulaires

Ce script teste la fonctionnalité de persistance des données de formulaires
implémentée dans la Phase 1.
"""

from app import app, db
from models import FormSubmission
import json


def test_submission_creation():
    """Test de création d'une soumission dans la base de données"""
    print("=" * 60)
    print("🧪 Test de sauvegarde des soumissions")
    print("=" * 60)

    with app.app_context():
        # Données de test
        test_data = {
            'type_contact': 'prive',
            'prenom': 'Jean',
            'nom': 'Dupont',
            'email': 'jean.dupont@example.com',
            'telephone': '+41 21 123 45 67',
            'type_certificat': 'CECB',
            'adresse_batiment': 'Route de l\'Hôpital 16b, 1180 Rolle',
            'npa': '1180',
            'localite': 'Rolle'
        }

        # Créer une soumission de test
        submission = FormSubmission(
            user_id='1767522312539',  # ID de test (format timestamp)
            form_type='devis_cecb',
            form_data=test_data,
            certificate_type=test_data.get('type_certificat', ''),
            client_name=f"{test_data.get('prenom', '')} {test_data.get('nom', '')}".strip(),
            building_address=test_data.get('adresse_batiment', ''),
            status='submitted'
        )

        # Sauvegarder dans la base de données
        try:
            db.session.add(submission)
            db.session.commit()
            print("✅ Soumission créée avec succès!")
            print(f"   ID: {submission.id}")
            print(f"   Utilisateur: {submission.user_id}")
            print(f"   Client: {submission.client_name}")
            print(f"   Type: {submission.certificate_type}")
            print(f"   Statut: {submission.status}")
        except Exception as e:
            print(f"❌ Erreur lors de la création: {str(e)}")
            db.session.rollback()
            return False

        # Vérifier la sauvegarde
        try:
            saved = FormSubmission.query.filter_by(id=submission.id).first()
            assert saved is not None, "La soumission n'a pas été trouvée dans la base de données"
            assert saved.form_data['prenom'] == 'Jean', "Les données du formulaire ne correspondent pas"
            assert saved.client_name == 'Jean Dupont', "Le nom du client ne correspond pas"
            assert saved.status == 'submitted', "Le statut ne correspond pas"
            print("\n✅ Vérification réussie!")
            print(f"   Données retrouvées: {saved.form_data}")
        except AssertionError as e:
            print(f"❌ Échec de la vérification: {str(e)}")
            return False

        # Tester la mise à jour du statut (simulation de création Bexio)
        try:
            saved.status = 'quote_created'
            saved.bexio_quote_id = '12345'
            saved.bexio_document_nr = 'A-0123'
            db.session.commit()
            print("\n✅ Mise à jour du statut réussie!")
            print(f"   Nouveau statut: {saved.status}")
            print(f"   ID Bexio: {saved.bexio_quote_id}")
            print(f"   Numéro de document: {saved.bexio_document_nr}")
        except Exception as e:
            print(f"❌ Erreur lors de la mise à jour: {str(e)}")
            db.session.rollback()
            return False

        # Lister toutes les soumissions
        try:
            all_submissions = FormSubmission.query.all()
            print(f"\n📊 Total de soumissions dans la base: {len(all_submissions)}")
            for sub in all_submissions:
                print(f"   - ID {sub.id}: {sub.client_name} ({sub.status})")
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture: {str(e)}")

        print("\n" + "=" * 60)
        print("✅ Test réussi!")
        print("=" * 60)
        return True


def test_parsing_functions():
    """Test des fonctions de parsing des sorties du script"""
    from app import extract_quote_id_from_output, extract_document_nr_from_output

    print("\n" + "=" * 60)
    print("🧪 Test des fonctions de parsing")
    print("=" * 60)

    # Simuler la sortie du script
    sample_output = """
INFO:__main__:✅ Offre créée avec succès !
INFO:__main__:   ID: 12345
INFO:__main__:   Numéro: A-0123
INFO:__main__:   Titre: CECB - Route de l'Hôpital 16b, 1180 Rolle
    """

    quote_id = extract_quote_id_from_output(sample_output)
    document_nr = extract_document_nr_from_output(sample_output)

    print(f"Sortie du script simulée:\n{sample_output}")
    print(f"\n✅ ID du devis extrait: {quote_id}")
    print(f"✅ Numéro de document extrait: {document_nr}")

    assert quote_id == '12345', f"ID attendu: 12345, obtenu: {quote_id}"
    assert document_nr == 'A-0123', f"Numéro attendu: A-0123, obtenu: {document_nr}"

    print("\n✅ Test de parsing réussi!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    print("\n🚀 Lancement des tests de Phase 1\n")

    # Test 1: Création de soumission
    if not test_submission_creation():
        print("\n❌ Échec du test de création")
        exit(1)

    # Test 2: Fonctions de parsing
    if not test_parsing_functions():
        print("\n❌ Échec du test de parsing")
        exit(1)

    print("\n🎉 Tous les tests sont réussis!")
    print("✅ Phase 1 implémentée avec succès!\n")
