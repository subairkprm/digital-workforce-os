from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.config import get_settings
from app.database import get_db
from app.dependencies import RequestContext, require_permission
from app.models import AuditEvent, Employee, Invitation, Membership, Role, User
from app.rate_limit import enforce_rate_limit
from app.schemas import InvitationAccept, InvitationCreate, InvitationOut, RoleOut
from app.security import digest_token, hash_password

router = APIRouter(prefix="/invitations", tags=["invitations"])


def invitation_out(invitation: Invitation, token: str | None = None) -> InvitationOut:
    return InvitationOut(
        id=invitation.id,
        email=invitation.email,
        role_ids=list(invitation.role_ids),
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
        revoked_at=invitation.revoked_at,
        created_at=invitation.created_at,
        token=token,
    )


@router.get("", response_model=list[InvitationOut])
def list_invitations(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("membership.manage"))],
) -> list[InvitationOut]:
    invitations = db.scalars(
        select(Invitation)
        .where(Invitation.tenant_id == context.tenant_id)
        .order_by(Invitation.created_at.desc())
        .limit(100)
    )
    return [invitation_out(invitation) for invitation in invitations]


@router.get("/available-roles", response_model=list[RoleOut])
def available_invitation_roles(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("membership.manage"))],
) -> list[RoleOut]:
    roles = db.scalars(
        select(Role).where(Role.tenant_id == context.tenant_id).order_by(Role.name, Role.id)
    )
    return [
        RoleOut(
            id=role.id,
            name=role.name,
            permissions=sorted(permission.code for permission in role.permissions),
        )
        for role in roles
    ]


@router.post("", response_model=InvitationOut, status_code=status.HTTP_201_CREATED)
def create_invitation(
    payload: InvitationCreate,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("membership.manage"))],
) -> InvitationOut:
    enforce_rate_limit(
        "tenant-mutation",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    email = payload.email.lower()
    if db.scalar(select(User.id).where(func.lower(User.email) == email)) is not None:
        raise HTTPException(status_code=409, detail="user already exists")
    role_ids = sorted(set(payload.role_ids))
    roles = list(
        db.scalars(
            select(Role.id).where(Role.id.in_(role_ids), Role.tenant_id == context.tenant_id)
        )
    )
    if len(roles) != len(role_ids):
        raise HTTPException(status_code=422, detail="invalid role")
    now = datetime.now(timezone.utc)
    db.query(Invitation).filter(
        Invitation.tenant_id == context.tenant_id,
        func.lower(Invitation.email) == email,
        Invitation.accepted_at.is_(None),
        Invitation.revoked_at.is_(None),
    ).update({Invitation.revoked_at: now}, synchronize_session=False)
    raw_token = secrets.token_urlsafe(48)
    invitation = Invitation(
        tenant_id=context.tenant_id,
        email=email,
        token_digest=digest_token(raw_token),
        role_ids=role_ids,
        invited_by_user_id=context.user.id,
        expires_at=now + timedelta(days=payload.expires_in_days),
    )
    db.add(invitation)
    db.flush()
    record_audit(db, context, "invitation.created", "invitation", invitation.id, {"email": email})
    db.commit()
    db.refresh(invitation)
    return invitation_out(invitation, raw_token)


@router.delete("/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invitation(
    invitation_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("membership.manage"))],
) -> None:
    invitation = db.scalar(
        select(Invitation).where(
            Invitation.id == invitation_id, Invitation.tenant_id == context.tenant_id
        )
    )
    if invitation is None:
        raise HTTPException(status_code=404, detail="invitation not found")
    if invitation.accepted_at is not None:
        raise HTTPException(status_code=409, detail="invitation already accepted")
    invitation.revoked_at = datetime.now(timezone.utc)
    record_audit(db, context, "invitation.revoked", "invitation", invitation.id)
    db.commit()


@router.post("/accept", status_code=status.HTTP_204_NO_CONTENT)
def accept_invitation(
    payload: InvitationAccept,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    remote_host = request.client.host if request.client else "unknown"
    enforce_rate_limit(
        "invitation-accept",
        f"{remote_host}:{digest_token(payload.token)[:16]}",
        get_settings().auth_rate_limit,
    )
    invitation = db.scalar(
        select(Invitation).where(Invitation.token_digest == digest_token(payload.token))
    )
    now = datetime.now(timezone.utc)
    if (
        invitation is None
        or invitation.revoked_at is not None
        or invitation.accepted_at is not None
    ):
        raise HTTPException(status_code=400, detail="invalid invitation")
    expires_at = invitation.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise HTTPException(status_code=400, detail="invitation expired")
    if db.scalar(select(User.id).where(func.lower(User.email) == invitation.email)) is not None:
        raise HTTPException(status_code=409, detail="user already exists")
    roles = list(
        db.scalars(
            select(Role).where(
                Role.id.in_(invitation.role_ids), Role.tenant_id == invitation.tenant_id
            )
        )
    )
    if len(roles) != len(set(invitation.role_ids)):
        raise HTTPException(status_code=400, detail="invitation roles are no longer valid")
    user = User(email=invitation.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    membership = Membership(tenant_id=invitation.tenant_id, user_id=user.id, roles=roles)
    db.add(membership)
    db.flush()
    employee = db.scalar(
        select(Employee).where(
            Employee.tenant_id == invitation.tenant_id,
            func.lower(Employee.work_email) == invitation.email,
            Employee.user_id.is_(None),
        )
    )
    if employee is not None:
        employee.user_id = user.id
    invitation.accepted_at = now
    db.add(
        AuditEvent(
            tenant_id=invitation.tenant_id,
            actor_user_id=user.id,
            action="invitation.accepted",
            resource_type="invitation",
            resource_id=invitation.id,
            details={"membership_id": membership.id},
        )
    )
    db.commit()
