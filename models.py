from extensions import db
from flask_login import UserMixin

class Discipline(db.Model):
    __tablename__ = 'disciplines'
    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(10), nullable=True) # MAC, MAT, MAE, MAP
    degree_level = db.Column(db.String(50), nullable=True) # Graduação / Pós-Graduação
    classes = db.relationship('Class', backref='discipline', lazy=True)

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    classes = db.relationship('ClassProfessor', backref='professor', lazy=True)

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20))
    discipline_code = db.Column(db.String(20), db.ForeignKey('disciplines.code'), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    class_type = db.Column(db.String(50))
    room = db.Column(db.String(100))
    
    schedules = db.relationship('Schedule', backref='class_obj', lazy=True)
    professors = db.relationship('ClassProfessor', backref='class_obj', lazy=True)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)

class ClassProfessor(db.Model):
    __tablename__ = 'class_professors'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(200))
    nusp = db.Column(db.String(50), unique=True)
    role = db.Column(db.String(20), default='user')
    password_hash = db.Column(db.String(200))
    is_default_password = db.Column(db.Boolean, default=False)

class GlobalSettings(db.Model):
    __tablename__ = 'global_settings'
    id = db.Column(db.Integer, primary_key=True)
    # Email Config
    email_user = db.Column(db.String(100), nullable=True)
    email_password = db.Column(db.String(100), nullable=True)
    email_to = db.Column(db.String(500), nullable=True) # Quem recebe notificacoes
    smtp_server = db.Column(db.String(100), default='smtp.gmail.com')
    smtp_port = db.Column(db.Integer, default=587)
    
    # Intervals (Optional, inherited from monitora_sites idea)
    interval_weekday = db.Column(db.Integer, default=60)
    interval_weekend = db.Column(db.Integer, default=120)
    alert_threshold = db.Column(db.Integer, default=15)
