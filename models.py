from extensions import db

class Discipline(db.Model):
    __tablename__ = 'disciplines'
    code = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    classes = db.relationship('Class', backref='discipline', lazy=True)

class Professor(db.Model):
    __tablename__ = 'professors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    classes = db.relationship('ClassProfessor', backref='professor', lazy=True)

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20)) # Código da Turma (can be non-unique across years? assuming unique for current scope)
    discipline_code = db.Column(db.String(20), db.ForeignKey('disciplines.code'), nullable=False)
    semester = db.Column(db.String(20), nullable=False) # e.g. "2026.1"
    class_type = db.Column(db.String(50)) # Graduação/Pós
    room = db.Column(db.String(100))
    
    schedules = db.relationship('Schedule', backref='class_obj', lazy=True)
    professors = db.relationship('ClassProfessor', backref='class_obj', lazy=True)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False) # seg, ter, qua...
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)

class ClassProfessor(db.Model):
    __tablename__ = 'class_professors'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('professors.id'), nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) # numero usp
    email = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
