from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from services.importer import process_csv_stream

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_csv():
    # Allow Admin and Operator
    if current_user.role not in ['admin', 'operator']:
        flash('Acesso negado. Permissão insuficiente.', 'danger')
        return redirect(url_for('main.index'))

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
        flash('Acesso negado. Apenas administradores.', 'danger')
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
            old_role = user.role
            user.name = name
            user.email = email
            user.role = role
            db.session.commit()
            
            if old_role != role and user.email:
                try:
                    from services.email_service import send_role_update_email
                    send_role_update_email(user, old_role, role)
                    flash('Usuário atualizado e notificado por e-mail!', 'success')
                except Exception as e:
                    print(f"Erro ao enviar email de role: {e}")
                    flash('Usuário atualizado, mas erro ao enviar e-mail.', 'warning')
            else:
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
        flash('Acesso negado. Apenas administradores.', 'danger')
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

# --- Schedule Management ---

from models import Class, Discipline, Schedule, Professor
from sqlalchemy import or_

@admin_bp.route('/schedules')
@login_required
def schedules_list():
    if current_user.role not in ['admin', 'operator']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))
        
    # Filters
    discipline_filter = request.args.get('discipline')
    class_filter = request.args.get('class_code')
    department_filter = request.args.get('department')
    level_filter = request.args.get('degree_level')
    
    query = Class.query.join(Discipline)
    
    if discipline_filter:
        query = query.filter(
            or_(
                Discipline.code.ilike(f'%{discipline_filter}%'),
                Discipline.name.ilike(f'%{discipline_filter}%')
            )
        )
    
    if class_filter:
        query = query.filter(Class.code.ilike(f'%{class_filter}%'))
        
    if department_filter:
        query = query.filter(Discipline.department == department_filter)
        
    if level_filter:
        query = query.filter(Discipline.degree_level == level_filter)
        
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/schedules.html', pagination=pagination, classes=pagination.items)

@admin_bp.route('/schedules/edit/<int:class_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(class_id):
    if current_user.role not in ['admin', 'operator']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))
        
    class_obj = Class.query.get_or_404(class_id)
    
    if request.method == 'POST':
        class_obj.class_type = request.form.get('class_type')
        class_obj.room = request.form.get('room')
        class_obj.semester = request.form.get('semester')
        # We could allow editing code, but be careful with discipline relation
        
        db.session.commit()
        flash('Turma atualizada com sucesso!', 'success')
        return redirect(url_for('admin.schedules_list'))
        
    return render_template('admin/edit_schedule.html', class_obj=class_obj)

@admin_bp.route('/schedules/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_schedule(class_id):
    if current_user.role not in ['admin', 'operator']:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.index'))
        
    class_obj = Class.query.get_or_404(class_id)
    
    # Process cleanup (Cascading deletes if not handled by DB needs manual cleanup)
    # SQLAlchemy relationship handles cascades usually if configured, 
    # but let's manual delete schedules just in case to be safe if cascade isn't set.
    Schedule.query.filter_by(class_id=class_obj.id).delete()
    # Also remove professors link??
    # ClassProfessor.query.filter_by(class_id=class_obj.id).delete() 
    # (Assuming we have imported ClassProfessor model, let's check imports)
    
    db.session.delete(class_obj)
    db.session.commit()
    
    flash('Turma excluída com sucesso.', 'success')
    return redirect(url_for('admin.schedules_list'))

# --- Global Settings ---
from models import GlobalSettings

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    try:
        if current_user.role != 'admin':
            flash('Acesso negado.', 'danger')
            return redirect(url_for('main.index'))
            
        settings = GlobalSettings.query.first()
        if not settings:
            settings = GlobalSettings()
            # Pre-populate from Env if available
            settings.smtp_server = current_app.config.get('EMAIL_SMTP_SERVER')
            settings.smtp_port = current_app.config.get('EMAIL_SMTP_PORT')
            settings.email_user = current_app.config.get('EMAIL_USER')
            settings.email_password = current_app.config.get('EMAIL_PASSWORD')
            settings.email_to = current_app.config.get('EMAIL_TO')
            
            db.session.add(settings)
            db.session.commit()

            
        if request.method == 'POST':
            settings.smtp_server = request.form.get('smtp_server')
            settings.smtp_port = int(request.form.get('smtp_port'))
            settings.email_user = request.form.get('email_user')
            
            pwd = request.form.get('email_password')
            if pwd and pwd.strip():
                settings.email_password = pwd
                
            settings.email_to = request.form.get('email_to')
            settings.interval_weekday = int(request.form.get('interval_weekday') or 60)
            settings.interval_weekend = int(request.form.get('interval_weekend') or 120)
            
            db.session.commit()
            flash('Configurações atualizadas com sucesso!', 'success')
            
        return render_template('admin/settings.html', settings=settings)
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Erro interno ao carregar configurações: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
