from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db
from models.application import Application
from models.history import History

dashboard_bp = Blueprint('dashboard', __name__)


def _app_query():
    """Admin ve todas las apps del sistema, user solo las suyas."""
    if current_user.is_admin:
        return Application.query
    return Application.query.filter_by(user_id=current_user.id)


def _history_query():
    """Historial siempre es personal."""
    return History.query.filter_by(user_id=current_user.id)


@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():

    # ── Stats ──────────────────────────────────────────────────────────────
    total_apps    = _app_query().count()

    # filter_by no funciona encadenado sobre una query con whereclause dinámica
    # → usar filter() con la columna explícita
    total_favs    = _app_query().filter(Application.favorito == True).count()
    total_accesos = _history_query().count()

    # Categorías distintas: construir el subquery manualmente según rol
    if current_user.is_admin:
        total_cats = db.session.query(
            func.count(func.distinct(Application.categoria))
        ).scalar() or 0
    else:
        total_cats = db.session.query(
            func.count(func.distinct(Application.categoria))
        ).filter(Application.user_id == current_user.id).scalar() or 0

    # ── Recientes (siempre personales) ─────────────────────────────────────
    recent_history = (
        _history_query()
        .order_by(History.fecha_acceso.desc())
        .limit(20).all()
    )
    seen, recent_apps = set(), []
    for h in recent_history:
        if h.application_id not in seen:
            seen.add(h.application_id)
            recent_apps.append(h.application)
            if len(recent_apps) >= 5:
                break

    # ── Última app abierta ─────────────────────────────────────────────────
    last_entry  = _history_query().order_by(History.fecha_acceso.desc()).first()
    last_app    = last_entry.application  if last_entry else None
    last_access = last_entry.fecha_acceso if last_entry else None

    # ── Quick apps para el grid ────────────────────────────────────────────
    if current_user.is_admin:
        quick_apps = (
        Application.query
        .order_by(
            Application.favorito.desc(),
            Application.nombre.asc()
        )
        .limit(8)
        .all()
    )
    else:
        quick_apps = (
        Application.query
        .filter(Application.user_id == current_user.id)
        .order_by(
            Application.favorito.desc(),
            Application.nombre.asc()
        )
        .limit(8)
        .all()
    )

    return render_template(
        'dashboard/index.html',
        total_apps=total_apps,
        total_favs=total_favs,
        total_cats=total_cats,
        total_accesos=total_accesos,
        recent_apps=recent_apps,
        last_app=last_app,
        last_access=last_access,
        quick_apps=quick_apps,
    )


# ── API: actividad semanal ─────────────────────────────────────────────────
@dashboard_bp.route('/api/stats/weekly')
@login_required
def api_weekly():
    labels, data = [], []
    today = datetime.utcnow().date()
    for i in range(6, -1, -1):
        dia    = today - timedelta(days=i)
        inicio = datetime.combine(dia, datetime.min.time())
        fin    = datetime.combine(dia, datetime.max.time())
        count  = _history_query().filter(
            History.fecha_acceso >= inicio,
            History.fecha_acceso <= fin,
        ).count()
        labels.append(dia.strftime('%a'))
        data.append(count)
    return jsonify(labels=labels, data=data)


# ── API: apps por categoría ────────────────────────────────────────────────
@dashboard_bp.route('/api/stats/categories')
@login_required
def api_categories():

    query = db.session.query(
        Application.categoria,
        func.count(Application.id)
    )

    if not current_user.is_admin:
        query = query.filter(
            Application.user_id == current_user.id
        )

    rows = (
        query
        .group_by(Application.categoria)
        .all()
    )

    return jsonify([
        {
            "categoria": r[0],
            "total": r[1]
        }
        for r in rows
    ])


