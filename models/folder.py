from datetime import datetime
from models import db


class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    categoria = db.Column(
        db.String(100),
        nullable=False,
        default='-'
    )

    descripcion = db.Column(
        db.Text,
        default=''
    )

    fecha_creacion = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # backref renombrado a 'parent_folder' para no chocar con folder_id de Application
    applications = db.relationship(
        'Application',
        backref='parent_folder',
        lazy='dynamic',
        foreign_keys='Application.folder_id'
    )

    def __repr__(self):
        return f'<Folder {self.nombre}>'