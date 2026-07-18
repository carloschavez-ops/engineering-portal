"""
Crea o resetea el administrador.
"""

from app import create_app
from models import db
from models.user import User

CORREO = 'admin@polyline.com'
NEW_PASSWORD = 'Admin2024*'

app = create_app()

with app.app_context():

    user = User.query.filter_by(correo=CORREO).first()

    if not user:
        user = User(
            nombre="Administrador Polyline",
            correo=CORREO,
            rol="admin",
            bio="Administrador del sistema"
        )

        user.set_password(NEW_PASSWORD)

        db.session.add(user)
        db.session.commit()

        print("✅ Administrador creado correctamente")

    else:
        user.set_password(NEW_PASSWORD)
        user.rol = "admin"
        db.session.commit()

        print("✅ Contraseña del administrador actualizada")

    print("----------------------------")
    print("Correo:", CORREO)
    print("Password:", NEW_PASSWORD)