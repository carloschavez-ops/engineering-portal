import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    DATABASE_URL = os.environ.get('DATABASE_URL', '')
    
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace(
        'postgres://',
        'postgresql://',
        1
    )
        
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///portal.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    # Cookies para producción
    SESSION_COOKIE_SECURE = bool(DATABASE_URL)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'