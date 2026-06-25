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
    # Evita que al llegar a /login aparezca un mensaje fijo.
    # El mensaje de “inicia sesión” se mostrará solo cuando realmente falte sesión.
    login_manager.login_message = ''
    login_manager.login_message_category = 'warning'

 
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
 
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.apps import apps_bp
    from routes.profile import profile_bp
    from routes.stats import stats_bp
 
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(apps_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(stats_bp)
 
    # Create tables
    with app.app_context():
        db.create_all()
 
    return app


app = create_app()


# Para desarrollo: permite que la sesión funcione en HTTP sin Secure cookies.
# (Evita que Flask-Login no persista sesión.)
app.config.setdefault('SESSION_COOKIE_SECURE', False)
app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')

if __name__ == "__main__":
    app.run()

 