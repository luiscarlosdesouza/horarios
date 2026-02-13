from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv(override=True)

app = create_app()

def create_admin():
    with app.app_context():
        # Get admin credentials from config or use defaults
        username = app.config.get('ADMIN_USERNAME') or os.environ.get('ADMIN_USERNAME') or 'admin'
        password = app.config.get('ADMIN_PASSWORD') or os.environ.get('ADMIN_PASSWORD') or 'Ec0l0g!@486642'
        email = app.config.get('ADMIN_EMAIL') or os.environ.get('ADMIN_EMAIL') or 'admin@ime.usp.br'

        print(f"DEBUG: Using ADMIN_USERNAME: {username}")
        print(f"DEBUG: Using ADMIN_PASSWORD: {'******' if password else 'None'}")
        
        print(f"Checking for admin user: {username}")
        
        user = User.query.filter_by(username=username).first()
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        if user:
            print(f"User {username} exists. Updating password (starts with {password[:3]}...) and role...")
            user.password_hash = hashed_password
            user.role = 'admin'
            if email:
                user.email = email
            models_action = "updated"
        else:
            print(f"User {username} does not exist. Creating new admin user...")
            user = User(
                username=username,
                password_hash=hashed_password,
                email=email,
                role='admin',
                name='Administrator',
                is_default_password=False
            )
            db.session.add(user)
            models_action = "created"
        
        try:
            db.session.commit()
            print(f"Admin user {username} successfully {models_action}.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating/updating admin user: {e}")

if __name__ == '__main__':
    create_admin()
