import os

os.environ["DWCO_DATABASE_URL"] = "sqlite:///./test.db"
os.environ["DWCO_REDIS_URL"] = "redis://localhost:6379/15"
os.environ["DWCO_JWT_SECRET"] = "test-secret-that-is-long-and-never-production"

import pytest
import redis
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Membership, Permission, Role, Tenant, User
from app.security import hash_password

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
def unavailable_rate_limit_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    def unavailable(*args: object, **kwargs: object) -> None:
        raise redis.ConnectionError("test Redis unavailable")

    monkeypatch.setattr("app.rate_limit.redis.from_url", unavailable)


@pytest.fixture
def db() -> Session:
    Base.metadata.create_all(engine)
    with TestingSession() as session:
        yield session
    Base.metadata.drop_all(engine)


@pytest.fixture
def seeded(db: Session) -> dict[str, object]:
    permission_codes = [
        "tenant.owner",
        "tenant.admin",
        "employee.read",
        "employee.create",
        "employee.update",
        "employee.suspend",
        "department.manage",
        "role.manage",
        "audit.read",
        "security.read",
    ]
    permissions = [Permission(code=code) for code in permission_codes]
    tenant_a, tenant_b = Tenant(slug="alpha", name="Alpha"), Tenant(slug="beta", name="Beta")
    owner = User(email="owner@example.com", password_hash=hash_password("correct-password"))
    viewer = User(email="viewer@example.com", password_hash=hash_password("correct-password"))
    db.add_all([*permissions, tenant_a, tenant_b, owner, viewer])
    db.flush()
    role_owner = Role(tenant_id=tenant_a.id, name="Owner", permissions=permissions)
    role_viewer = Role(tenant_id=tenant_a.id, name="Viewer", permissions=[permissions[2]])
    member_owner = Membership(tenant_id=tenant_a.id, user_id=owner.id, roles=[role_owner])
    member_viewer = Membership(tenant_id=tenant_a.id, user_id=viewer.id, roles=[role_viewer])
    role_b = Role(tenant_id=tenant_b.id, name="Owner", permissions=permissions)
    member_b = Membership(tenant_id=tenant_b.id, user_id=owner.id, roles=[role_b])
    db.add_all([role_owner, role_viewer, role_b, member_owner, member_viewer, member_b])
    db.commit()
    return {
        "tenant_a": tenant_a,
        "tenant_b": tenant_b,
        "owner": owner,
        "viewer": viewer,
        "member_owner": member_owner,
        "member_viewer": member_viewer,
        "member_b": member_b,
        "role_owner": role_owner,
    }


@pytest.fixture
def client(db: Session, seeded: dict[str, object]) -> TestClient:
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def login(
    client: TestClient, email: str = "owner@example.com", password: str = "correct-password"
) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()
