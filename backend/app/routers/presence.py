from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import Context, RequestContext, require_permission
from app.models import Employee, Presence, utcnow
from app.rate_limit import enforce_rate_limit
from app.schemas import PresenceHeartbeat, PresenceOut, PresenceStatus, PresenceUpdate

router = APIRouter(prefix="/presence", tags=["presence"])
HEARTBEAT_TTL = timedelta(seconds=120)


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def _resolved_status(presence: Optional[Presence], now: datetime) -> PresenceStatus:
    if presence is None or presence.status == "offline" or _aware(presence.expires_at) <= now:
        return "offline"
    if presence.status == "available":
        return "available"
    if presence.status == "away":
        return "away"
    return "busy"


def _active_status(value: str) -> PresenceStatus:
    if value == "away":
        return "away"
    if value == "busy":
        return "busy"
    return "available"


def _employee_for_user(db: Session, tenant_id: str, user_id: str) -> Optional[Employee]:
    return db.scalar(
        select(Employee).where(
            Employee.tenant_id == tenant_id,
            Employee.user_id == user_id,
        )
    )


def _output(
    presence: Optional[Presence], employee: Optional[Employee], now: datetime
) -> PresenceOut:
    return PresenceOut(
        employee_id=employee.id if employee else None,
        employee_name=employee.full_name if employee else None,
        status=_resolved_status(presence, now),
        last_seen_at=presence.last_seen_at if presence else None,
        expires_at=presence.expires_at if presence else None,
    )


def _upsert(db: Session, context: RequestContext, status: PresenceStatus) -> Presence:
    now = utcnow()
    presence = db.scalar(
        select(Presence).where(
            Presence.tenant_id == context.tenant_id,
            Presence.user_id == context.user.id,
        )
    )
    expires_at = now if status == "offline" else now + HEARTBEAT_TTL
    if presence is None:
        presence = Presence(
            tenant_id=context.tenant_id,
            user_id=context.user.id,
            status=status,
            last_seen_at=now,
            expires_at=expires_at,
        )
        db.add(presence)
    else:
        presence.status = status
        presence.last_seen_at = now
        presence.expires_at = expires_at
    db.commit()
    db.refresh(presence)
    return presence


@router.get("/me", response_model=PresenceOut)
def get_my_presence(
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> PresenceOut:
    now = utcnow()
    presence = db.scalar(
        select(Presence).where(
            Presence.tenant_id == context.tenant_id,
            Presence.user_id == context.user.id,
        )
    )
    return _output(
        presence,
        _employee_for_user(db, context.tenant_id, context.user.id),
        now,
    )


@router.put("/me", response_model=PresenceOut)
def set_my_presence(
    payload: PresenceUpdate,
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> PresenceOut:
    enforce_rate_limit(
        "presence",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    presence = _upsert(db, context, payload.status)
    return _output(
        presence,
        _employee_for_user(db, context.tenant_id, context.user.id),
        utcnow(),
    )


@router.post("/me/heartbeat", response_model=PresenceOut)
def heartbeat(
    payload: PresenceHeartbeat,
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> PresenceOut:
    enforce_rate_limit(
        "presence",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().mutation_rate_limit,
    )
    existing = db.scalar(
        select(Presence).where(
            Presence.tenant_id == context.tenant_id,
            Presence.user_id == context.user.id,
        )
    )
    status: PresenceStatus = payload.status or (
        _active_status(existing.status)
        if existing is not None and existing.status != "offline"
        else "available"
    )
    presence = _upsert(db, context, status)
    return _output(
        presence,
        _employee_for_user(db, context.tenant_id, context.user.id),
        utcnow(),
    )


@router.get("", response_model=list[PresenceOut])
def list_presence(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("employee.read"))],
    q: Annotated[Optional[str], Query(max_length=160)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[PresenceOut]:
    query = select(Employee).where(Employee.tenant_id == context.tenant_id)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(
                Employee.full_name.ilike(pattern),
                Employee.work_email.ilike(pattern),
                Employee.employee_number.ilike(pattern),
            )
        )
    employees = list(
        db.scalars(query.order_by(Employee.full_name, Employee.id).offset(offset).limit(limit))
    )
    user_ids = [employee.user_id for employee in employees if employee.user_id is not None]
    presences = (
        list(
            db.scalars(
                select(Presence).where(
                    Presence.tenant_id == context.tenant_id,
                    Presence.user_id.in_(user_ids),
                )
            )
        )
        if user_ids
        else []
    )
    by_user = {presence.user_id: presence for presence in presences}
    now = utcnow()
    return [
        _output(
            by_user.get(employee.user_id) if employee.user_id is not None else None,
            employee,
            now,
        )
        for employee in employees
    ]
