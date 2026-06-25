from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db
 
 
class User(UserMixin, db.Model):
    __tablename__ = 'users'
 
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    foto = db.Column(db.String(200), default='default_avatar.png')
    bio = db.Column(db.String(300), default='')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
 
    # Relationships
    applications = db.relationship('Application', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    history = db.relationship('History', backref='user', lazy='dynamic', cascade='all, delete-orphan')
 
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
 
    def __repr__(self):
        return f'<User {self.correo}>'
 