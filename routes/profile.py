from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import User
 
profile_bp = Blueprint('profile', __name__)
 
 
@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        bio = request.form.get('bio', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
 
        if not nombre:
            flash('El nombre no puede estar vacío.', 'danger')
            return redirect(url_for('profile.profile'))
 
        current_user.nombre = nombre
        current_user.bio = bio
 
        if new_password:
            if not current_user.check_password(current_password):
                flash('La contraseña actual es incorrecta.', 'danger')
                return redirect(url_for('profile.profile'))
            if len(new_password) < 6:
                flash('La nueva contraseña debe tener al menos 6 caracteres.', 'danger')
                return redirect(url_for('profile.profile'))
            if new_password != confirm_password:
                flash('Las contraseñas no coinciden.', 'danger')
                return redirect(url_for('profile.profile'))
            current_user.set_password(new_password)
 
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('profile.profile'))
 
    return render_template('profile/profile.html')