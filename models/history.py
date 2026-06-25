from datetime import datetime
from models import db


class History(db.Model):
    __tablename__ = 'history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    fecha_acceso = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<History user={self.user_id} app={self.application_id}>'

