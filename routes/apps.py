from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.application import Application, CATEGORIAS
from models.history import History

apps_bp = Blueprint('apps', __name__)

ICONOS = [
    'grid', 'code', 'cpu', 'bar-chart-2', 'calculator', 'layers', 'tool',
    'globe', 'zap', 'database', 'file-text', 'settings', 'activity',
    'box', 'terminal'
]

COLORES = [
    '#6C63FF', '#00D4AA', '#FF6B6B', '#4ECDC4', '#45B7D1',
    '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'
]


@apps_bp.route('/apps')
@login_required
def list_apps():
    categoria = request.args.get('categoria', '')
    query = Application.query.filter_by(user_id=current_user.id)

    if categoria:
        query = query.filter_by(categoria=categoria)

    apps = query.order_by(Application.fecha_creacion.desc()).all()

    return render_template(
        'apps/list.html',
        apps=apps,
        categorias=CATEGORIAS,
        selected_cat=categoria,
        titulo='Todas las Aplicaciones'
    )


@apps_bp.route('/apps/favorites')
@login_required
def favorites():
    apps = Application.query.filter_by(
        user_id=current_user.id,
        favorito=True
    ).order_by(Application.nombre).all()

    return render_template(
        'apps/list.html',
        apps=apps,
        categorias=CATEGORIAS,
        selected_cat='',
        titulo='Aplicaciones Favoritas'
    )


@apps_bp.route('/apps/recent')
@login_required
def recent():
    history = (
        History.query
        .filter_by(user_id=current_user.id)
        .order_by(History.fecha_acceso.desc())
        .limit(50)
        .all()
    )

    seen = set()
    apps = []

    for h in history:
        if h.application_id not in seen:
            seen.add(h.application_id)
            apps.append(h.application)
            if len(apps) >= 20:
                break

    return render_template(
        'apps/list.html',
        apps=apps,
        categorias=CATEGORIAS,
        selected_cat='',
        titulo='Aplicaciones Recientes'
    )


@apps_bp.route('/apps/new', methods=['GET', 'POST'])
@login_required
def new_app():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        url = request.form.get('url', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria = request.form.get('categoria', 'Otras')
        icono = request.form.get('icono', 'grid')
        color = request.form.get('color', '#6C63FF')
        favorito = request.form.get('favorito') == 'on'

        if not nombre or not url:
            flash('El nombre y la URL son obligatorios.', 'danger')
        else:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            new_app = Application(
                user_id=current_user.id,
                nombre=nombre,
                url=url,
                descripcion=descripcion,
                categoria=categoria,
                icono=icono,
                color=color,
                favorito=favorito,
            )

            db.session.add(new_app)
            db.session.commit()

            flash(f'Aplicación "{nombre}" creada exitosamente.', 'success')
            return redirect(url_for('apps.list_apps'))

    return render_template(
        'apps/form.html',
        app=None,
        categorias=CATEGORIAS,
        iconos=ICONOS,
        colores=COLORES,
        titulo='Nueva Aplicación'
    )


@apps_bp.route('/apps/<int:app_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_app(app_id):
    app = Application.query.filter_by(id=app_id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        app.nombre = request.form.get('nombre', '').strip()
        app.url = request.form.get('url', '').strip()
        app.descripcion = request.form.get('descripcion', '').strip()
        app.categoria = request.form.get('categoria', 'Otras')
        app.icono = request.form.get('icono', 'grid')
        app.color = request.form.get('color', '#6C63FF')
        app.favorito = request.form.get('favorito') == 'on'

        if not app.nombre or not app.url:
            flash('El nombre y la URL son obligatorios.', 'danger')
        else:
            if not app.url.startswith(('http://', 'https://')):
                app.url = 'https://' + app.url

            db.session.commit()
            flash('Aplicación actualizada correctamente.', 'success')
            return redirect(url_for('apps.list_apps'))

    return render_template(
        'apps/form.html',
        app=app,
        categorias=CATEGORIAS,
        iconos=ICONOS,
        colores=COLORES,
        titulo='Editar Aplicación'
    )


@apps_bp.route('/apps/<int:app_id>/delete', methods=['POST'])
@login_required
def delete_app(app_id):
    app = Application.query.filter_by(id=app_id, user_id=current_user.id).first_or_404()

    nombre = app.nombre
    db.session.delete(app)
    db.session.commit()

    flash(f'Aplicación "{nombre}" eliminada.', 'warning')
    return redirect(url_for('apps.list_apps'))


@apps_bp.route('/apps/<int:app_id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite(app_id):
    app = Application.query.filter_by(id=app_id, user_id=current_user.id).first_or_404()
    app.favorito = not app.favorito
    db.session.commit()

    return jsonify({'favorito': app.favorito})


@apps_bp.route('/apps/<int:app_id>/open')
@login_required
def open_app(app_id):
    app = Application.query.filter_by(id=app_id, user_id=current_user.id).first_or_404()

    entry = History(user_id=current_user.id, application_id=app_id)
    db.session.add(entry)
    db.session.commit()

    return redirect(app.url)