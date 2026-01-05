"""
Script pour corriger les données des soumissions existantes

Corrige :
1. Le nom du client (société vs personne)
2. L'adresse du bâtiment
"""

from app import app, db
from models import FormSubmission

print("=" * 60)
print("🔧 Correction des soumissions existantes")
print("=" * 60)

with app.app_context():
    submissions = FormSubmission.query.all()

    print(f"\n📊 {len(submissions)} soumission(s) trouvée(s)\n")

    corrected = 0

    for sub in submissions:
        form_data = sub.form_data
        updated = False

        # Correction 1 : Nom du client
        old_client_name = sub.client_name
        if form_data.get('type_contact') == 'societe':
            new_client_name = form_data.get('nom_entreprise', '') or form_data.get('nom_societe', '')
        else:
            prenom = form_data.get('prenom', '')
            nom = form_data.get('nom', '') or form_data.get('nom_famille', '')
            new_client_name = f"{prenom} {nom}".strip()

        if new_client_name and new_client_name != old_client_name:
            sub.client_name = new_client_name
            print(f"✅ Soumission #{sub.id}")
            print(f"   Client: '{old_client_name}' -> '{new_client_name}'")
            updated = True

        # Correction 2 : Adresse du bâtiment
        old_address = sub.building_address
        new_address = (
            form_data.get('adresse_batiment') or
            form_data.get('rue_batiment') or
            ''
        )

        if new_address and new_address != old_address:
            sub.building_address = new_address
            old_display = old_address or "(vide)"
            print(f"   Adresse: '{old_display}' -> '{new_address}'")
            updated = True

        if updated:
            corrected += 1
            print()

    # Sauvegarder toutes les modifications
    if corrected > 0:
        db.session.commit()
        print(f"✅ {corrected} soumission(s) corrigée(s)")
    else:
        print("ℹ️  Aucune correction nécessaire")

    print("\n" + "=" * 60)
    print("Résumé après correction :")
    print("=" * 60)

    for sub in FormSubmission.query.all():
        print(f"#{sub.id:2d} | {sub.client_name:30s} | {sub.building_address or '(vide)'}")
