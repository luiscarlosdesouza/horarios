from app import create_app
from extensions import db
from services.importer import process_csv_file

app = create_app()

def import_data():
    with app.app_context():
        db.create_all()
        print("Database initialized.")
        count = process_csv_file('todos_horarios.csv')
        print(f"Import complete! Processed {count} rows.")

if __name__ == '__main__':
    import_data()
