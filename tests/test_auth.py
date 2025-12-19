"""
Тесты для системы аутентификации.
"""
from app.models import User


def test_register_user(client, db_session):
    """Тест регистрации нового пользователя."""
    response = client.post(
        "/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    data = response.get_json()
    assert "user_id" in data

    # Проверка создания пользователя в БД
    user = User.query.filter_by(username="newuser").first()
    assert user is not None
    assert user.email == "newuser@example.com"


def test_register_duplicate_username(client, db_session, user):
    """Тест регистрации с существующим именем пользователя."""
    response = client.post(
        "/register",
        json={
            "username": "testuser",  # Уже существует
            "email": "another@example.com",
            "password": "password123",
        },
        content_type="application/json",
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data


def test_register_invalid_email(client, db_session):
    """Тест регистрации с невалидным email."""
    response = client.post(
        "/register",
        json={
            "username": "newuser",
            "email": "invalid-email",
            "password": "password123",
        },
        content_type="application/json",
    )

    assert response.status_code == 400


def test_login_success(client, user):
    """Тест успешного входа."""
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "testpass123"},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "user_id" in data


def test_login_wrong_password(client, user):
    """Тест входа с неправильным паролем."""
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "wrongpassword"},
        content_type="application/json",
    )

    assert response.status_code == 401
    data = response.get_json()
    assert "error" in data


def test_login_nonexistent_user(client):
    """Тест входа несуществующего пользователя."""
    response = client.post(
        "/login",
        json={"username": "nonexistent", "password": "password123"},
        content_type="application/json",
    )

    assert response.status_code == 401


def test_logout(client, authenticated_client):
    """Тест выхода из системы."""
    response = authenticated_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_protected_route_requires_auth(client):
    """Тест доступа к защищенному роуту без авторизации."""
    response = client.get("/api/subscriptions")
    assert response.status_code in (401, 302)  # Редирект на логин или 401
