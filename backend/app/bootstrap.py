import argparse

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Membership, Permission, Role, Tenant, User
from app.security import hash_password

PERMISSIONS = [
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


def bootstrap(tenant_slug: str, tenant_name: str, email: str, password: str) -> None:
    with SessionLocal.begin() as db:
        if db.scalar(select(Tenant).where(Tenant.slug == tenant_slug)) is not None:
            raise ValueError("tenant slug already exists")
        if db.scalar(select(User).where(User.email == email.lower())) is not None:
            raise ValueError("user email already exists")
        permissions = []
        for code in PERMISSIONS:
            permission = db.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code)
                db.add(permission)
            permissions.append(permission)
        tenant = Tenant(slug=tenant_slug, name=tenant_name)
        user = User(email=email.lower(), password_hash=hash_password(password))
        db.add_all([tenant, user])
        db.flush()
        role = Role(tenant_id=tenant.id, name="Owner", permissions=permissions)
        db.add(role)
        db.flush()
        db.add(Membership(tenant_id=tenant.id, user_id=user.id, roles=[role]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the first local DWCO tenant owner")
    parser.add_argument("--tenant-slug", required=True)
    parser.add_argument("--tenant-name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    if len(args.password) < 12:
        parser.error("password must be at least 12 characters")
    bootstrap(args.tenant_slug, args.tenant_name, args.email, args.password)


if __name__ == "__main__":
    main()
