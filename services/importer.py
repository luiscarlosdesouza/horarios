import csv
import io
from extensions import db
from models import Discipline, Professor, Class, Schedule, ClassProfessor

def parse_schedule(schedule_str):
    if not schedule_str or schedule_str == 'nan':
        return []
    
    entries = []
    lines = schedule_str.split('\n')
    for line in lines:
        line = line.strip()
        if not line: continue
        parts = line.split()
        if len(parts) >= 3:
            day = parts[0]
            start = parts[1]
            end = parts[2]
            entries.append({'day': day, 'start': start, 'end': end})
    return entries

def parse_professors(prof_str):
    if not prof_str or prof_str == 'nan':
        return []
    return [p.strip() for p in prof_str.split('\n') if p.strip()]

def process_csv_stream(file_stream):
    # Wrapper to handle text stream from file upload
    # If file_stream is bytes, decode it.
    if isinstance(file_stream, bytes):
        file_stream = file_stream.decode('utf-8')
        
    csv_file = io.StringIO(file_stream)
    reader = csv.DictReader(csv_file)
    process_csv_rows(reader)

def process_csv_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        process_csv_rows(reader)

def process_csv_rows(reader):
    count = 0
    for row in reader:
        # Discipline
        disc_code = row['Código da Disciplina']
        disc_name = row['Nome da Disciplina']
        # Extract department from first 3 chars of code (e.g. MAC0110 -> MAC)
        dept = disc_code[:3] if len(disc_code) >= 3 else None
        
        # Extract degree level from 'Tipo' column (assuming it exists based on user request)
        # Fallback to None if not present
        degree_level = row.get('Tipo') or row.get('Tipo da Turma') 
        
        # Normalize Pós-Graduação
        if degree_level and 'pós' in degree_level.lower() and 'graduação' in degree_level.lower():
             degree_level = 'Pós-Graduação'
        elif degree_level and degree_level.lower().strip() == 'graduação':
             degree_level = 'Graduação'
        
        discipline = Discipline.query.get(disc_code)
        if not discipline:
            discipline = Discipline(
                code=disc_code, 
                name=disc_name,
                department=dept,
                degree_level=degree_level
            )
            db.session.add(discipline)
        else:
            # Update existing discipline fields if missing/changed
            if not discipline.department:
                discipline.department = dept
            if not discipline.degree_level:
                discipline.degree_level = degree_level
        
        # Class
        class_code = row['Código da Turma']
        semester = "2026.1"
        class_type = row['Tipo da Turma']
        room = row['Sala']
        
        class_obj = Class.query.filter_by(code=class_code, discipline_code=disc_code).first()
        if not class_obj:
            class_obj = Class(
                code=class_code,
                discipline_code=disc_code,
                semester=semester,
                class_type=class_type,
                room=room
            )
            db.session.add(class_obj)
            db.session.flush()
        
        # Professors
        prof_names = parse_professors(row['Professor(es)'])
        for name in prof_names:
            prof = Professor.query.filter_by(name=name).first()
            if not prof:
                prof = Professor(name=name)
                db.session.add(prof)
                db.session.flush()
            
            link = ClassProfessor.query.filter_by(class_id=class_obj.id, professor_id=prof.id).first()
            if not link:
                link = ClassProfessor(class_id=class_obj.id, professor_id=prof.id)
                db.session.add(link)
        
        # Schedules
        sched_entries = parse_schedule(row['Horários'])
        for entry in sched_entries:
            existing_sched = Schedule.query.filter_by(
                class_id=class_obj.id,
                day=entry['day'],
                start_time=entry['start']
            ).first()
            
            if not existing_sched:
                sched = Schedule(
                    class_id=class_obj.id,
                    day=entry['day'],
                    start_time=entry['start'],
                    end_time=entry['end']
                )
                db.session.add(sched)
        
        count += 1
        if count % 50 == 0:
            db.session.commit()
            
    db.session.commit()
    return count
