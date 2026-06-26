"""
Resetea la contraseña del admin directamente.
Uso: python reset_admin.py
"""
from app import create_app
from models import db
from models.user import User

CORREO       = 'admin@polyline.com'
NEW_PASSWORD = 'Admin2024*'

app = create_app()
with app.app_context():
    user = User.query.filter_by(correo=CORREO).first()
    if not user:
        print(f"❌ No existe usuario con correo: {CORREO}")
    else:
        user.set_password(NEW_PASSWORD)
        user.rol = 'admin'
        db.session.commit()
        print(f"✅ Contraseña actualizada para: {CORREO}")
        print(f"   Nueva contraseña : {NEW_PASSWORD}")
        print(f"   Rol              : {user.rol}")
        