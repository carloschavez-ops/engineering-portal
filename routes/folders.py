from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db
from models.folder import Folder
from models.application import Application

folders_bp = Blueprint(
    "folders",
    __name__,
    url_prefix="/folders"
)


@folders_bp.route("/")
@login_required
def list_folders():
    if current_user.is_admin:
        # Carpetas A-Z por nombre
        folders = Folder.query.order_by(func.lower(Folder.nombre)).all()
    else:
        folders = Folder.query.filter_by(
            user_id=current_user.id
        ).order_by(func.lower(Folder.nombre)).all()

    return render_template("folders/list.html", folders=folders)


@folders_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_folder():
    if request.method == "POST":
        folder = Folder(
            user_id=current_user.id,
            nombre=request.form["nombre"],
            categoria=request.form.get("categoria", "General"),
            descripcion=request.form.get("descripcion", "")
        )
        db.session.add(folder)
        db.session.commit()
        flash("Carpeta creada correctamente", "success")
        return redirect(url_for("folders.list_folders"))

    return render_template("folders/form.html")


@folders_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_folder(id):
    folder = Folder.query.get_or_404(id)

    if not current_user.is_admin and folder.user_id != current_user.id:
        return "Acceso denegado", 403

    if request.method == "POST":
        folder.nombre = request.form["nombre"]
        folder.categoria = request.form.get("categoria", "")
        folder.descripcion = request.form.get("descripcion", "")
        db.session.commit()
        flash("Carpeta actualizada correctamente", "success")
        return redirect(url_for('folders.list_folders'))

    return render_template('folders/form.html', folder=folder)


@folders_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_folder(id):
    folder = Folder.query.get_or_404(id)

    if not current_user.is_admin and folder.user_id != current_user.id:
        return "Acceso denegado", 403

    db.session.delete(folder)
    db.session.commit()
    flash("Carpeta eliminada correctamente", "success")
    return redirect(url_for('folders.list_folders'))


@folders_bp.route('/<int:id>')
@login_required
def detail(id):
    folder = Folder.query.get_or_404(id)

    if not current_user.is_admin and folder.user_id != current_user.id:
        return "Acceso denegado", 403

    # Apps dentro de la carpeta A-Z
    apps = folder.applications.order_by(func.lower(Application.nombre)).all()

    return render_template(
        'folders/detail.html',
        folder=folder,
        apps=apps
    )