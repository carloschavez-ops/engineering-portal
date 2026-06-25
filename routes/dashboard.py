from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db
from models.application import Application
from models.history import History
 
dashboard_bp = Blueprint('dashboard', __name__)
 
 
@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Stats
    total_apps = Application.query.filter_by(user_id=current_user.id).count()
    total_favs = Application.query.filter_by(user_id=current_user.id, favorito=True).count()
 
    # Recent apps (last 5 distinct)
    recent_history = (
        db.session.query(History)
        .filter_by(user_id=current_user.id)
        .order_by(History.fecha_acceso.desc())
        .limit(20)
        .all()
    )
    seen = set()
    recent_apps = []
    for h in recent_history:
        if h.application_id not in seen:
            seen.add(h.application_id)
            recent_apps.append(h.application)
            if len(recent_apps) >= 5:
                break
 
    # Last used app
    last_entry = (
        History.query
        .filter_by(user_id=current_user.id)
        .order_by(History.fecha_acceso.desc())
        .first()
    )
    last_app = last_entry.application if last_entry else None
    last_access = last_entry.fecha_acceso if last_entry else None
 
    # Categories count
    cats = (
        db.session.query(Application.categoria, func.count(Application.id))
        .filter_by(user_id=current_user.id)
        .group_by(Application.categoria)
        .all()
    )
    total_cats = len(cats)
 
    # Total accesses
    total_accesos = History.query.filter_by(user_id=current_user.id).count()
 
    return render_template(
        'dashboard/index.html',
        total_apps=total_apps,
        total_favs=total_favs,
        total_cats=total_cats,
        total_accesos=total_accesos,
        recent_apps=recent_apps,
        last_app=last_app,
        last_access=last_access,
    )
 
 
@dashboard_bp.route('/api/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
 
    apps = Application.query.filter(
        Application.user_id == current_user.id,
        (Application.nombre.ilike(f'%{q}%') | Application.descripcion.ilike(f'%{q}%') | Application.categoria.ilike(f'%{q}%'))
    ).limit(8).all()
 
    results = [{
        'id': a.id,
        'nombre': a.nombre,
        'url': a.url,
        'categoria': a.categoria,
        'color': a.color,
        'icono': a.icono,
    } for a in apps]
 
    return jsonify(results)
 