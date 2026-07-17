from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.application import Application, CATEGORIAS, ESTADOS
from models.history import History
from models.favorite import Favorite
from models.folder import Folder
from sqlalchemy import func

apps_bp = Blueprint('apps', __name__)

ICONOS = ['grid', 'code', 'cpu', 'bar-chart-2', 'calculator', 'layers', 'tool', 'globe',
          'zap', 'database', 'file-text', 'settings', 'activity', 'box', 'terminal']

COLORES = ['#23486A', '#2D9E6B', '#D43B3B', '#C8923A', '#2E5A84',
           '#4A7FA5', '#D9C6A3', '#5B8DB8', '#7BAFD4', '#8FA8BE']


def _app_query():
    """Todos los usuarios pueden ver todas las aplicaciones."""
    return Application.query

def _get_app(app_id):
    """Cualquier usuario puede acceder a la aplicación para abrirla."""
    return Application.query.get_or_404(app_id)

def _get_owned_app_or_404(app_id):
    """Solo el dueño o el administrador pueden modificar una aplicación."""
    if current_user.is_admin:
        return Application.query.get_or_404(app_id)

    return Application.query.filter_by(
        id=app_id,
        user_id=current_user.id
    ).first_or_404()


# ── Listados ───────────────────────────────────────────────────────────────

@apps_bp.route('/apps')
@login_required
def list_apps():
    categoria = request.args.get('categoria', '')
    orden = request.args.get('orden', 'recientes')

    query = _app_query()

    if categoria:
        query = query.filter(Application.categoria == categoria)

    if orden == 'nombre':
        apps = query.order_by(func.lower(Application.nombre)).all()
    else:
        apps = query.order_by(Application.fecha_creacion.desc()).all()

    return render_template(
        'apps/list.html',
        apps=apps,
        categorias=CATEGORIAS,
        selected_cat=categoria,
        titulo='Todas las Aplicaciones',
        orden=orden
    )

@apps_bp.route('/apps/favorites')
@login_required
def favorites():

    apps = (
        Application.query
        .join(Favorite)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Application.nombre)
        .all()
    )

    return render_template(
        "apps/list.html",
        apps=apps,
        categorias=CATEGORIAS,
        selected_cat='',
        titulo="Aplicaciones Favoritas"
    )


@apps_bp.route('/apps/recent')
@login_required
def recent():

    orden = request.args.get('orden', 'recientes')

    history = (
        History.query
        .filter_by(user_id=current_user.id)
        .order_by(History.fecha_acceso.desc())
        .all()
    )

    seen = set()
    apps = []

    for h in history:
        if h.application_id not in seen:
            seen.add(h.application_id)
            apps.append(h.application)

    if orden == "nombre":
        apps.sort(key=lambda x: x.nombre.lower())

    return render_template(
        'apps/list.html',
        apps=apps,
        categorias=CATEGORIAS,
        selected_cat='',
        titulo='Aplicaciones Recientes',
        orden=orden
    )


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
    app = _get_owned_app_or_404(app_id)

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
            #app.favorito    = favorito
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
    app = _get_owned_app_or_404(app_id)
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

    favorito = Favorite.query.filter_by(
        user_id=current_user.id,
        application_id=app_id
    ).first()

    if favorito:
        db.session.delete(favorito)
        favorito_activo = False
    else:
        favorito = Favorite(
            user_id=current_user.id,
            application_id=app_id
        )
        db.session.add(favorito)
        favorito_activo = True

    db.session.commit()

    return jsonify({
        "favorito": favorito_activo
    })

# ── Agregar a carpeta ─────────────────────────────────────────────

@apps_bp.route('/apps/<int:app_id>/add-folder', methods=['GET','POST'])
@login_required
def add_to_folder(app_id):

    app = _get_owned_app_or_404(app_id)


    if request.method == "POST":

        folder_id = request.form.get('folder_id')


        if folder_id:

            app.folder_id = folder_id

            db.session.commit()


            flash(
                f'Aplicación "{app.nombre}" agregada a la carpeta.',
                'success'
            )


            return redirect(
                url_for('apps.list_apps')
            )


    if current_user.is_admin:

        folders = Folder.query.all()

    else:

        folders = Folder.query.filter_by(
            user_id=current_user.id
        ).all()



    return render_template(
        'apps/add_folder.html',
        app=app,
        folders=folders
    )
@apps_bp.route('/apps/<int:app_id>/remove-folder', methods=['POST'])
@login_required
def remove_from_folder(app_id):

    app = _get_owned_app_or_404(app_id)

    app.folder_id = None

    db.session.commit()

    flash(
        f'La aplicación "{app.nombre}" fue quitada de la carpeta.',
        'success'
    )

    return redirect(request.referrer or url_for('folders.list_folders'))

# ── Abrir ──────────────────────────────────────────────────────────────────

@apps_bp.route('/apps/<int:app_id>/open')
@login_required
def open_app(app_id):
    app = _get_app(app_id)
    if app.estado == 'fuera':
        flash(f'"{app.nombre}" está fuera de servicio.', 'danger')
        return redirect(url_for('apps.list_apps'))
    entry = History(user_id=current_user.id, application_id=app_id)
    db.session.add(entry)
    db.session.commit()
    return redirect(app.url)
