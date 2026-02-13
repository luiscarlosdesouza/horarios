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
    
    # Filters
    discipline_filter = request.args.get('discipline')
    class_filter = request.args.get('class_code')
    department_filter = request.args.get('department')
    level_filter = request.args.get('degree_level')
    
    # If any filter is present, run search
    search_results = []
    has_search = False
    
    if discipline_filter or class_filter or department_filter or level_filter:
        has_search = True
        from sqlalchemy import or_
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
            
        search_results = query.limit(100).all()
    
    return render_template('index.html', 
                           total_classes=total_classes,
                           total_disciplines=total_disciplines,
                           total_professors=total_professors,
                           search_results=search_results,
                           has_search=has_search)

@main_bp.route('/horarios/pdf')
def export_pdf():
    # Reuse filtering logic (Copy-paste for now to ensure consistency, 
    # ideally refactor into a service function later)
    discipline_filter = request.args.get('discipline')
    class_filter = request.args.get('class_code')
    department_filter = request.args.get('department')
    level_filter = request.args.get('degree_level')
    
    from sqlalchemy import or_
    query = Class.query.join(Discipline)
    
    # Apply filters (same logic as index)
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
        
    classes = query.order_by(Discipline.code).limit(200).all() # Limit for PDF performance
    
    # Generate PDF
    from xhtml2pdf import pisa
    from io import BytesIO
    
    html = render_template('pdf_report.html', classes=classes, 
                          department=department_filter, level=level_filter)
    
    pdf_output = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_output)
    
    if pisa_status.err:
        return f"Erro ao gerar PDF: {pisa_status.err}", 500
        
    pdf_output.seek(0)
    
    from flask import send_file
    return send_file(pdf_output, 
                     as_attachment=True, 
                     download_name='horarios_filtros.pdf', 
                     mimetype='application/pdf')

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
