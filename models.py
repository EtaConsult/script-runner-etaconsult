"""
Modèles de base de données pour Script Runner

Ce module définit les modèles SQLAlchemy pour la persistance des données.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instance SQLAlchemy à partager avec app.py
db = SQLAlchemy()


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
