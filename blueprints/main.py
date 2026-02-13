from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from models import Class, Discipline, Professor, Schedule, ClassProfessor

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Dashboard summary
    total_classes = Class.query.count()
    total_disciplines = Discipline.query.count()
    total_professors = Professor.query.count()
    
    return render_template('index.html', 
                           total_classes=total_classes,
                           total_disciplines=total_disciplines,
                           total_professors=total_professors)

@main_bp.route('/horarios/relatorio')
def report_schedules():
    department = request.args.get('department')
    level = request.args.get('level')
    
    query = Class.query.join(Discipline)
    
    if department:
        query = query.filter(Discipline.department == department)
    
    if level:
        if 'Pós' in level or 'Pos' in level:
            # Match any "Pós..." variation
            query = query.filter(Discipline.degree_level.ilike(f"%Pós%"))
        elif level == 'Graduação':
            # Match "Graduação" but EXCLUDE "Pós"
            query = query.filter(
                Discipline.degree_level.ilike(f"%Graduação%"),
                ~Discipline.degree_level.ilike(f"%Pós%")
            )
        else:
            query = query.filter(Discipline.degree_level == level)
        
    classes = query.order_by(Discipline.code).all()
    
    # Prepare data for view (similar to CSV structure)
    data = []
    for c in classes:
        # Format Schedules
        sched_strs = []
        for s in c.schedules:
            sched_strs.append(f"{s.day} {s.start_time} {s.end_time}")
        sched_display = "<br>".join(sched_strs)
        
        # Format Professors
        prof_strs = []
        for cp in c.professors:
            prof_strs.append(cp.professor.name)
        prof_display = "<br>".join(prof_strs)
        
        data.append({
            'class_code': c.code,
            'discipline_code': c.discipline.code,
            'discipline_name': c.discipline.name,
            'type': c.class_type,
            'room': c.room,
            'schedule': sched_display,
            'professors': prof_display
        })
        
    title = "Relatório Geral"
    if department and level:
        title = f"{level} - Departamento {department}"
    elif department:
        title = f"Departamento {department}"
    elif level:
        title = f"{level}"
        
    return render_template('all_schedules.html', classes=data, title=title)

# TODO: Add other views
