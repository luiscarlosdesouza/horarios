import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-this')
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'instance', 'horarios.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # USP Senha Unica
    USP_CLIENT_KEY = os.environ.get('USP_CLIENT_KEY')
    USP_CLIENT_SECRET = os.environ.get('USP_CLIENT_SECRET')
    USP_CALLBACK_ID = os.environ.get('USP_CALLBACK_ID')
    
    # Admin User
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'luiscarlosdesouza@gmail.com'

    # Email Config
    EMAIL_USER = os.environ.get('EMAIL_USER')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    EMAIL_SMTP_SERVER = os.environ.get('EMAIL_SMTP_SERVER')
    EMAIL_SMTP_PORT = int(os.environ.get('EMAIL_SMTP_PORT') or 587)
    EMAIL_TO = os.environ.get('EMAIL_TO')

