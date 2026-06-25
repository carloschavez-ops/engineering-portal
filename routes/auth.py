from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
 
auth_bp = Blueprint('auth', __name__)
 
 
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
 
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
 
        error = None
        if not nombre or not correo or not password:
            error = 'Todos los campos son obligatorios.'
        elif len(password) < 6:
            error = 'La contraseña debe tener al menos 6 caracteres.'
        elif password != confirm:
            error = 'Las contraseñas no coinciden.'
        elif User.query.filter_by(correo=correo).first():
            error = 'Ya existe una cuenta con ese correo electrónico.'
 
        if error:
            flash(error, 'danger')
        else:
            user = User(nombre=nombre, correo=correo)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('¡Cuenta creada exitosamente! Bienvenido al portal.', 'success')
            return redirect(url_for('dashboard.index'))
 
    return render_template('auth/register.html')
 
 
@auth_bp.route('/login', methods=['GET', 'POST'])
# Nota: esta ruta evita depender del parámetro next para el flujo básico.

def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
 
    if request.method == 'GET':
        return render_template('auth/login.html')

 
    if request.method == 'POST':
        # No uses next del querystring para evitar bucles raros

        # (ej: /login?next=%2F que podría caer en una ruta protegida al no autenticar).
        correo = request.form.get('correo', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(correo=correo).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)

            # Prioriza next del POST (viene en input hidden). Fallback a querystring.

            next_page = request.form.get('next') or request.args.get('next')

            flash(f'¡Bienvenido de vuelta, {user.nombre}!', 'success')

            # Sanitiza next: solo rutas relativas internas.
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
 