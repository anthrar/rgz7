import json
from datetime import date, timedelta

from app.models import AuditLog, Subscription


def test_get_subscriptions_empty(authenticated_client):
    response = authenticated_client.get("/api/subscriptions")

    assert response.status_code == 200
    data = response.get_json()
    assert "subscriptions" in data
    assert data["subscriptions"] == []

def test_create_subscription_success(authenticated_client):
    payload = {
        "name": "Yandex Music",
        "amount": 9.99,
        "interval": "monthly",
        "next_billing_date": (date.today() + timedelta(days=30)).isoformat(),
    }

    response = authenticated_client.post(
        "/api/subscriptions",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert response.status_code == 201
    data = response.get_json()

    assert data["name"] == "Yandex Music"
    assert data["amount"] == 9.99
    assert data["interval"] == "monthly"
    assert data["is_active"] is True


def test_create_subscription_validation_error(authenticated_client):
    response = authenticated_client.post("/api/subscriptions", json={})

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data or "errors" in data

def test_get_single_subscription(authenticated_client, user, db_session):
    subscription = Subscription(
        user_id=user.id,
        name="Spotify",
        amount=5.99,
        interval="monthly",
        next_billing_date=date.today(),
        is_active=True,
    )
    db_session.add(subscription)
    db_session.flush()

    response = authenticated_client.get(f"/api/subscriptions/{subscription.id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Spotify"


def test_get_subscription_forbidden(authenticated_client, db_session):
    subscription = Subscription(
        user_id=9999,  # другой пользователь
        name=" чужая ",
        amount=10,
        interval="monthly",
        next_billing_date=date.today(),
        is_active=True,
    )
    db_session.add(subscription)
    db_session.flush()

    response = authenticated_client.get(f"/api/subscriptions/{subscription.id}")

    assert response.status_code == 403


def test_update_subscription(authenticated_client, user, db_session):
    subscription = Subscription(
        user_id=user.id,
        name="Old name",
        amount=10,
        interval="monthly",
        next_billing_date=date.today(),
        is_active=True,
    )
    db_session.add(subscription)
    db_session.flush()

    response = authenticated_client.put(
        f"/api/subscriptions/{subscription.id}",
        json={"name": "New name", "amount": 20},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "New name"
    assert data["amount"] == 20

def test_delete_subscription(authenticated_client, user, db_session):
    subscription = Subscription(
        user_id=user.id,
        name="To delete",
        amount=3,
        interval="monthly",
        next_billing_date=date.today(),
        is_active=True,
    )
    db_session.add(subscription)
    db_session.flush()

    response = authenticated_client.delete(f"/api/subscriptions/{subscription.id}")

    assert response.status_code == 200

    deleted = db_session.get(Subscription, subscription.id)
    assert deleted is None

def test_get_audit_logs(authenticated_client, user, db_session):
    log = AuditLog(
        user_id=user.id,
        action="create",
        entity_type="subscription",
        entity_id=1,
    )
    db_session.add(log)
    db_session.flush()

    response = authenticated_client.get("/api/audit_logs")

    assert response.status_code == 200
    data = response.get_json()
    assert "audit_logs" in data
    assert len(data["audit_logs"]) == 1
