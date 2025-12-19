"""
Точка входа для запуска Flask приложения.
"""
import os
from app import create_app

# Определяем окружение из переменной окружения или используем development по умолчанию
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

