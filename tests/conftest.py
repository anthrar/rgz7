"""
Конфигурация pytest и фикстуры для тестов.
"""
import os

import pytest
from sqlalchemy.pool import StaticPool

# Настраиваем окружение до импорта приложения,
# чтобы Flask конфигурация подхватила SQLite для тестов.

from app import create_app, db
from app.models import User


def _sqlite_engine_options(uri: str):
    """Настройки движка для SQLite in-memory."""
    if uri.startswith("sqlite"):
        return {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }
    return {}


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    database_uri = str(app.config['SQLALCHEMY_DATABASE_URI'])
    if _sqlite_engine_options(database_uri):
        app.config.update(
            SQLALCHEMY_ENGINE_OPTIONS=_sqlite_engine_options(database_uri),
        )

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(autouse=True)
def reset_database(app):
    """Сбрасывает БД перед каждым тестом."""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


@pytest.fixture(scope="session")
def database(): 
    yield db


@pytest.fixture(scope="function")
def db_session(app): 
    """Возвращает сессию SQLAlchemy внутри app context."""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture(scope="function")
def client(app):
    """Тестовый HTTP клиент Flask."""
    return app.test_client()


@pytest.fixture(scope="function")
def user(db_session):
    """Создание тестового пользователя."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("testpass123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def authenticated_client(client, user):
    """HTTP клиент с аутентифицированным пользователем в сессии."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)  # Flask-Login хранит id в сессии
        sess["_fresh"] = True
    return client
