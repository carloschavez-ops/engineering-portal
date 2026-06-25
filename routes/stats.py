from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from models import db
from models.application import Application
from models.history import History
 
stats_bp = Blueprint('stats', __name__)
 
 
@stats_bp.route('/stats')
@login_required
def stats():
    return render_template('stats/stats.html')
 
 
@stats_bp.route('/api/stats/overview')
@login_required
def overview():
    total_apps = Application.query.filter_by(user_id=current_user.id).count()
    total_favs = Application.query.filter_by(user_id=current_user.id, favorito=True).count()
    total_accesos = History.query.filter_by(user_id=current_user.id).count()
 
    cats = (
        db.session.query(Application.categoria, func.count(Application.id))
        .filter_by(user_id=current_user.id)
        .group_by(Application.categoria)
        .all()
    )
 
    return jsonify({
        'total_apps': total_apps,
        'total_favs': total_favs,
        'total_accesos': total_accesos,
        'total_cats': len(cats),
    })
 
 
@stats_bp.route('/api/stats/top-apps')
@login_required
def top_apps():
    results = (
        db.session.query(Application.nombre, Application.color, func.count(History.id).label('total'))
        .join(History, History.application_id == Application.id)
        .filter(Application.user_id == current_user.id)
        .group_by(Application.id)
        .order_by(func.count(History.id).desc())
        .limit(8)
        .all()
    )
    return jsonify([{'nombre': r.nombre, 'color': r.color, 'total': r.total} for r in results])
 
 
@stats_bp.route('/api/stats/weekly')
@login_required
def weekly():
    today = datetime.utcnow().date()
    labels = []
    data = []
 
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = History.query.filter(
            History.user_id == current_user.id,
            func.date(History.fecha_acceso) == day
        ).count()
        labels.append(day.strftime('%a'))
        data.append(count)
 
    return jsonify({'labels': labels, 'data': data})
 
 
@stats_bp.route('/api/stats/categories')
@login_required
def categories():
    results = (
        db.session.query(Application.categoria, func.count(Application.id))
        .filter_by(user_id=current_user.id)
        .group_by(Application.categoria)
        .all()
    )
    return jsonify([{'categoria': r[0], 'total': r[1]} for r in results])
 
 
@stats_bp.route('/history')
@login_required
def history():
    page = int(request.args.get('page', 1))
    per_page = 20
    
    from flask import request
    entries = (
        History.query
        .filter_by(user_id=current_user.id)
        .order_by(History.fecha_acceso.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    return render_template('stats/history.html', entries=entries)