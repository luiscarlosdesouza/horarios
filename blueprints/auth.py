from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager, oauth
from models import User
import secrets

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Update Name/Email
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        
        # Password Change
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password:
            if new_password != confirm_password:
                flash('Novas senhas não conferem.', 'danger')
                return redirect(url_for('auth.profile'))
            
            from werkzeug.security import generate_password_hash
            current_user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
            current_user.is_default_password = False
            flash('Senha alterada com sucesso!', 'success')
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('profile.html')

# --- USP Senha Unica OAuth 1.0a ---
@auth_bp.route('/login/usp')
def usp_login():
    redirect_uri = url_for('auth.usp_callback', _external=True)
    # Ensure USP_CALLBACK_ID is set in .env
    callback_id = current_app.config.get('USP_CALLBACK_ID')
    return oauth.usp.authorize_redirect(redirect_uri, callback_id=callback_id)

@auth_bp.route('/login/usp/callback')
def usp_callback():
    try:
        token = oauth.usp.authorize_access_token()
        resp = oauth.usp.post('usuariousp', token=token)
        user_data = resp.json()
        
        username = user_data.get('loginUsuario')
        name = user_data.get('nomeUsuario')
        email = user_data.get('emailPrincipalUsuario')
        raw_nusp = user_data.get('codpes') # USP Number
        
        nusp = str(raw_nusp) if raw_nusp else str(username) if username else None

        if not username:
             flash("Dados de usuário inválidos retornados pela USP.", 'danger')
             return redirect(url_for('auth.login'))

        # Check if user exists
        user = User.query.filter((User.nusp == nusp) | (User.username == username)).first()
        
        if not user:
            # Auto-register
            # Check for email collision
            if email:
                 existing_email = User.query.filter_by(email=email).first()
                 if existing_email:
                     user = existing_email
                     user.nusp = nusp
                     db.session.commit()
            
            if not user:
                # Create NEW User
                temp_pass = secrets.token_urlsafe(16)
                hashed = generate_password_hash(temp_pass, method='pbkdf2:sha256')
                
                final_username = username
                if User.query.filter_by(username=final_username).first():
                    final_username = f"{username}_{nusp}"

                user = User(
                    username=final_username,
                    password_hash=hashed,
                    name=name,
                    email=email,
                    nusp=nusp,
                    role='user',
                    is_default_password=False
                )
                db.session.add(user)
                db.session.commit()
                # Send Notifications
                try:
                    from models import GlobalSettings
                    from services.email_service import send_welcome_email, send_new_user_admin_notification
                    
                    settings = GlobalSettings.query.first()
                    if settings:
                        # Send Welcome to User
                        send_welcome_email(user, settings)
                        
                        # Notify Admins (defined in settings or query DB)
                        admins = User.query.filter_by(role='admin').all()
                        send_new_user_admin_notification(user, admins, settings)
                        
                except Exception as e:
                    print(f"Error sending emails: {e}")

                
        login_user(user)
        flash(f'Bem-vindo, {user.name}!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash(f'Erro no login USP: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))
