"""
Инициализация Flask приложения.
"""
from flask import Flask
from flask_login import LoginManager
from config import config
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Загрузить пользователя из базы данных."""
    return db.session.get(User, int(user_id))
    

def create_app(config_name='development'):
    """
    создание Flask приложения с правильным конфигом.
    
    Args:
        config_name: Имя конфигурации ('development', 'testing', 'production')
    
    Returns:
        Flask приложение
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    
    # Регистрация blueprints
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)
    
    return app
