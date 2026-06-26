from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

# Correos que pueden registrarse/entrar sin ser @gmail.com
CORREOS_ADMIN = {'admin@polyline.com'}


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        nombre   = request.form.get('nombre', '').strip()
        correo   = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        error = None
        if not nombre or not correo or not password:
            error = 'Todos los campos son obligatorios.'
        elif correo.endswith("@polyline.com") and correo not in CORREOS_ADMIN:
            error = "Solo el administrador puede usar un correo @polyline.com."
        elif len(password) < 6:
            error = 'La contraseña debe tener al menos 6 caracteres.'
        elif password != confirm:
            error = 'Las contraseñas no coinciden.'
        elif correo in CORREOS_ADMIN:
            error = 'Esta cuenta está reservada para el administrador del sistema.'
        elif User.query.filter_by(correo=correo).first():
            error = 'Ya existe una cuenta con ese correo electrónico.'

        if error:
            flash(error, 'danger')
        else:
            rol = 'user'
            user = User(nombre=nombre, correo=correo, rol=rol)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash('¡Cuenta creada exitosamente! Bienvenido al portal.', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'GET':
        return render_template('auth/login.html')

    correo   = request.form.get('correo', '').strip().lower()
    password = request.form.get('password', '')
    remember = request.form.get('remember') == 'on'

    try:
        user = User.query.filter_by(correo=correo).first()
    except Exception as e:
        # Columna 'rol' no existe aún en la BD → ejecutar python create_users.py
        if '1054' in str(e) or 'rol' in str(e).lower():
            flash(
                "Error de BD: la columna 'rol' no existe. "
                "Ejecuta: python create_users.py",
                'danger'
            )
        else:
            flash('Error de base de datos. Contacta al administrador.', 'danger')
        return render_template('auth/login.html')

    if user and user.check_password(password):
        login_user(user, remember=remember)
        next_page = request.form.get('next') or request.args.get('next')
        flash(f'¡Bienvenido de vuelta, {user.nombre}!', 'success')
        if next_page and isinstance(next_page, str) and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard.index'))
    else:
        flash('Correo o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('auth.login'))