from flask import Blueprint, render_template
from flask import jsonify
from flask import request, flash, redirect, url_for
from sqlalchemy import func
from flask_login import login_required, current_user
from functools import wraps
from models import db

from models.user import User
from models.application import Application
from models.history import History

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Decorador para permitir solo administradores
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return "Acceso denegado", 403
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():

    total_users = User.query.count()
    total_apps = Application.query.count()
    total_history = History.query.count()
    total_favorites = Application.query.filter_by(favorito=True).count()

    users = (
    User.query
    .order_by(User.fecha_registro.desc())
    .limit(5)
    .all()
)
    
    
    return render_template(
    "admin/dashboard.html",
    total_users=total_users,
    total_apps=total_apps,
    total_history=total_history,
    total_favorites=total_favorites,
    users=users
)
@admin_bp.route("/users")
@admin_required
def users():

    users = User.query.order_by(User.nombre).all()

    return render_template(
        "admin/users.html",
        users=users
    )
@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    

    user = User.query.get_or_404(user_id)

    if request.method == "POST":

        user.nombre = request.form["nombre"]
        user.correo = request.form["correo"]
        user.rol = request.form["rol"]

        db.session.commit()

        flash("Usuario actualizado correctamente.", "success")

        return redirect(url_for("admin.users"))

    return render_template(
        "admin/edit_user.html",
        user=user
    
    )

@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    # Evitar que el administrador se elimine a sí mismo
    if user.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta.", "danger")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()

    flash("Usuario eliminado correctamente.", "success")

    return redirect(url_for("admin.users"))

@admin_bp.route("/api/categories")
@login_required
@admin_required
def categories_chart():

    data = (
        db.session.query(
            Application.categoria,
            func.count(Application.id)
        )
        .group_by(Application.categoria)
        .all()
    )

    labels = [x[0] for x in data]
    values = [x[1] for x in data]

    return jsonify({
        "labels": labels,
        "values": values
    })