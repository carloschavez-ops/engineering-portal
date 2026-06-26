import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = ''
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Inyecta variables globales a todos los templates ──────────────────
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from models.application import Application

        total = 0

        try:
            if current_user.is_authenticated:
                if current_user.is_admin:
                    # El administrador ve todas las aplicaciones
                    total = Application.query.count()
                else:
                    # El usuario normal solo ve sus aplicaciones
                    total = Application.query.filter_by(
                        user_id=current_user.id
                    ).count()
        except Exception:
            total = 0

        return dict(total_apps_global=total)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.apps import apps_bp
    from routes.profile import profile_bp
    from routes.stats import stats_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(apps_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(admin_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

app.config.setdefault('SESSION_COOKIE_SECURE', False)
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')

if __name__ == "__main__":
    app.run()