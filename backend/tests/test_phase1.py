from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditEvent
from tests.conftest import login


def headers(tokens: dict[str, str], tenant_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tokens['access_token']}", "X-Tenant-ID": tenant_id}


def test_health_endpoints(client: TestClient) -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/livez").status_code == 200
    with patch("app.main.redis.from_url") as redis_mock:
        redis_mock.return_value.ping.return_value = True
        assert client.get("/readyz").status_code == 200


def test_auth_success_failure_and_current_tenant(
    client: TestClient, seeded: dict[str, object]
) -> None:
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "owner@example.com", "password": "wrong-pass"}
        ).status_code
        == 401
    )
    tokens = login(client)
    tenant_a = seeded["tenant_a"]
    response = client.get("/api/v1/auth/me", headers=headers(tokens, tenant_a.id))
    assert response.status_code == 200
    assert response.json()["tenant_id"] == tenant_a.id
    assert (
        client.get(
            "/api/v1/auth/me",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "X-Tenant-ID": "not-a-tenant",
            },
        ).status_code
        == 403
    )


def test_refresh_rotation_logout_and_reuse_detection(client: TestClient) -> None:
    first = login(client)
    rotated = client.post("/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != first["refresh_token"]
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]}
        ).status_code
        == 401
    )
    second = login(client)
    assert (
        client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": second["refresh_token"]},
            headers={"Authorization": f"Bearer {second['access_token']}"},
        ).status_code
        == 204
    )
    assert (
        client.post(
            "/api/v1/auth/refresh", json={"refresh_token": second["refresh_token"]}
        ).status_code
        == 401
    )


def test_employee_crud_audit_and_cross_tenant_denial(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tokens = login(client)
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    created = client.post(
        "/api/v1/employees",
        headers=headers(tokens, tenant_a.id),
        json={"employee_number": "A-1", "full_name": "Alice", "work_email": "alice@example.com"},
    )
    assert created.status_code == 201
    employee_id = created.json()["id"]
    assert (
        client.get(
            f"/api/v1/employees/{employee_id}", headers=headers(tokens, tenant_a.id)
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/v1/employees/{employee_id}",
            headers=headers(tokens, tenant_a.id),
            json={"title": "Manager"},
        ).json()["title"]
        == "Manager"
    )
    assert (
        client.post(
            f"/api/v1/employees/{employee_id}/suspend", headers=headers(tokens, tenant_a.id)
        ).json()["is_suspended"]
        is True
    )
    assert (
        client.get(
            f"/api/v1/employees/{employee_id}", headers=headers(tokens, tenant_b.id)
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"/api/v1/employees/{employee_id}",
            headers=headers(tokens, tenant_b.id),
            json={"title": "Intruder"},
        ).status_code
        == 404
    )
    assert len(list(db.scalars(select(AuditEvent).where(AuditEvent.tenant_id == tenant_a.id)))) == 3


def test_permission_denial(client: TestClient, seeded: dict[str, object]) -> None:
    tokens = login(client, email="viewer@example.com")
    tenant_a = seeded["tenant_a"]
    assert (
        client.post(
            "/api/v1/employees",
            headers=headers(tokens, tenant_a.id),
            json={"employee_number": "A-2", "full_name": "Nope", "work_email": "nope@example.com"},
        ).status_code
        == 403
    )


def test_department_foundation(client: TestClient, seeded: dict[str, object]) -> None:
    tokens = login(client)
    tenant_a = seeded["tenant_a"]
    created = client.post(
        "/api/v1/departments", headers=headers(tokens, tenant_a.id), json={"name": "Engineering"}
    )
    assert created.status_code == 201
    updated = client.patch(
        f"/api/v1/departments/{created.json()['id']}",
        headers=headers(tokens, tenant_a.id),
        json={"description": "Builds DWCO"},
    )
    assert updated.status_code == 200
    assert (
        client.get("/api/v1/departments", headers=headers(tokens, tenant_a.id)).status_code == 200
    )


def test_client_tenant_id_is_ignored_in_employee_payload(
    client: TestClient, seeded: dict[str, object]
) -> None:
    tokens = login(client)
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    response = client.post(
        "/api/v1/employees",
        headers=headers(tokens, tenant_a.id),
        json={
            "tenant_id": tenant_b.id,
            "employee_number": "A-3",
            "full_name": "Safe",
            "work_email": "safe@example.com",
        },
    )
    assert response.status_code == 201
