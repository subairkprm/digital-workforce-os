from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.config import get_settings
from app.database import get_db
from app.dependencies import RequestContext, require_permission
from app.models import Membership, Permission, Role, membership_roles
from app.rate_limit import enforce_rate_limit
from app.schemas import MembershipOut, MembershipRoleUpdate, RoleCreate, RoleOut, RolePatch

router = APIRouter(tags=["roles"])


def role_out(role: Role) -> RoleOut:
    return RoleOut(id=role.id, name=role.name, permissions=sorted(p.code for p in role.permissions))


def resolve_permissions(db: Session, codes: list[str]) -> list[Permission]:
    unique_codes = sorted(set(codes))
    permissions = list(db.scalars(select(Permission).where(Permission.code.in_(unique_codes))))
    if len(permissions) != len(unique_codes):
        raise HTTPException(status_code=422, detail="unknown permission")
    return permissions


@router.get("/roles", response_model=list[RoleOut])
def list_roles(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("role.manage"))],
) -> list[RoleOut]:
    return [
        role_out(role)
        for role in db.scalars(select(Role).where(Role.tenant_id == context.tenant_id))
    ]


@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    payload: RoleCreate,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("role.manage"))],
) -> RoleOut:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    role = Role(
        tenant_id=context.tenant_id,
        name=payload.name,
        permissions=resolve_permissions(db, payload.permissions),
    )
    db.add(role)
    db.flush()
    record_audit(db, context, "role.created", "role", role.id, {"permissions": payload.permissions})
    db.commit()
    db.refresh(role)
    return role_out(role)


@router.patch("/roles/{role_id}", response_model=RoleOut)
def update_role(
    role_id: str,
    payload: RolePatch,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("role.manage"))],
) -> RoleOut:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    role = db.scalar(select(Role).where(Role.id == role_id, Role.tenant_id == context.tenant_id))
    if role is None:
        raise HTTPException(status_code=404, detail="role not found")
    changes = payload.model_dump(exclude_unset=True)
    if payload.name is not None:
        role.name = payload.name
    if payload.permissions is not None:
        role.permissions = resolve_permissions(db, payload.permissions)
    record_audit(db, context, "role.updated", "role", role.id, {"fields": sorted(changes)})
    db.commit()
    db.refresh(role)
    return role_out(role)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("role.manage"))],
) -> None:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    role = db.scalar(select(Role).where(Role.id == role_id, Role.tenant_id == context.tenant_id))
    if role is None:
        raise HTTPException(status_code=404, detail="role not found")
    assigned = db.scalar(
        select(membership_roles.c.membership_id)
        .where(membership_roles.c.role_id == role.id)
        .limit(1)
    )
    if assigned is not None:
        raise HTTPException(status_code=409, detail="role is assigned")
    record_audit(db, context, "role.deleted", "role", role.id, {"name": role.name})
    db.delete(role)
    db.commit()


@router.get("/memberships", response_model=list[MembershipOut])
def list_memberships(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("role.manage"))],
) -> list[MembershipOut]:
    memberships = db.scalars(select(Membership).where(Membership.tenant_id == context.tenant_id))
    return [
        MembershipOut(id=m.id, user_id=m.user_id, role_ids=[r.id for r in m.roles])
        for m in memberships
    ]


@router.put("/memberships/{membership_id}/roles", response_model=MembershipOut)
def set_membership_roles(
    membership_id: str,
    payload: MembershipRoleUpdate,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("role.manage"))],
) -> MembershipOut:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    membership = db.scalar(
        select(Membership).where(
            Membership.id == membership_id, Membership.tenant_id == context.tenant_id
        )
    )
    if membership is None:
        raise HTTPException(status_code=404, detail="membership not found")
    role_ids = sorted(set(payload.role_ids))
    roles = list(
        db.scalars(select(Role).where(Role.id.in_(role_ids), Role.tenant_id == context.tenant_id))
    )
    if len(roles) != len(role_ids):
        raise HTTPException(status_code=422, detail="invalid role")
    membership.roles = roles
    record_audit(
        db, context, "membership.roles_updated", "membership", membership.id, {"role_ids": role_ids}
    )
    db.commit()
    return MembershipOut(
        id=membership.id, user_id=membership.user_id, role_ids=[r.id for r in membership.roles]
    )
