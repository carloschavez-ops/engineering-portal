"""
Script de diagnóstico — ejecuta: python debug_login.py
Muestra exactamente qué hay en la BD para el correo admin.
"""
from app import create_app
from models import db
from sqlalchemy import text

CORREO   = 'admin@polyline.com'
PASSWORD = 'Admin2024*'

app = create_app()
with app.app_context():

    print("=" * 55)
    print("  DIAGNÓSTICO DE LOGIN")
    print("=" * 55)

    # 1. Verificar que la tabla existe y tiene la columna rol
    try:
        cols = db.session.execute(text("DESCRIBE users")).fetchall()
        print("\n📋 Columnas en tabla 'users':")
        for c in cols:
            print(f"   {c[0]:20} {c[1]}")
    except Exception as e:
        print(f"\n❌ Error al leer tabla users: {e}")

    # 2. Buscar el usuario por correo (raw SQL para evitar caché ORM)
    try:
        row = db.session.execute(
            text("SELECT id, nombre, correo, password_hash, rol FROM users WHERE correo = :c"),
            {'c': CORREO}
        ).fetchone()

        if not row:
            print(f"\n❌ No existe ningún usuario con correo: {CORREO}")
            print("   → Ejecuta: python create_users.py")
        else:
            print(f"\n✅ Usuario encontrado:")
            print(f"   id            : {row[0]}")
            print(f"   nombre        : {row[1]}")
            print(f"   correo        : {row[2]}")
            print(f"   rol           : {row[4]}")
            print(f"   password_hash : {row[3][:40]}...")

            # 3. Verificar la contraseña
            from werkzeug.security import check_password_hash
            ok = check_password_hash(row[3], PASSWORD)
            print(f"\n🔑 ¿Contraseña '{PASSWORD}' es correcta? → {'✅ SÍ' if ok else '❌ NO'}")

            if not ok:
                print("\n   → La contraseña en BD no coincide.")
                print("   → Ejecuta: python create_users.py  (actualiza el hash)")

    except Exception as e:
        print(f"\n❌ Error al buscar usuario: {e}")

    print("\n" + "=" * 55)