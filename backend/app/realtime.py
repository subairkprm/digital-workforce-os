from __future__ import annotations

import asyncio
import hashlib
import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional, cast

import redis
from fastapi import WebSocket

from app.config import get_settings
from app.dependencies import RequestContext

MAX_OUTBOUND_EVENTS = 100


class RealtimeStoreUnavailable(RuntimeError):
    pass


class InvalidRealtimeTicket(ValueError):
    pass


@dataclass(frozen=True)
class RealtimeClaims:
    tenant_id: str
    user_id: str
    membership_id: str


def _ticket_key(raw: str) -> str:
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return f"dwco:realtime:ticket:{digest}"


def issue_realtime_ticket(context: RequestContext) -> tuple[str, int]:
    settings = get_settings()
    raw = secrets.token_urlsafe(48)
    value = json.dumps(
        {
            "tenant_id": context.tenant_id,
            "user_id": context.user.id,
            "membership_id": context.membership.id,
        },
        separators=(",", ":"),
    )
    try:
        client = redis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
        )
        stored = client.set(
            _ticket_key(raw),
            value,
            ex=settings.realtime_ticket_ttl_seconds,
            nx=True,
        )
    except redis.RedisError as exc:
        raise RealtimeStoreUnavailable("realtime ticket store unavailable") from exc
    if not stored:
        raise RealtimeStoreUnavailable("realtime ticket could not be reserved")
    return raw, settings.realtime_ticket_ttl_seconds


def consume_realtime_ticket(raw: str) -> RealtimeClaims:
    if len(raw) < 32 or len(raw) > 256:
        raise InvalidRealtimeTicket("invalid realtime ticket")
    try:
        client = redis.from_url(  # type: ignore[no-untyped-call]
            get_settings().redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
        )
        value = client.getdel(_ticket_key(raw))
    except redis.RedisError as exc:
        raise RealtimeStoreUnavailable("realtime ticket store unavailable") from exc
    if value is None:
        raise InvalidRealtimeTicket("invalid or expired realtime ticket")
    try:
        payload = cast(dict[str, Any], json.loads(value))
        tenant_id = str(payload["tenant_id"])
        user_id = str(payload["user_id"])
        membership_id = str(payload["membership_id"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise InvalidRealtimeTicket("invalid realtime ticket") from exc
    if not all(len(identifier) == 36 for identifier in (tenant_id, user_id, membership_id)):
        raise InvalidRealtimeTicket("invalid realtime ticket")
    return RealtimeClaims(
        tenant_id=tenant_id,
        user_id=user_id,
        membership_id=membership_id,
    )


@dataclass(eq=False)
class RealtimeConnection:
    websocket: WebSocket
    tenant_id: str
    user_id: str
    permissions: frozenset[str]
    queue: asyncio.Queue[dict[str, object]]
    revalidate: Optional[Callable[[], Optional[frozenset[str]]]] = None
    sender_task: Optional[asyncio.Task[None]] = None


class RealtimeHub:
    """Local fan-out boundary; a shared broker adapter is required before deployment."""

    def __init__(self) -> None:
        self._connections: set[RealtimeConnection] = set()

    async def connect(
        self,
        websocket: WebSocket,
        *,
        tenant_id: str,
        user_id: str,
        permissions: frozenset[str],
        revalidate: Optional[Callable[[], Optional[frozenset[str]]]] = None,
    ) -> RealtimeConnection:
        await websocket.accept()
        connection = RealtimeConnection(
            websocket=websocket,
            tenant_id=tenant_id,
            user_id=user_id,
            permissions=permissions,
            queue=asyncio.Queue(maxsize=MAX_OUTBOUND_EVENTS),
            revalidate=revalidate,
        )
        self._connections.add(connection)
        connection.sender_task = asyncio.create_task(self._sender(connection))
        return connection

    async def disconnect(self, connection: RealtimeConnection) -> None:
        self._connections.discard(connection)
        task = connection.sender_task
        if task is not None and task is not asyncio.current_task():
            task.cancel()
        try:
            await connection.websocket.close()
        except RuntimeError:
            pass

    async def publish_users(
        self,
        tenant_id: str,
        user_ids: set[str],
        event: dict[str, object],
    ) -> None:
        for connection in list(self._connections):
            if connection.tenant_id != tenant_id or connection.user_id not in user_ids:
                continue
            if await self._refresh_authorization(connection):
                await self.send(connection, event)

    async def publish_tenant(
        self,
        tenant_id: str,
        event: dict[str, object],
        *,
        permission: Optional[str] = None,
        include_user_ids: Optional[set[str]] = None,
    ) -> None:
        included = include_user_ids or set()
        for connection in list(self._connections):
            if connection.tenant_id != tenant_id:
                continue
            if not await self._refresh_authorization(connection):
                continue
            if (
                permission is None
                or permission in connection.permissions
                or "tenant.owner" in connection.permissions
                or connection.user_id in included
            ):
                await self.send(connection, event)

    async def send(self, connection: RealtimeConnection, event: dict[str, object]) -> None:
        try:
            connection.queue.put_nowait(event)
        except asyncio.QueueFull:
            await self.disconnect(connection)

    async def _refresh_authorization(self, connection: RealtimeConnection) -> bool:
        if connection.revalidate is None:
            return True
        permissions = await asyncio.to_thread(connection.revalidate)
        if permissions is None:
            await self.disconnect(connection)
            return False
        connection.permissions = permissions
        return True

    async def _sender(self, connection: RealtimeConnection) -> None:
        try:
            while True:
                event = await connection.queue.get()
                await connection.websocket.send_json(event)
        except (RuntimeError, asyncio.CancelledError):
            self._connections.discard(connection)


realtime_hub = RealtimeHub()
