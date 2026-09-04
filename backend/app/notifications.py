from __future__ import annotations

from typing import Protocol


class NotificationAdapter(Protocol):
    def notify_message_available(
        self,
        *,
        tenant_id: str,
        recipient_user_ids: set[str],
        conversation_id: str,
        message_id: str,
    ) -> None: ...


class NullNotificationAdapter:
    """Local provider-neutral boundary. It intentionally sends nothing."""

    def notify_message_available(
        self,
        *,
        tenant_id: str,
        recipient_user_ids: set[str],
        conversation_id: str,
        message_id: str,
    ) -> None:
        del tenant_id, recipient_user_ids, conversation_id, message_id


notification_adapter: NotificationAdapter = NullNotificationAdapter()
