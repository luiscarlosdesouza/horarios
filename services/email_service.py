from flask_mail import Message
from extensions import mail
from flask import current_app
from models import GlobalSettings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_email_config():
    """
    Returns a dictionary with email configuration, priority: GlobalSettings > App Config (.env)
    """
    settings = GlobalSettings.query.first()
    
    config = {
        'smtp_server': current_app.config.get('EMAIL_SMTP_SERVER'),
        'smtp_port': current_app.config.get('EMAIL_SMTP_PORT') or 587,
        'email_user': current_app.config.get('EMAIL_USER'),
        'email_password': current_app.config.get('EMAIL_PASSWORD'),
        'email_to': current_app.config.get('EMAIL_TO')
    }
    
    if settings:
        if settings.smtp_server: config['smtp_server'] = settings.smtp_server
        if settings.smtp_port: config['smtp_port'] = settings.smtp_port
        if settings.email_user: config['email_user'] = settings.email_user
        if settings.email_password: config['email_password'] = settings.email_password
        if settings.email_to: config['email_to'] = settings.email_to
        
    return config

def send_email(subject, recipients, html_body, sender=None):
    """
    Generic email sender using smtplib with fallback configuration.
    """
    try:
        config = get_email_config()
        
        if not config['smtp_server'] or not config['email_user'] or not config['email_password']:
            print("WARNING: Missing email configuration (SMTP/User/Pass). Cannot send email.")
            return False

        msg = MIMEMultipart()
        msg['From'] = sender or config['email_user']
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email_user'], config['email_password'])
        text = msg.as_string()
        server.sendmail(config['email_user'], recipients, text)
        server.quit()
        
        print(f"Email sent to {recipients}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_welcome_email(user):
    subject = "Bem-vindo ao Sistema de Horários IME-USP"
    html_body = f"""
    <h3>Olá, {user.name or user.username}!</h3>
    <p>Seu cadastro foi recebido com sucesso.</p>
    <p><b>Status atual:</b> {user.role} (Acesso Básico)</p>
    <p>Para obter permissões de Operador ou Administrador, aguarde a liberação por um responsável (prazo estimado: até 48h).</p>
    <hr>
    <p><i>Sistema de Horários IME-USP</i></p>
    """
    return send_email(subject, [user.email], html_body)

def send_new_user_admin_notification(new_user, admins):
    config = get_email_config()
    recipients = []
    
    if config['email_to']:
         recipients.append(config['email_to'])
    
    if not recipients and admins:
        recipients = [a.email for a in admins if a.email]
        
    if not recipients:
        print("WARNING: No admin recipients found for notification.")
        return False
    
    subject = f"[ADMIN] Novo Usuário Cadastrado: {new_user.username}"
    html_body = f"""
    <h3>Novo registro no sistema</h3>
    <ul>
        <li><b>Usuario:</b> {new_user.username}</li>
        <li><b>Nome:</b> {new_user.name}</li>
        <li><b>Email:</b> {new_user.email}</li>
        <li><b>NUSP:</b> {new_user.nusp}</li>
    </ul>
    <p>Acesse o painel administrativo para alterar o nível de acesso deste usuário se necessário.</p>
    """
    return send_email(subject, recipients, html_body)

def send_role_update_email(user, old_role, new_role):
    subject = "Atualização de Permissões - Sistema de Horários"
    html_body = f"""
    <h3>Olá, {user.name or user.username}!</h3>
    <p>Suas permissões no sistema foram alteradas.</p>
    <ul>
        <li><b>Perfil Anterior:</b> {old_role}</li>
        <li><b>Novo Perfil:</b> {new_role}</li>
    </ul>
    <p>Se você recebeu permissões de operador ou administrador, novas funcionalidades já estão disponíveis no menu.</p>
    <p><i>Acesse: <a href="http://www2.ime.usp.br:5001">Sistema de Horários</a></i></p>
    """
    return send_email(subject, [user.email], html_body)


