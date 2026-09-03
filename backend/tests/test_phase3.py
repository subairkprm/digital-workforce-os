from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    AuditEvent,
    Department,
    Employee,
    Invitation,
    Membership,
    RefreshSession,
    User,
)
from tests.conftest import login
from tests.test_phase1 import headers


def test_invitation_acceptance_is_single_use_and_audited(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tenant = seeded["tenant_a"]
    tokens = login(client)
    employee = Employee(
        tenant_id=tenant.id,
        employee_number="A-INVITED",
        full_name="New User",
        work_email="new.user@example.com",
    )
    db.add(employee)
    db.commit()
    created = client.post(
        "/api/v1/invitations",
        headers=headers(tokens, tenant.id),
        json={"email": "new.user@example.com", "role_ids": []},
    )
    assert created.status_code == 201
    raw_token = created.json()["token"]
    invitation_id = created.json()["id"]
    listed = client.get("/api/v1/invitations", headers=headers(tokens, tenant.id))
    assert listed.status_code == 200
    assert listed.json()[0]["token"] is None

    accepted = client.post(
        "/api/v1/invitations/accept",
        json={"token": raw_token, "password": "new-user-password"},
    )
    assert accepted.status_code == 204
    assert (
        client.post(
            "/api/v1/invitations/accept",
            json={"token": raw_token, "password": "another-password"},
        ).status_code
        == 400
    )
    invitation = db.get(Invitation, invitation_id)
    assert invitation is not None and invitation.accepted_at is not None
    invited_user = db.scalar(select(User).where(User.email == "new.user@example.com"))
    assert invited_user is not None
    db.refresh(employee)
    assert employee.user_id == invited_user.id
    membership = db.scalar(
        select(Membership).where(
            Membership.tenant_id == tenant.id, Membership.user_id == invited_user.id
        )
    )
    assert membership is not None
    actions = set(db.scalars(select(AuditEvent.action).where(AuditEvent.tenant_id == tenant.id)))
    assert {"invitation.created", "invitation.accepted"} <= actions


def test_invitation_rejects_cross_tenant_role_and_revoked_token(
    client: TestClient, seeded: dict[str, object]
) -> None:
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    tokens = login(client)
    cross_tenant = client.post(
        "/api/v1/invitations",
        headers=headers(tokens, tenant_a.id),
        json={"email": "cross@example.com", "role_ids": [seeded["role_b"].id]},
    )
    assert cross_tenant.status_code == 422
    created = client.post(
        "/api/v1/invitations",
        headers=headers(tokens, tenant_b.id),
        json={"email": "revoked@example.com"},
    )
    assert created.status_code == 201
    assert (
        client.delete(
            f"/api/v1/invitations/{created.json()['id']}", headers=headers(tokens, tenant_b.id)
        ).status_code
        == 204
    )
    assert (
        client.post(
            "/api/v1/invitations/accept",
            json={"token": created.json()["token"], "password": "revoked-password"},
        ).status_code
        == 400
    )


def test_session_list_and_revoke_are_user_scoped(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    owner_tokens = login(client)
    viewer_tokens = login(client, email="viewer@example.com")
    viewer = seeded["viewer"]
    viewer_session = db.scalar(select(RefreshSession).where(RefreshSession.user_id == viewer.id))
    assert viewer_session is not None
    assert (
        client.delete(
            f"/api/v1/auth/sessions/{viewer_session.id}",
            headers={"Authorization": f"Bearer {owner_tokens['access_token']}"},
        ).status_code
        == 404
    )
    listing = client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {viewer_tokens['access_token']}"},
    )
    assert listing.status_code == 200
    assert {item["id"] for item in listing.json()} == {viewer_session.id}
    assert (
        client.delete(
            f"/api/v1/auth/sessions/{viewer_session.id}",
            headers={"Authorization": f"Bearer {viewer_tokens['access_token']}"},
        ).status_code
        == 204
    )


def test_workforce_search_reactivation_and_tenant_safe_manager(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    tokens = login(client)
    employee_a = Employee(
        tenant_id=tenant_a.id,
        employee_number="A-SEARCH",
        full_name="Searchable Person",
        work_email="search@example.com",
        is_suspended=True,
    )
    employee_b = Employee(
        tenant_id=tenant_b.id,
        employee_number="B-MANAGER",
        full_name="Wrong Tenant",
        work_email="wrong@example.com",
    )
    department = Department(tenant_id=tenant_a.id, name="Operations")
    db.add_all([employee_a, employee_b, department])
    db.commit()
    response = client.get(
        "/api/v1/employees?q=Searchable&suspended=true&limit=10",
        headers=headers(tokens, tenant_a.id),
    )
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [employee_a.id]
    assert (
        client.post(
            f"/api/v1/employees/{employee_a.id}/reactivate", headers=headers(tokens, tenant_a.id)
        ).json()["is_suspended"]
        is False
    )
    assert (
        client.patch(
            f"/api/v1/departments/{department.id}",
            headers=headers(tokens, tenant_a.id),
            json={"manager_employee_id": employee_b.id},
        ).status_code
        == 422
    )
    assigned = client.patch(
        f"/api/v1/departments/{department.id}",
        headers=headers(tokens, tenant_a.id),
        json={"manager_employee_id": employee_a.id},
    )
    assert assigned.status_code == 200 and assigned.json()["manager_employee_id"] == employee_a.id
    assert (
        client.get("/api/v1/employees?limit=101", headers=headers(tokens, tenant_a.id)).status_code
        == 422
    )


def test_employee_lifecycle_controls_linked_tenant_membership(
    client: TestClient, db: Session, seeded: dict[str, object]
) -> None:
    tenant = seeded["tenant_a"]
    viewer = seeded["viewer"]
    membership = seeded["member_viewer"]
    employee = Employee(
        tenant_id=tenant.id,
        user_id=viewer.id,
        employee_number="A-LINKED",
        full_name="Linked User",
        work_email=viewer.email,
    )
    db.add(employee)
    db.commit()
    tokens = login(client)
    suspended = client.post(
        f"/api/v1/employees/{employee.id}/suspend", headers=headers(tokens, tenant.id)
    )
    assert suspended.status_code == 200
    db.refresh(membership)
    assert membership.is_active is False
    reactivated = client.post(
        f"/api/v1/employees/{employee.id}/reactivate", headers=headers(tokens, tenant.id)
    )
    assert reactivated.status_code == 200
    db.refresh(membership)
    assert membership.is_active is True
