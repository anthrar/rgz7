"""
Тесты для моделей данных.
"""
from datetime import date

from app.models import AuditLog, Subscription, User


def test_user_creation(db_session):
    """Тест создания пользователя."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password_hash != "password123"  # Пароль должен быть захеширован


def test_user_password_check(db_session):
    """Тест проверки пароля пользователя."""
    user = User(username="testuser", email="test@example.com")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    assert user.check_password("password123") is True
    assert user.check_password("wrongpassword") is False


def test_subscription_creation(db_session, user):
    """Тест создания подписки."""
    subscription = Subscription(
        user_id=user.id,
        name="Netflix",
        amount=999.99,
        interval="monthly",
        next_billing_date=date(2024, 12, 1),
        is_active=True,
    )
    db_session.add(subscription)
    db_session.commit()

    assert subscription.id is not None
    assert subscription.user_id == user.id
    assert subscription.name == "Netflix"
    assert float(subscription.amount) == 999.99
    assert subscription.interval == "monthly"
    assert subscription.is_active is True


def test_subscription_to_dict(db_session, user):
    """Тест преобразования подписки в словарь."""
    subscription = Subscription(
        user_id=user.id,
        name="Spotify",
        amount=499.00,
        interval="monthly",
        next_billing_date=date(2024, 12, 1),
    )
    db_session.add(subscription)
    db_session.commit()

    data = subscription.to_dict()
    assert "id" in data
    assert "name" in data
    assert "amount" in data
    assert data["name"] == "Spotify"
    assert data["amount"] == 499.0


def test_audit_log_creation(db_session, user):
    """Тест создания лога аудита."""
    audit_log = AuditLog(
        user_id=user.id,
        action="create",
        entity_type="subscription",
        entity_id=1,
        ip_address="127.0.0.1",
        user_agent="test-agent",
    )
    db_session.add(audit_log)
    db_session.commit()

    assert audit_log.id is not None
    assert audit_log.user_id == user.id
    assert audit_log.action == "create"
    assert audit_log.entity_type == "subscription"
    assert audit_log.entity_id == 1


def test_user_subscription_relationship(db_session, user):
    """Тест связи пользователя с подписками."""
    subscription1 = Subscription(
        user_id=user.id,
        name="Service 1",
        amount=100.0,
        interval="monthly",
        next_billing_date=date(2024, 12, 1),
    )
    subscription2 = Subscription(
        user_id=user.id,
        name="Service 2",
        amount=200.0,
        interval="yearly",
        next_billing_date=date(2024, 12, 1),
    )
    db_session.add_all([subscription1, subscription2])
    db_session.commit()

    assert len(user.subscriptions) == 2
    assert subscription1.user.username == "testuser"
    assert subscription2.user.username == "testuser"
