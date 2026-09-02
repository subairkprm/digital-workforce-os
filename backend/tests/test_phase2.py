from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditEvent, SecurityEvent
from tests.conftest import login
from tests.test_phase1 import headers


def test_role_crud_membership_assignment_and_audit(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tokens = login(client)
    tenant_a = seeded["tenant_a"]
    created = client.post(
        "/api/v1/roles",
        headers=headers(tokens, tenant_a.id),
        json={"name": "People Ops", "permissions": ["employee.read"]},
    )
    assert created.status_code == 201
    role_id = created.json()["id"]
    assert created.json()["permissions"] == ["employee.read"]

    updated = client.patch(
        f"/api/v1/roles/{role_id}",
        headers=headers(tokens, tenant_a.id),
        json={"permissions": ["employee.read", "employee.update"]},
    )
    assert updated.status_code == 200
    assert updated.json()["permissions"] == ["employee.read", "employee.update"]

    membership = seeded["member_viewer"]
    assigned = client.put(
        f"/api/v1/memberships/{membership.id}/roles",
        headers=headers(tokens, tenant_a.id),
        json={"role_ids": [role_id]},
    )
    assert assigned.status_code == 200
    assert assigned.json()["role_ids"] == [role_id]
    assert (
        client.delete(f"/api/v1/roles/{role_id}", headers=headers(tokens, tenant_a.id)).status_code
        == 409
    )

    actions = set(db.scalars(select(AuditEvent.action).where(AuditEvent.tenant_id == tenant_a.id)))
    assert {"role.created", "role.updated", "membership.roles_updated"} <= actions


def test_role_permission_and_cross_tenant_denials(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    viewer_tokens = login(client, email="viewer@example.com")
    denied = client.post(
        "/api/v1/roles",
        headers=headers(viewer_tokens, tenant_a.id),
        json={"name": "Denied", "permissions": []},
    )
    assert denied.status_code == 403
    event = db.scalar(select(SecurityEvent).where(SecurityEvent.category == "authorization.denied"))
    assert event is not None and event.tenant_id == tenant_a.id

    owner_tokens = login(client)
    role_b = seeded["role_owner"]
    assert (
        client.patch(
            f"/api/v1/roles/{role_b.id}",
            headers=headers(owner_tokens, tenant_b.id),
            json={"name": "Cross tenant"},
        ).status_code
        == 404
    )
    member_b = seeded["member_b"]
    assert (
        client.put(
            f"/api/v1/memberships/{member_b.id}/roles",
            headers=headers(owner_tokens, tenant_a.id),
            json={"role_ids": []},
        ).status_code
        == 404
    )


def test_security_event_access_is_tenant_scoped(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    db.add_all(
        [
            SecurityEvent(tenant_id=tenant_a.id, category="rate.limit", outcome="denied"),
            SecurityEvent(tenant_id=tenant_b.id, category="rate.limit", outcome="denied"),
        ]
    )
    db.commit()
    tokens = login(client)
    response = client.get("/api/v1/security-events", headers=headers(tokens, tenant_a.id))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_auth_rate_limit_returns_429(client: TestClient, db: Session) -> None:
    fake_redis = MagicMock()
    fake_redis.incr.side_effect = [1, 2]
    with (
        patch("app.rate_limit.redis.from_url", return_value=fake_redis),
        patch("app.routers.auth.get_settings") as settings,
    ):
        settings.return_value.auth_rate_limit = 1
        first = client.post(
            "/api/v1/auth/login",
            json={"email": "owner@example.com", "password": "correct-password"},
        )
        second = client.post(
            "/api/v1/auth/login",
            json={"email": "owner@example.com", "password": "correct-password"},
        )
    assert first.status_code == 200
    assert second.status_code == 429
    assert (
        db.scalar(select(SecurityEvent).where(SecurityEvent.category == "rate.limit")) is not None
    )


def test_tenant_mutation_rate_limit(client: TestClient, seeded: dict[str, object]) -> None:
    fake_redis = MagicMock()
    fake_redis.incr.side_effect = [1, 2]
    tenant_a = seeded["tenant_a"]
    tokens = login(client)
    with (
        patch("app.rate_limit.redis.from_url", return_value=fake_redis),
        patch("app.routers.roles.get_settings") as settings,
    ):
        settings.return_value.mutation_rate_limit = 1
        first = client.post(
            "/api/v1/roles",
            headers=headers(tokens, tenant_a.id),
            json={"name": "First", "permissions": []},
        )
        second = client.post(
            "/api/v1/roles",
            headers=headers(tokens, tenant_a.id),
            json={"name": "Second", "permissions": []},
        )
    assert first.status_code == 201
    assert second.status_code == 429


def test_refresh_reuse_creates_security_event(client: TestClient, db: Session) -> None:
    tokens = login(client)
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        ).status_code
        == 401
    )
    assert (
        db.scalar(select(SecurityEvent).where(SecurityEvent.category == "refresh.reuse"))
        is not None
    )
