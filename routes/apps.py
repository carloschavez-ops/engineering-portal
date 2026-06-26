from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.application import Application, CATEGORIAS, ESTADOS
from models.history import History

apps_bp = Blueprint('apps', __name__)

ICONOS = ['grid', 'code', 'cpu', 'bar-chart-2', 'calculator', 'layers', 'tool', 'globe',
          'zap', 'database', 'file-text', 'settings', 'activity', 'box', 'terminal']

COLORES = ['#23486A', '#2D9E6B', '#D43B3B', '#C8923A', '#2E5A84',
           '#4A7FA5', '#D9C6A3', '#5B8DB8', '#7BAFD4', '#8FA8BE']


def _app_query():
    """Admin ve todas las apps; usuario normal solo las suyas."""
    if current_user.is_admin:
        return Application.query
    return Application.query.filter_by(user_id=current_user.id)


def _get_app_or_404(app_id):
    """Obtiene una app por id respetando el rol: admin puede acceder a cualquiera."""
    if current_user.is_admin:
        return Application.query.get_or_404(app_id)
    return Application.query.filter_by(id=app_id, user_id=current_user.id).first_or_404()


# ── Listados ───────────────────────────────────────────────────────────────

@apps_bp.route('/apps')
@login_required
def list_apps():
    categoria = request.args.get('categoria', '')
    query = _app_query()
    if categoria:
        query = query.filter(Application.categoria == categoria)
    apps = query.order_by(Application.fecha_creacion.desc()).all()
    return render_template('apps/list.html', apps=apps, categorias=CATEGORIAS,
                           selected_cat=categoria, titulo='Todas las Aplicaciones')


@apps_bp.route('/apps/favorites')
@login_required
def favorites():
    apps = _app_query().filter(Application.favorito == True)\
                       .order_by(Application.nombre).all()
    return render_template('apps/list.html', apps=apps, categorias=CATEGORIAS,
                           selected_cat='', titulo='Aplicaciones Favoritas')


@apps_bp.route('/apps/recent')
@login_required
def recent():
    history = (
        History.query
        .filter_by(user_id=current_user.id)
        .order_by(History.fecha_acceso.desc())
        .limit(50).all()
    )
    seen, apps = set(), []
    for h in history:
        if h.application_id not in seen:
            seen.add(h.application_id)
            apps.append(h.application)
            if len(apps) >= 20:
                break
    return render_template('apps/list.html', apps=apps, categorias=CATEGORIAS,
                           selected_cat='', titulo='Aplicaciones Recientes')


# ── Crear ──────────────────────────────────────────────────────────────────

@apps_bp.route('/apps/new', methods=['GET', 'POST'])
@login_required
def new_app():
    if request.method == 'POST':
        nombre      = request.form.get('nombre', '').strip()
        url         = request.form.get('url', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria   = request.form.get('categoria', 'Otros')
        icono       = request.form.get('icono', 'grid')
        color       = request.form.get('color', '#23486A')
        favorito    = request.form.get('favorito') == 'on'
        estado      = request.form.get('estado', 'disponible')

        if estado not in [e[0] for e in ESTADOS]:
            estado = 'disponible'

        if not nombre or not url:
            flash('El nombre y la URL son obligatorios.', 'danger')
        else:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            app = Application(
                user_id=current_user.id,
                nombre=nombre, url=url,
                descripcion=descripcion, categoria=categoria,
                icono=icono, color=color,
                favorito=favorito, estado=estado,
            )
            db.session.add(app)
            db.session.commit()
            db.session.expire(current_user)
            flash(f'Aplicación "{nombre}" creada exitosamente.', 'success')
            return redirect(url_for('apps.list_apps'))

    return render_template('apps/form.html', app=None, categorias=CATEGORIAS,
                           iconos=ICONOS, colores=COLORES, estados=ESTADOS,
                           titulo='Nueva Aplicación')


# ── Editar ─────────────────────────────────────────────────────────────────

@apps_bp.route('/apps/<int:app_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_app(app_id):
    app = _get_app_or_404(app_id)

    if request.method == 'POST':
        nombre      = request.form.get('nombre', '').strip()
        url         = request.form.get('url', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        categoria   = request.form.get('categoria', 'Otros')
        icono       = request.form.get('icono', 'grid')
        color       = request.form.get('color', '#23486A')
        favorito    = request.form.get('favorito') == 'on'
        estado      = request.form.get('estado', 'disponible')

        if estado not in [e[0] for e in ESTADOS]:
            estado = 'disponible'

        if not nombre or not url:
            flash('El nombre y la URL son obligatorios.', 'danger')
        else:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            app.nombre      = nombre
            app.url         = url
            app.descripcion = descripcion
            app.categoria   = categoria
            app.icono       = icono
            app.color       = color
            app.favorito    = favorito
            app.estado      = estado
            db.session.commit()
            flash('Aplicación actualizada correctamente.', 'success')
            return redirect(url_for('apps.list_apps'))

    return render_template('apps/form.html', app=app, categorias=CATEGORIAS,
                           iconos=ICONOS, colores=COLORES, estados=ESTADOS,
                           titulo='Editar Aplicación')


# ── Eliminar ───────────────────────────────────────────────────────────────

@apps_bp.route('/apps/<int:app_id>/delete', methods=['POST'])
@login_required
def delete_app(app_id):
    app = _get_app_or_404(app_id)
    nombre = app.nombre
    db.session.delete(app)
    db.session.commit()
    db.session.expire(current_user)
    flash(f'Aplicación "{nombre}" eliminada.', 'warning')
    return redirect(url_for('apps.list_apps'))


# ── Favorito ───────────────────────────────────────────────────────────────

@apps_bp.route('/apps/<int:app_id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite(app_id):
    app = _get_app_or_404(app_id)
    app.favorito = not app.favorito
    db.session.commit()
    return jsonify({'favorito': app.favorito})


# ── Abrir ──────────────────────────────────────────────────────────────────

@apps_bp.route('/apps/<int:app_id>/open')
@login_required
def open_app(app_id):
    app = _get_app_or_404(app_id)
    if app.estado == 'fuera':
        flash(f'"{app.nombre}" está fuera de servicio.', 'danger')
        return redirect(url_for('apps.list_apps'))
    entry = History(user_id=current_user.id, application_id=app_id)
    db.session.add(entry)
    db.session.commit()
    return redirect(app.url)
