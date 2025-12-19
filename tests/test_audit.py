"""
Тесты для системы аудита.
"""
from datetime import date

from app.models import AuditLog, Subscription
from app.services.audit import log_audit_event


def test_audit_log_on_create(authenticated_client, user, db_session):
    """Тест логирования создания подписки."""
    response = authenticated_client.post(
        "/api/subscriptions",
        json={
            "name": "Test Service",
            "amount": 100.0,
            "interval": "monthly",
            "next_billing_date": "2024-12-01",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    data = response.get_json()
    subscription_id = data["id"]

    # Проверка записи в аудите
    audit_log = AuditLog.query.filter_by(
        user_id=user.id,
        action="create",
        entity_type="subscription",
        entity_id=subscription_id,
    ).first()

    assert audit_log is not None
    assert audit_log.action == "create"
    assert audit_log.entity_type == "subscription"
    assert audit_log.entity_id == subscription_id


def test_audit_log_on_update(authenticated_client, user, db_session):
    """Тест логирования обновления подписки."""
    subscription = Subscription(
        user_id=user.id,
        name="Original Name",
        amount=100.0,
        interval="monthly",
        next_billing_date=date(2024, 12, 1),
    )
    db_session.add(subscription)
    db_session.commit()

    response = authenticated_client.put(
        f"/api/subscriptions/{subscription.id}",
        json={"name": "Updated Name"},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == "Updated Name"

    # Проверка записи в аудите
    audit_log = AuditLog.query.filter_by(
        user_id=user.id,
        action="update",
        entity_type="subscription",
        entity_id=subscription.id,
    ).first()

    assert audit_log is not None
    assert audit_log.action == "update"


def test_audit_log_on_delete(authenticated_client, user, db_session):
    """Тест логирования удаления подписки."""
    subscription = Subscription(
        user_id=user.id,
        name="To Delete",
        amount=100.0,
        interval="monthly",
        next_billing_date=date(2024, 12, 1),
    )
    db_session.add(subscription)
    db_session.commit()
    subscription_id = subscription.id

    response = authenticated_client.delete(f"/api/subscriptions/{subscription_id}")

    assert response.status_code == 200

    # Проверка записи в аудите
    audit_log = AuditLog.query.filter_by(
        user_id=user.id,
        action="delete",
        entity_type="subscription",
        entity_id=subscription_id,
    ).first()

    assert audit_log is not None
    assert audit_log.action == "delete"


def test_audit_log_ip_address(authenticated_client, user, db_session):
    """Тест сохранения IP адреса в логе аудита."""
    response = authenticated_client.post(
        "/api/subscriptions",
        json={
            "name": "Test",
            "amount": 100.0,
            "interval": "monthly",
            "next_billing_date": "2024-12-01",
        },
        content_type="application/json",
    )

    assert response.status_code == 201
    data = response.get_json()

    audit_log = AuditLog.query.filter_by(
        entity_id=data["id"],
        action="create",
    ).first()

    assert audit_log is not None
    # IP адрес должен быть сохранен (может быть 127.0.0.1 для тестового клиента)
    assert audit_log.ip_address is not None


def test_get_audit_logs(authenticated_client, user, db_session):
    """Тест получения логов аудита."""
    # Создаем несколько подписок для генерации логов
    for i in range(3):
        subscription = Subscription(
            user_id=user.id,
            name=f"Service {i}",
            amount=100.0 * (i + 1),
            interval="monthly",
            next_billing_date=date(2024, 12, 1),
        )
        db_session.add(subscription)
        db_session.commit()

        log_audit_event(user.id, "create", "subscription", subscription.id, None)

    response = authenticated_client.get("/api/audit_logs")

    assert response.status_code == 200
    data = response.get_json()
    assert "audit_logs" in data
    assert len(data["audit_logs"]) >= 3
