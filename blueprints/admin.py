from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from services.importer import process_csv_stream

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def admin_required():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores.', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/upload', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado.', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
            
        if file and file.filename.endswith('.csv'):
            try:
                # Read file content as string
                content = file.read().decode('utf-8')
                count = process_csv_stream(content)
                flash(f'Importação concluída! {count} registros processados.', 'success')
            except Exception as e:
                flash(f'Erro na importação: {str(e)}', 'danger')
        else:
            flash('Formato de arquivo inválido. Envie um CSV.', 'danger')
            
    return render_template('admin/upload.html')

# --- User Management ---

from models import User
from extensions import db
from werkzeug.security import generate_password_hash
import secrets

@admin_bp.route('/users')
@login_required
def users_list():
    if current_user.role != 'admin':
        flash('Acesso negado. Apenas administradores podem gerenciar usuários.', 'danger')
        return redirect(url_for('main.index'))
    
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id=None):
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))
        
    user = User.query.get(user_id) if user_id else None
    
    if request.method == 'POST':
        # Password Reset
        if request.form.get('reset_password'):
            temp_pass = secrets.token_urlsafe(8)
            user.password_hash = generate_password_hash(temp_pass, method='pbkdf2:sha256')
            user.is_default_password = True
            db.session.commit()
            flash(f'Senha redefinida! Nova senha temporária: {temp_pass}', 'warning')
            return redirect(url_for('admin.edit_user', user_id=user.id))

        name = request.form.get('name')
        email = request.form.get('email')
        role = request.form.get('role')
        # receive_notifications logic omitted as service doesn't exist yet
        
        if user:
            user.name = name
            user.email = email
            user.role = role
            db.session.commit()
            
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('admin.users_list'))
        else:
            username = request.form.get('username')
            if User.query.filter_by(username=username).first():
                flash('Nome de usuário já existe.', 'danger')
                return render_template('admin/edit_user.html', user=None)
            
            temp_pass = secrets.token_urlsafe(8)
            hashed = generate_password_hash(temp_pass, method='pbkdf2:sha256')
            
            new_user = User(
                username=username,
                password_hash=hashed,
                name=name,
                email=email,
                role=role,
                is_default_password=True
            )
            db.session.add(new_user)
            db.session.commit()
            flash(f'Usuário criado! Senha temporária: {temp_pass}', 'success')
            return redirect(url_for('admin.users_list'))

    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('admin.users_list'))
        
    user = User.query.get(user_id)
    if user:
        if user.username == 'admin':
            flash('Não é possível excluir o administrador principal.', 'danger')
        elif user.id == current_user.id:
            flash('Você não pode excluir a si mesmo.', 'danger')
        else:
            db.session.delete(user)
            db.session.commit()
            flash('Usuário excluído.', 'success')
    return redirect(url_for('admin.users_list'))
