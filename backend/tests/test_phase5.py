from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import Any, cast

import pytest
import redis
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from app.models import AuditEvent, Conversation, Message, utcnow
from app.realtime import MAX_OUTBOUND_EVENTS, RealtimeConnection, RealtimeHub
from tests.conftest import login
from tests.test_phase1 import headers


class FakeTicketRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.counts: dict[str, int] = {}

    def set(self, key: str, value: str, *, ex: int, nx: bool) -> bool:
        del ex
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    def getdel(self, key: str) -> str | None:
        return self.values.pop(key, None)

    def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    def expire(self, key: str, seconds: int) -> bool:
        del key, seconds
        return True


class SpyNotificationAdapter:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def notify_message_available(self, **kwargs: object) -> None:
        self.calls.append(kwargs)


class FailingNotificationAdapter:
    def notify_message_available(self, **kwargs: object) -> None:
        del kwargs
        raise RuntimeError("simulated provider failure")


def create_conversation(
    client: TestClient,
    tokens: dict[str, str],
    tenant_id: str,
    participant_user_id: str,
) -> dict[str, object]:
    response = client.post(
        "/api/v1/messaging/conversations/direct",
        headers=headers(tokens, tenant_id),
        json={"participant_user_id": participant_user_id},
    )
    assert response.status_code == 200
    return cast(dict[str, object], response.json())


def test_direct_conversations_are_deduplicated_and_tenant_scoped(
    client: TestClient, seeded: dict[str, Any]
) -> None:
    owner_tokens = login(client)
    tenant_a, tenant_b = seeded["tenant_a"], seeded["tenant_b"]
    owner, viewer = seeded["owner"], seeded["viewer"]

    conversation = create_conversation(client, owner_tokens, tenant_a.id, viewer.id)
    duplicate = create_conversation(client, owner_tokens, tenant_a.id, viewer.id)
    assert duplicate["id"] == conversation["id"]
    assert conversation["participant_user_ids"] == sorted([owner.id, viewer.id])

    assert (
        client.post(
            "/api/v1/messaging/conversations/direct",
            headers=headers(owner_tokens, tenant_a.id),
            json={"participant_user_id": owner.id},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/messaging/conversations/direct",
            headers=headers(owner_tokens, tenant_b.id),
            json={"participant_user_id": viewer.id},
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/api/v1/messaging/conversations/{conversation['id']}/messages",
            headers=headers(owner_tokens, tenant_b.id),
        ).status_code
        == 404
    )

    viewer_tokens = login(client, email=viewer.email)
    listed = client.get(
        "/api/v1/messaging/conversations",
        headers=headers(viewer_tokens, tenant_a.id),
    )
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [conversation["id"]]
    assert (
        client.get(
            "/api/v1/messaging/conversations?limit=51",
            headers=headers(viewer_tokens, tenant_a.id),
        ).status_code
        == 422
    )


def test_message_ordering_idempotency_receipts_and_redaction(
    client: TestClient,
    db: Session,
    seeded: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = seeded["tenant_a"]
    viewer = seeded["viewer"]
    owner_tokens = login(client)
    viewer_tokens = login(client, email=viewer.email)
    conversation = create_conversation(client, owner_tokens, tenant.id, viewer.id)
    conversation_id = str(conversation["id"])
    notification_adapter = SpyNotificationAdapter()
    monkeypatch.setattr("app.routers.messaging.notification_adapter", notification_adapter)

    first = client.post(
        f"/api/v1/messaging/conversations/{conversation_id}/messages",
        headers=headers(owner_tokens, tenant.id),
        json={"client_message_id": "mobile-0001", "body": "Hello"},
    )
    assert first.status_code == 201
    assert first.json()["sequence_number"] == 1
    assert len(notification_adapter.calls) == 1
    assert "body" not in notification_adapter.calls[0]
    duplicate = client.post(
        f"/api/v1/messaging/conversations/{conversation_id}/messages",
        headers=headers(owner_tokens, tenant.id),
        json={"client_message_id": "mobile-0001", "body": "Hello"},
    )
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == first.json()["id"]
    assert (
        client.post(
            f"/api/v1/messaging/conversations/{conversation_id}/messages",
            headers=headers(owner_tokens, tenant.id),
            json={"client_message_id": "mobile-0001", "body": "Changed"},
        ).status_code
        == 409
    )
    second = client.post(
        f"/api/v1/messaging/conversations/{conversation_id}/messages",
        headers=headers(viewer_tokens, tenant.id),
        json={"client_message_id": "mobile-0002", "body": "Reply"},
    )
    assert second.status_code == 201
    assert second.json()["sequence_number"] == 2

    read = client.post(
        f"/api/v1/messaging/conversations/{conversation_id}/messages/{first.json()['id']}/read",
        headers=headers(viewer_tokens, tenant.id),
    )
    assert read.status_code == 200
    assert read.json()["user_id"] == viewer.id
    history = client.get(
        f"/api/v1/messaging/conversations/{conversation_id}/messages",
        headers=headers(owner_tokens, tenant.id),
    )
    assert [item["sequence_number"] for item in history.json()] == [1, 2]
    assert history.json()[0]["read_by_user_ids"] == [viewer.id]
    assert (
        client.get(
            f"/api/v1/messaging/conversations/{conversation_id}/messages?limit=101",
            headers=headers(owner_tokens, tenant.id),
        ).status_code
        == 422
    )

    assert (
        client.delete(
            f"/api/v1/messaging/conversations/{conversation_id}/messages/{first.json()['id']}",
            headers=headers(viewer_tokens, tenant.id),
        ).status_code
        == 403
    )
    redacted = client.delete(
        f"/api/v1/messaging/conversations/{conversation_id}/messages/{first.json()['id']}",
        headers=headers(owner_tokens, tenant.id),
    )
    assert redacted.status_code == 200
    assert redacted.json()["body"] is None
    stored = db.get(Message, first.json()["id"])
    assert stored is not None and stored.body == "[deleted]"


def test_retention_metrics_and_permissioned_purge(
    client: TestClient, db: Session, seeded: dict[str, Any]
) -> None:
    tenant = seeded["tenant_a"]
    viewer = seeded["viewer"]
    owner_tokens = login(client)
    viewer_tokens = login(client, email=viewer.email)
    conversation = create_conversation(client, owner_tokens, tenant.id, viewer.id)
    conversation_id = str(conversation["id"])
    sent = client.post(
        f"/api/v1/messaging/conversations/{conversation_id}/messages",
        headers=headers(owner_tokens, tenant.id),
        json={"client_message_id": "retention-0001", "body": "Expires"},
    )
    message = db.get(Message, sent.json()["id"])
    assert message is not None
    message.expires_at = utcnow() - timedelta(seconds=1)
    db.commit()

    assert (
        client.post(
            f"/api/v1/messaging/conversations/{conversation_id}/messages",
            headers=headers(owner_tokens, tenant.id),
            json={"client_message_id": "retention-0001", "body": "Expires"},
        ).status_code
        == 410
    )

    history = client.get(
        f"/api/v1/messaging/conversations/{conversation_id}/messages",
        headers=headers(owner_tokens, tenant.id),
    )
    assert history.json() == []
    assert (
        client.get(
            "/api/v1/messaging/admin/metrics",
            headers=headers(viewer_tokens, tenant.id),
        ).status_code
        == 403
    )
    metrics = client.get(
        "/api/v1/messaging/admin/metrics",
        headers=headers(owner_tokens, tenant.id),
    )
    assert metrics.status_code == 200
    assert metrics.json()["expired_message_count"] == 1
    purged = client.post(
        "/api/v1/messaging/admin/retention/purge",
        headers=headers(owner_tokens, tenant.id),
    )
    assert purged.json() == {"purged_messages": 1}
    assert db.get(Message, sent.json()["id"]) is None
    stored_conversation = db.get(Conversation, conversation_id)
    assert stored_conversation is not None and stored_conversation.last_message_at is None
    audit = db.scalar(select(AuditEvent).where(AuditEvent.action == "message.retention.purge"))
    assert audit is not None and audit.details == {"purged_messages": 1}


def test_notification_failure_does_not_change_durable_send_result(
    client: TestClient,
    seeded: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = seeded["tenant_a"]
    viewer = seeded["viewer"]
    owner_tokens = login(client)
    conversation = create_conversation(client, owner_tokens, tenant.id, viewer.id)
    monkeypatch.setattr("app.routers.messaging.notification_adapter", FailingNotificationAdapter())

    sent = client.post(
        f"/api/v1/messaging/conversations/{conversation['id']}/messages",
        headers=headers(owner_tokens, tenant.id),
        json={"client_message_id": "provider-failure-0001", "body": "Still durable"},
    )
    assert sent.status_code == 201
    assert sent.json()["body"] == "Still durable"


def test_blank_body_and_send_rate_limit_are_rejected(
    client: TestClient, seeded: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    tenant = seeded["tenant_a"]
    viewer = seeded["viewer"]
    owner_tokens = login(client)
    conversation = create_conversation(client, owner_tokens, tenant.id, viewer.id)
    path = f"/api/v1/messaging/conversations/{conversation['id']}/messages"
    assert (
        client.post(
            path,
            headers=headers(owner_tokens, tenant.id),
            json={"client_message_id": "blank-0001", "body": "   "},
        ).status_code
        == 422
    )

    def limited(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    monkeypatch.setattr("app.routers.messaging.enforce_rate_limit", limited)
    assert (
        client.post(
            path,
            headers=headers(owner_tokens, tenant.id),
            json={"client_message_id": "limited-0001", "body": "Blocked"},
        ).status_code
        == 429
    )


def test_realtime_ticket_is_one_time_and_membership_is_revalidated(
    client: TestClient,
    db: Session,
    seeded: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ticket_redis = FakeTicketRedis()
    monkeypatch.setattr("app.realtime.redis.from_url", lambda *args, **kwargs: ticket_redis)
    tenant = seeded["tenant_a"]
    tokens = login(client)
    response = client.post("/api/v1/realtime/tickets", headers=headers(tokens, tenant.id))
    assert response.status_code == 200
    ticket = response.json()["ticket"]
    with client.websocket_connect(f"/api/v1/realtime/ws?ticket={ticket}") as socket:
        assert socket.receive_json()["type"] == "realtime.ready"
        socket.send_json({"type": "ping"})
        assert socket.receive_json() == {"type": "pong"}
        socket.send_json({"type": "message.send", "body": "not allowed"})
        assert socket.receive_json() == {"type": "error", "code": "unsupported"}

    with pytest.raises(WebSocketDisconnect) as reused:
        with client.websocket_connect(f"/api/v1/realtime/ws?ticket={ticket}") as socket:
            socket.receive_json()
    assert reused.value.code == 4401

    oversized_ticket = client.post(
        "/api/v1/realtime/tickets", headers=headers(tokens, tenant.id)
    ).json()["ticket"]
    with client.websocket_connect(f"/api/v1/realtime/ws?ticket={oversized_ticket}") as socket:
        assert socket.receive_json()["type"] == "realtime.ready"
        socket.send_text("x" * (8 * 1024 + 1))
        with pytest.raises(WebSocketDisconnect) as oversized:
            socket.receive_json()
        assert oversized.value.code == 1009

    expired_ticket = client.post(
        "/api/v1/realtime/tickets", headers=headers(tokens, tenant.id)
    ).json()["ticket"]
    ticket_redis.values.clear()
    with pytest.raises(WebSocketDisconnect) as expired:
        with client.websocket_connect(f"/api/v1/realtime/ws?ticket={expired_ticket}") as socket:
            socket.receive_json()
    assert expired.value.code == 4401

    new_ticket = client.post("/api/v1/realtime/tickets", headers=headers(tokens, tenant.id)).json()[
        "ticket"
    ]
    seeded["member_owner"].is_active = False
    db.commit()
    with pytest.raises(WebSocketDisconnect) as inactive:
        with client.websocket_connect(f"/api/v1/realtime/ws?ticket={new_ticket}") as socket:
            socket.receive_json()
    assert inactive.value.code == 4403


def test_realtime_ticket_store_failure_is_not_bypassed(
    client: TestClient, seeded: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def unavailable(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise redis.ConnectionError("unavailable")

    monkeypatch.setattr("app.realtime.redis.from_url", unavailable)
    tokens = login(client)
    response = client.post(
        "/api/v1/realtime/tickets",
        headers=headers(tokens, seeded["tenant_a"].id),
    )
    assert response.status_code == 503


class FakeWebSocket:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def test_realtime_backpressure_disconnects_slow_connections() -> None:
    async def exercise() -> None:
        websocket = FakeWebSocket()
        connection = RealtimeConnection(
            websocket=cast(Any, websocket),
            tenant_id="tenant",
            user_id="user",
            permissions=frozenset(),
            queue=asyncio.Queue(maxsize=MAX_OUTBOUND_EVENTS),
        )
        hub = RealtimeHub()
        hub._connections.add(connection)
        for index in range(MAX_OUTBOUND_EVENTS):
            connection.queue.put_nowait({"index": index})
        await hub.send(connection, {"overflow": True})
        assert websocket.closed is True
        assert connection not in hub._connections

    asyncio.run(exercise())


def test_realtime_fanout_is_tenant_user_and_permission_scoped() -> None:
    async def exercise() -> None:
        hub = RealtimeHub()

        def connection(
            tenant_id: str, user_id: str, permissions: frozenset[str]
        ) -> RealtimeConnection:
            return RealtimeConnection(
                websocket=cast(Any, FakeWebSocket()),
                tenant_id=tenant_id,
                user_id=user_id,
                permissions=permissions,
                queue=asyncio.Queue(maxsize=MAX_OUTBOUND_EVENTS),
            )

        target = connection("tenant-a", "user-a", frozenset({"employee.read"}))
        other_user = connection("tenant-a", "user-b", frozenset())
        other_tenant = connection("tenant-b", "user-a", frozenset({"employee.read"}))
        hub._connections.update({target, other_user, other_tenant})

        await hub.publish_users("tenant-a", {"user-a"}, {"type": "message.created"})
        assert target.queue.qsize() == 1
        assert other_user.queue.empty()
        assert other_tenant.queue.empty()
        target.queue.get_nowait()

        await hub.publish_tenant(
            "tenant-a",
            {"type": "presence.updated"},
            permission="employee.read",
        )
        assert target.queue.qsize() == 1
        assert other_user.queue.empty()
        assert other_tenant.queue.empty()

    asyncio.run(exercise())
