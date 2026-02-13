from flask_mail import Message
from extensions import mail
from flask import current_app
from models import GlobalSettings

def send_email(subject, recipients, html_body, sender=None, settings=None):
    """
    Generic email sender using Flask-Mail.
    Overrides configuration if settings object is provided.
    """
    try:
        if not settings:
            settings = GlobalSettings.query.first()
            
        if not settings:
            print("WARNING: No GlobalSettings found. Cannot send email.")
            return False

        # Configure Flask-Mail dynamically (if needed) or rely on app config
        # For simple cases with Flask-Mail, we usually rely on app.config being updated
        # or we construct the connection manually. 
        # Here we assume app.config is kept in sync or we use a custom connection.
        
        # NOTE: Flask-Mail uses current_app.config. To support dynamic settings from DB,
        # we might need to re-configure it or send via a new connection.
        # For simplicity in this stack, let's assume we update app config on settings save
        # or use a direct SMTP connection if Flask-Mail is too static.
        
        # However, to avoid complexity, let's try to use the mail instance.
        # If dynamic config is strict, we might need smtplib directly.
        
        msg = Message(subject, sender=sender or settings.email_user, recipients=recipients)
        msg.html = html_body
        
        # If we need to dynamically set server params per send, Flask-Mail is tricky.
        # Let's assume for now we reuse the app's mail extension which is configured via env/db.
        # If DB settings change, we should reload app config or use smtplib.
        
        # Let's use smtplib for robustness with dynamic DB settings.
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg['From'] = sender or settings.email_user
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.email_user, settings.email_password)
        text = msg.as_string()
        server.sendmail(settings.email_user, recipients, text)
        server.quit()
        
        print(f"Email sent to {recipients}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_welcome_email(user, settings):
    subject = "Bem-vindo ao Sistema de Horários IME-USP"
    html_body = f"""
    <h3>Olá, {user.name or user.username}!</h3>
    <p>Seu cadastro foi recebido com sucesso.</p>
    <p><b>Status atual:</b> {user.role} (Acesso Básico)</p>
    <p>Para obter permissões de Operador ou Administrador, aguarde a liberação por um responsável (prazo estimado: até 48h).</p>
    <hr>
    <p><i>Sistema de Horários IME-USP</i></p>
    """
    return send_email(subject, [user.email], html_body, settings=settings)

def send_new_user_admin_notification(new_user, admins, settings):
    if not settings.email_to and not admins:
        return False
        
    recipients = [settings.email_to] if settings.email_to else [a.email for a in admins if a.email]
    
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
    return send_email(subject, recipients, html_body, settings=settings)
