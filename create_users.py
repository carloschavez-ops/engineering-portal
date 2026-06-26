"""
Script para crear usuarios iniciales en la BD.
Uso: python create_users.py

- Agrega la columna 'rol' a la tabla users si no existe
- Crea los usuarios definidos abajo (omite los que ya existen)
"""

from app import create_app
from models import db
from models.user import User
from sqlalchemy import text

# ══════════════════════════════════════════
#  DEFINE AQUÍ TUS USUARIOS
# ══════════════════════════════════════════
USUARIOS = [
    {
        'nombre':   'Administrador Polyline',
        'correo':   'admin@polyline.com',
        'password': 'Admin2024*',
        'rol':      'admin',
    },
    {
        'nombre':   'Usuario Demo',
        'correo':   'usuario@polyline.com',
        'password': 'User2024*',
        'rol':      'user',
    },
]
# ══════════════════════════════════════════


def agregar_columna_rol(session):
    """Agrega la columna 'rol' si no existe. Si ya existe, lo ignora."""
    try:
        session.execute(text(
            "ALTER TABLE users ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'user'"
        ))
        session.commit()
        print("  ✓  Columna 'rol' agregada a la tabla users.")
    except Exception as e:
        session.rollback()
        if '1060' in str(e) or 'Duplicate column' in str(e):
            print("  ℹ  Columna 'rol' ya existe — OK.")
        else:
            print(f"  ⚠  Error al agregar columna 'rol': {e}")


def main():
    app = create_app()
    with app.app_context():
        # 1. Crear tablas si no existen
        db.create_all()

        # 2. Asegurar que la columna 'rol' existe en users
        agregar_columna_rol(db.session)

        # 3. Crear usuarios
        creados  = 0
        omitidos = 0

        for data in USUARIOS:
            existe = User.query.filter_by(correo=data['correo']).first()
            if existe:
                # Actualizar rol por si acaso
                existe.rol = data['rol']
                db.session.commit()
                print(f"  ⚠  Ya existe: {data['correo']}  → rol actualizado a '{data['rol']}'")
                omitidos += 1
                continue

            u = User(
                nombre=data['nombre'],
                correo=data['correo'],
                rol=data['rol'],
            )
            u.set_password(data['password'])
            db.session.add(u)
            creados += 1
            print(f"  ✓  Creado [{data['rol']:5}]: {data['correo']}  /  {data['password']}")

        db.session.commit()
        print(f"\n  Resultado: {creados} creado(s), {omitidos} omitido(s).")
        print("\n  Credenciales para iniciar sesión:")
        for u in USUARIOS:
            print(f"    [{u['rol']:5}] {u['correo']}  /  {u['password']}")


if __name__ == '__main__':
    main()