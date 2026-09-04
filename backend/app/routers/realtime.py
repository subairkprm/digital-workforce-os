from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.dependencies import Context
from app.models import Membership, Tenant, User
from app.rate_limit import enforce_rate_limit
from app.realtime import (
    InvalidRealtimeTicket,
    RealtimeClaims,
    RealtimeStoreUnavailable,
    consume_realtime_ticket,
    issue_realtime_ticket,
    realtime_hub,
)
from app.schemas import RealtimeTicketOut
from app.security_events import record_security_event

router = APIRouter(prefix="/realtime", tags=["realtime"])
logger = logging.getLogger(__name__)
MAX_FRAME_BYTES = 8 * 1024


def authorize_realtime_claims(
    claims: RealtimeClaims,
    session_factory: Optional[Callable[[], Session]] = None,
) -> Optional[frozenset[str]]:
    """Authorize a ticket in a short session that ends before socket acceptance."""
    factory = session_factory or SessionLocal
    with factory() as db:
        tenant = db.get(Tenant, claims.tenant_id)
        user = db.get(User, claims.user_id)
        membership = db.scalar(
            select(Membership).where(
                Membership.id == claims.membership_id,
                Membership.tenant_id == claims.tenant_id,
                Membership.user_id == claims.user_id,
                Membership.is_active.is_(True),
            )
        )
        if tenant is None or not tenant.is_active or user is None or not user.is_active:
            record_security_event(
                db,
                "realtime.authorization",
                "denied",
                tenant_id=claims.tenant_id if tenant is not None else None,
                actor_user_id=claims.user_id if user is not None else None,
                metadata={"reason": "inactive_context"},
            )
            db.commit()
            return None
        if membership is None:
            record_security_event(
                db,
                "realtime.authorization",
                "denied",
                tenant_id=claims.tenant_id,
                actor_user_id=claims.user_id,
                metadata={"reason": "inactive_membership"},
            )
            db.commit()
            return None
        return frozenset(
            permission.code for role in membership.roles for permission in role.permissions
        )


@router.post("/tickets", response_model=RealtimeTicketOut)
def create_ticket(context: Context) -> RealtimeTicketOut:
    enforce_rate_limit(
        "realtime-ticket",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().realtime_ticket_rate_limit,
    )
    try:
        ticket, ttl = issue_realtime_ticket(context)
    except RealtimeStoreUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="realtime temporarily unavailable",
        ) from exc
    return RealtimeTicketOut(ticket=ticket, expires_in_seconds=ttl)


@router.websocket("/ws")
async def realtime_socket(
    websocket: WebSocket,
    ticket: Annotated[str, Query(min_length=32, max_length=256)],
) -> None:
    try:
        claims = consume_realtime_ticket(ticket)
    except InvalidRealtimeTicket:
        logger.warning("realtime.ticket_rejected reason=invalid_or_expired")
        await websocket.close(code=4401, reason="invalid or expired ticket")
        return
    except RealtimeStoreUnavailable:
        logger.warning("realtime.ticket_rejected reason=store_unavailable")
        await websocket.close(code=1013, reason="realtime temporarily unavailable")
        return

    permissions = authorize_realtime_claims(claims)
    if permissions is None:
        await websocket.close(code=4403, reason="membership inactive")
        return

    connection = await realtime_hub.connect(
        websocket,
        tenant_id=claims.tenant_id,
        user_id=claims.user_id,
        permissions=permissions,
        revalidate=lambda: authorize_realtime_claims(claims),
    )
    await realtime_hub.send(
        connection,
        {
            "type": "realtime.ready",
            "tenant_id": claims.tenant_id,
            "user_id": claims.user_id,
        },
    )
    logger.info(
        "realtime.connected tenant_id=%s user_id=%s",
        claims.tenant_id,
        claims.user_id,
    )
    try:
        while True:
            frame = await websocket.receive_text()
            if len(frame.encode()) > MAX_FRAME_BYTES:
                await websocket.close(code=1009, reason="frame too large")
                break
            try:
                payload = json.loads(frame)
            except json.JSONDecodeError:
                await realtime_hub.send(connection, {"type": "error", "code": "invalid_json"})
                continue
            if not isinstance(payload, dict) or payload.get("type") != "ping":
                await realtime_hub.send(connection, {"type": "error", "code": "unsupported"})
                continue
            await realtime_hub.send(connection, {"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        await realtime_hub.disconnect(connection)
        logger.info(
            "realtime.disconnected tenant_id=%s user_id=%s",
            claims.tenant_id,
            claims.user_id,
        )
