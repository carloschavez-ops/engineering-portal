import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db
from models.user import User
from models.folder import Folder
from flask_migrate import Migrate
from sqlalchemy import inspect


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = ''
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ── Inyecta variables globales a todos los templates ──────────────────
    @app.context_processor 
    def inject_globals(): 
        from flask_login import current_user
        from models.application import Application 

        total_apps = 0
        total_folders = 0
        try:
            if current_user.is_authenticated:
                total_apps = Application.query.count()
                from models.folder import Folder
                total_folders = Folder.query.count()
        except Exception as e:
            print("Error contador sidebar:", e)
        return dict(
            total_apps_global=total_apps,
            total_folders_global=total_folders
            )
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.apps import apps_bp
    from routes.profile import profile_bp
    from routes.stats import stats_bp
    from routes.admin import admin_bp
    from routes.folders import folders_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(apps_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(folders_bp)
    

    # Create tables
    # Crear administrador solo si la tabla users ya existe
    # El administrador se creará después de ejecutar las migraciones
    pass


app = create_app()

app.config.setdefault('SESSION_COOKIE_SECURE', False)
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)