"""
Modèles de base de données pour Script Runner

Ce module définit les modèles SQLAlchemy pour la persistance des données.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Instance SQLAlchemy à partager avec app.py
db = SQLAlchemy()


def get_local_time():
    """
    Retourne l'heure actuelle en timezone Suisse (Europe/Zurich)
    UTC+1 en hiver, UTC+2 en été
    """
    # Pour simplifier, on utilise UTC+1 (heure de Suisse en hiver)
    # En production, utiliser pytz pour gérer correctement les fuseaux horaires
    from datetime import timedelta
    return datetime.now(timezone.utc) + timedelta(hours=1)


class FormSubmission(db.Model):
    """Modèle pour sauvegarder les soumissions de formulaires CECB"""

    __tablename__ = 'form_submissions'

    # Identifiant unique
    id = db.Column(db.Integer, primary_key=True)

    # Référence utilisateur (ID string depuis users.json)
    user_id = db.Column(db.String(50), nullable=False, index=True)

    # Type de formulaire
    form_type = db.Column(db.String(50), nullable=False, default='devis_cecb')

    # Données complètes du formulaire (JSON)
    form_data = db.Column(db.JSON, nullable=False)

    # Données Bexio
    bexio_quote_id = db.Column(db.String(50), nullable=True)
    bexio_document_nr = db.Column(db.String(50), nullable=True)

    # Statut et erreurs
    status = db.Column(db.String(20), default='submitted')  # submitted, quote_created, error
    error_message = db.Column(db.Text, nullable=True)

    # Métadonnées pour recherche
    name = db.Column(db.String(100), nullable=True)
    certificate_type = db.Column(db.String(50), nullable=True)
    client_name = db.Column(db.String(200), nullable=True)
    building_address = db.Column(db.String(300), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=get_local_time, index=True)
    updated_at = db.Column(db.DateTime, default=get_local_time, onupdate=get_local_time)

    def __repr__(self):
        return f'<FormSubmission {self.id} - {self.client_name} - {self.status}>'

    def to_dict(self):
        """Convertit la soumission en dictionnaire pour API"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'form_type': self.form_type,
            'form_data': self.form_data,
            'bexio_quote_id': self.bexio_quote_id,
            'bexio_document_nr': self.bexio_document_nr,
            'status': self.status,
            'error_message': self.error_message,
            'name': self.name,
            'certificate_type': self.certificate_type,
            'client_name': self.client_name,
            'building_address': self.building_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
