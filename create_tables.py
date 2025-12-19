"""
Скрипт для создания таблиц в базе данных.
"""
import sys
from app import create_app
from app.models import db

def create_tables():
    """Создать все таблицы в базе данных."""
    app = create_app('development')
    
    with app.app_context():
        try:
            db.create_all()
            print("Таблицы успешно созданы!")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    create_tables()

