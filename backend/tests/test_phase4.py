from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Employee, Presence, utcnow
from tests.conftest import login
from tests.test_phase1 import headers


def test_presence_heartbeat_manual_status_and_expiry(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tenant = seeded["tenant_a"]
    owner = seeded["owner"]
    employee = Employee(
        tenant_id=tenant.id,
        user_id=owner.id,
        employee_number="A-PRESENCE",
        full_name="Present Owner",
        work_email=owner.email,
    )
    db.add(employee)
    db.commit()
    tokens = login(client)

    initial = client.get("/api/v1/presence/me", headers=headers(tokens, tenant.id))
    assert initial.status_code == 200
    assert initial.json()["status"] == "offline"
    assert initial.json()["employee_id"] == employee.id

    heartbeat = client.post(
        "/api/v1/presence/me/heartbeat",
        headers=headers(tokens, tenant.id),
        json={},
    )
    assert heartbeat.status_code == 200
    assert heartbeat.json()["status"] == "available"

    busy = client.put(
        "/api/v1/presence/me",
        headers=headers(tokens, tenant.id),
        json={"status": "busy"},
    )
    assert busy.status_code == 200
    assert busy.json()["status"] == "busy"

    presence = db.scalar(
        select(Presence).where(
            Presence.tenant_id == tenant.id,
            Presence.user_id == owner.id,
        )
    )
    assert presence is not None
    presence.expires_at = utcnow() - timedelta(seconds=1)
    db.commit()
    expired = client.get("/api/v1/presence/me", headers=headers(tokens, tenant.id))
    assert expired.status_code == 200
    assert expired.json()["status"] == "offline"


def test_presence_directory_is_tenant_scoped_and_bounded(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    owner = seeded["owner"]
    employee_a = Employee(
        tenant_id=tenant_a.id,
        user_id=owner.id,
        employee_number="A-ONLINE",
        full_name="Alpha Owner",
        work_email="alpha-presence@example.com",
    )
    employee_b = Employee(
        tenant_id=tenant_b.id,
        user_id=owner.id,
        employee_number="B-ONLINE",
        full_name="Beta Owner",
        work_email="beta-presence@example.com",
    )
    db.add_all([employee_a, employee_b])
    db.commit()
    tokens = login(client)
    assert (
        client.post(
            "/api/v1/presence/me/heartbeat",
            headers=headers(tokens, tenant_a.id),
            json={"status": "available"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/presence/me/heartbeat",
            headers=headers(tokens, tenant_b.id),
            json={"status": "away"},
        ).status_code
        == 200
    )

    alpha = client.get("/api/v1/presence", headers=headers(tokens, tenant_a.id))
    assert alpha.status_code == 200
    assert [(item["employee_id"], item["status"]) for item in alpha.json()] == [
        (employee_a.id, "available")
    ]
    beta = client.get("/api/v1/presence", headers=headers(tokens, tenant_b.id))
    assert beta.status_code == 200
    assert [(item["employee_id"], item["status"]) for item in beta.json()] == [
        (employee_b.id, "away")
    ]
    assert (
        client.get("/api/v1/presence?limit=101", headers=headers(tokens, tenant_a.id)).status_code
        == 422
    )


def test_presence_rejects_invalid_status(client: TestClient, seeded: dict[str, object]) -> None:
    tokens = login(client)
    response = client.put(
        "/api/v1/presence/me",
        headers=headers(tokens, seeded["tenant_a"].id),
        json={"status": "invisible"},
    )
    assert response.status_code == 422
