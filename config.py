# config.py
import os
from datetime import timedelta

# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Database configuration
DATABASE_PATH = os.path.join(basedir, 'instance', 'the_newel.db')
SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret key for session management
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-this-in-production'

# Security settings
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

# Application settings
APP_NAME = "The Newel"
APP_VERSION = "1.0.0"
DEBUG = True  # Set to False in production