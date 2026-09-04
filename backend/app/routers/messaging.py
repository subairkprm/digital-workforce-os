from __future__ import annotations

import logging
from datetime import timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit import record_audit
from app.config import get_settings
from app.database import get_db
from app.dependencies import Context, RequestContext, require_permission
from app.models import (
    Conversation,
    ConversationParticipant,
    Membership,
    Message,
    MessageReceipt,
    User,
    utcnow,
)
from app.notifications import notification_adapter
from app.rate_limit import enforce_rate_limit
from app.realtime import realtime_hub
from app.schemas import (
    ConversationOut,
    DirectConversationCreate,
    MessageCreate,
    MessageOut,
    MessageReceiptOut,
    MessagingMetricsOut,
    RetentionPurgeOut,
)
from app.security_events import record_security_event

router = APIRouter(prefix="/messaging", tags=["messaging"])
logger = logging.getLogger(__name__)


def _direct_key(first_user_id: str, second_user_id: str) -> str:
    return ":".join(sorted((first_user_id, second_user_id)))


def _participant_ids(db: Session, conversation: Conversation) -> list[str]:
    return list(
        db.scalars(
            select(ConversationParticipant.user_id)
            .where(
                ConversationParticipant.tenant_id == conversation.tenant_id,
                ConversationParticipant.conversation_id == conversation.id,
            )
            .order_by(ConversationParticipant.user_id)
        )
    )


def _conversation_out(
    db: Session, conversation: Conversation, current_user_id: str
) -> ConversationOut:
    participant_ids = _participant_ids(db, conversation)
    peer_id = next(
        (participant_id for participant_id in participant_ids if participant_id != current_user_id),
        current_user_id,
    )
    return ConversationOut(
        id=conversation.id,
        participant_user_ids=participant_ids,
        peer_user_id=peer_id,
        last_message_at=conversation.last_message_at,
        created_at=conversation.created_at,
    )


def _require_conversation(
    db: Session,
    context: RequestContext,
    conversation_id: str,
    *,
    lock: bool = False,
) -> Conversation:
    query = (
        select(Conversation)
        .join(
            ConversationParticipant,
            ConversationParticipant.conversation_id == Conversation.id,
        )
        .where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == context.tenant_id,
            ConversationParticipant.tenant_id == context.tenant_id,
            ConversationParticipant.user_id == context.user.id,
        )
    )
    if lock:
        query = query.with_for_update()
    conversation = db.scalar(query)
    if conversation is None:
        record_security_event(
            db,
            "messaging.authorization",
            "denied",
            tenant_id=context.tenant_id,
            actor_user_id=context.user.id,
            metadata={"operation": "conversation.access"},
        )
        db.commit()
        raise HTTPException(status_code=404, detail="conversation not found")
    return conversation


def _message_out(db: Session, message: Message) -> MessageOut:
    read_by = list(
        db.scalars(
            select(MessageReceipt.user_id)
            .where(
                MessageReceipt.tenant_id == message.tenant_id,
                MessageReceipt.message_id == message.id,
            )
            .order_by(MessageReceipt.user_id)
        )
    )
    return MessageOut(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_user_id=message.sender_user_id,
        client_message_id=message.client_message_id,
        sequence_number=message.sequence_number,
        body=None if message.deleted_at is not None else message.body,
        created_at=message.created_at,
        expires_at=message.expires_at,
        deleted_at=message.deleted_at,
        read_by_user_ids=read_by,
    )


def _idempotent_message(
    db: Session,
    context: RequestContext,
    conversation_id: str,
    client_message_id: str,
    body: str,
) -> Optional[MessageOut]:
    existing = db.scalar(
        select(Message).where(
            Message.tenant_id == context.tenant_id,
            Message.sender_user_id == context.user.id,
            Message.client_message_id == client_message_id,
        )
    )
    if existing is None:
        return None
    if existing.conversation_id != conversation_id:
        raise HTTPException(status_code=409, detail="client message id conflict")
    if db.scalar(
        select(Message.id).where(Message.id == existing.id, Message.expires_at <= utcnow())
    ):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="message expired")
    if existing.deleted_at is None and existing.body != body:
        raise HTTPException(status_code=409, detail="client message id conflict")
    return _message_out(db, existing)


@router.post("/conversations/direct", response_model=ConversationOut)
def create_direct_conversation(
    payload: DirectConversationCreate,
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> ConversationOut:
    if payload.participant_user_id == context.user.id:
        raise HTTPException(status_code=422, detail="direct conversation requires another member")
    participant = db.scalar(
        select(Membership)
        .join(User, User.id == Membership.user_id)
        .where(
            Membership.tenant_id == context.tenant_id,
            Membership.user_id == payload.participant_user_id,
            Membership.is_active.is_(True),
            User.is_active.is_(True),
        )
    )
    if participant is None:
        raise HTTPException(status_code=404, detail="tenant member not found")
    direct_key = _direct_key(context.user.id, payload.participant_user_id)
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.tenant_id == context.tenant_id,
            Conversation.direct_key == direct_key,
        )
    )
    if conversation is None:
        conversation = Conversation(
            tenant_id=context.tenant_id,
            kind="direct",
            direct_key=direct_key,
            created_by_user_id=context.user.id,
        )
        db.add(conversation)
        db.flush()
        db.add_all(
            [
                ConversationParticipant(
                    tenant_id=context.tenant_id,
                    conversation_id=conversation.id,
                    user_id=user_id,
                )
                for user_id in (context.user.id, payload.participant_user_id)
            ]
        )
        try:
            db.commit()
            db.refresh(conversation)
        except IntegrityError:
            db.rollback()
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.tenant_id == context.tenant_id,
                    Conversation.direct_key == direct_key,
                )
            )
            if conversation is None:
                raise
    return _conversation_out(db, conversation, context.user.id)


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Annotated[Session, Depends(get_db)],
    context: Context,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 25,
) -> list[ConversationOut]:
    conversations = list(
        db.scalars(
            select(Conversation)
            .join(
                ConversationParticipant,
                ConversationParticipant.conversation_id == Conversation.id,
            )
            .where(
                Conversation.tenant_id == context.tenant_id,
                ConversationParticipant.tenant_id == context.tenant_id,
                ConversationParticipant.user_id == context.user.id,
            )
            .order_by(
                func.coalesce(Conversation.last_message_at, Conversation.created_at).desc(),
                Conversation.id,
            )
            .offset(offset)
            .limit(limit)
        )
    )
    return [_conversation_out(db, conversation, context.user.id) for conversation in conversations]


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(
    conversation_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Context,
    before_sequence: Annotated[Optional[int], Query(ge=1)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[MessageOut]:
    conversation = _require_conversation(db, context, conversation_id)
    query = select(Message).where(
        Message.tenant_id == context.tenant_id,
        Message.conversation_id == conversation.id,
        Message.expires_at > utcnow(),
    )
    if before_sequence is not None:
        query = query.where(Message.sequence_number < before_sequence)
    messages = list(db.scalars(query.order_by(Message.sequence_number.desc()).limit(limit)))
    messages.reverse()
    return [_message_out(db, message) for message in messages]


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> MessageOut:
    enforce_rate_limit(
        "message-send",
        f"{context.tenant_id}:{context.user.id}",
        get_settings().message_send_rate_limit,
    )
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="message body must not be blank")
    existing = _idempotent_message(db, context, conversation_id, payload.client_message_id, body)
    if existing is not None:
        return existing

    conversation = _require_conversation(db, context, conversation_id, lock=True)
    existing = _idempotent_message(db, context, conversation_id, payload.client_message_id, body)
    if existing is not None:
        return existing
    next_sequence = (
        db.scalar(
            select(func.max(Message.sequence_number)).where(
                Message.conversation_id == conversation.id
            )
        )
        or 0
    ) + 1
    now = utcnow()
    message = Message(
        tenant_id=context.tenant_id,
        conversation_id=conversation.id,
        sender_user_id=context.user.id,
        client_message_id=payload.client_message_id,
        sequence_number=next_sequence,
        body=body,
        created_at=now,
        expires_at=now + timedelta(days=get_settings().message_retention_days),
    )
    conversation.last_message_at = now
    db.add(message)
    db.commit()
    db.refresh(message)
    participant_ids = set(_participant_ids(db, conversation))
    output = _message_out(db, message)
    event: dict[str, object] = {
        "type": "message.created",
        "message": output.model_dump(mode="json"),
    }
    await realtime_hub.publish_users(context.tenant_id, participant_ids, event)
    try:
        notification_adapter.notify_message_available(
            tenant_id=context.tenant_id,
            recipient_user_ids=participant_ids - {context.user.id},
            conversation_id=conversation.id,
            message_id=message.id,
        )
    except Exception:  # pragma: no cover - provider implementations are external boundaries
        logger.warning(
            "notification.delivery_failed tenant_id=%s conversation_id=%s message_id=%s",
            context.tenant_id,
            conversation.id,
            message.id,
        )
    return output


@router.post(
    "/conversations/{conversation_id}/messages/{message_id}/read",
    response_model=MessageReceiptOut,
)
async def mark_message_read(
    conversation_id: str,
    message_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> MessageReceiptOut:
    conversation = _require_conversation(db, context, conversation_id)
    message = db.scalar(
        select(Message)
        .where(
            Message.id == message_id,
            Message.tenant_id == context.tenant_id,
            Message.conversation_id == conversation.id,
            Message.expires_at > utcnow(),
        )
        .with_for_update()
    )
    if message is None:
        raise HTTPException(status_code=404, detail="message not found")
    receipt = db.scalar(
        select(MessageReceipt).where(
            MessageReceipt.tenant_id == context.tenant_id,
            MessageReceipt.message_id == message.id,
            MessageReceipt.user_id == context.user.id,
        )
    )
    if receipt is None:
        receipt = MessageReceipt(
            tenant_id=context.tenant_id,
            message_id=message.id,
            user_id=context.user.id,
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)
    output = MessageReceiptOut(
        message_id=receipt.message_id,
        user_id=receipt.user_id,
        read_at=receipt.read_at,
    )
    await realtime_hub.publish_users(
        context.tenant_id,
        set(_participant_ids(db, conversation)),
        {"type": "message.read", "receipt": output.model_dump(mode="json")},
    )
    return output


@router.delete(
    "/conversations/{conversation_id}/messages/{message_id}",
    response_model=MessageOut,
)
async def redact_message(
    conversation_id: str,
    message_id: str,
    db: Annotated[Session, Depends(get_db)],
    context: Context,
) -> MessageOut:
    conversation = _require_conversation(db, context, conversation_id)
    message = db.scalar(
        select(Message).where(
            Message.id == message_id,
            Message.tenant_id == context.tenant_id,
            Message.conversation_id == conversation.id,
        )
    )
    if message is None:
        raise HTTPException(status_code=404, detail="message not found")
    if message.sender_user_id != context.user.id:
        record_security_event(
            db,
            "messaging.authorization",
            "denied",
            tenant_id=context.tenant_id,
            actor_user_id=context.user.id,
            metadata={"operation": "message.redact"},
        )
        db.commit()
        raise HTTPException(status_code=403, detail="only the sender may redact a message")
    if message.deleted_at is None:
        message.body = "[deleted]"
        message.deleted_at = utcnow()
        db.commit()
        db.refresh(message)
    output = _message_out(db, message)
    await realtime_hub.publish_users(
        context.tenant_id,
        set(_participant_ids(db, conversation)),
        {"type": "message.redacted", "message": output.model_dump(mode="json")},
    )
    return output


@router.get("/admin/metrics", response_model=MessagingMetricsOut)
def messaging_metrics(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("message.metadata.read"))],
) -> MessagingMetricsOut:
    now = utcnow()
    conversation_count = db.scalar(
        select(func.count(Conversation.id)).where(Conversation.tenant_id == context.tenant_id)
    )
    active_count = db.scalar(
        select(func.count(Message.id)).where(
            Message.tenant_id == context.tenant_id,
            Message.expires_at > now,
        )
    )
    expired_count = db.scalar(
        select(func.count(Message.id)).where(
            Message.tenant_id == context.tenant_id,
            Message.expires_at <= now,
        )
    )
    oldest = db.scalar(
        select(func.min(Message.created_at)).where(
            Message.tenant_id == context.tenant_id,
            Message.expires_at > now,
        )
    )
    newest = db.scalar(
        select(func.max(Message.created_at)).where(Message.tenant_id == context.tenant_id)
    )
    return MessagingMetricsOut(
        conversation_count=conversation_count or 0,
        active_message_count=active_count or 0,
        expired_message_count=expired_count or 0,
        oldest_active_message_at=oldest,
        newest_message_at=newest,
    )


@router.post("/admin/retention/purge", response_model=RetentionPurgeOut)
def purge_expired_messages(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("message.retention.manage"))],
) -> RetentionPurgeOut:
    expired_ids = list(
        db.scalars(
            select(Message.id).where(
                Message.tenant_id == context.tenant_id,
                Message.expires_at <= utcnow(),
            )
        )
    )
    affected_conversation_ids = (
        list(
            db.scalars(
                select(Message.conversation_id).where(Message.id.in_(expired_ids)).distinct()
            )
        )
        if expired_ids
        else []
    )
    if expired_ids:
        db.execute(
            delete(MessageReceipt).where(
                MessageReceipt.tenant_id == context.tenant_id,
                MessageReceipt.message_id.in_(expired_ids),
            )
        )
        db.execute(
            delete(Message).where(
                Message.tenant_id == context.tenant_id,
                Message.id.in_(expired_ids),
            )
        )
        now = utcnow()
        for conversation_id in affected_conversation_ids:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.tenant_id == context.tenant_id,
                )
            )
            if conversation is not None:
                conversation.last_message_at = db.scalar(
                    select(func.max(Message.created_at)).where(
                        Message.tenant_id == context.tenant_id,
                        Message.conversation_id == conversation_id,
                        Message.expires_at > now,
                    )
                )
    record_audit(
        db,
        context,
        "message.retention.purge",
        "tenant",
        context.tenant_id,
        {"purged_messages": len(expired_ids)},
    )
    db.commit()
    return RetentionPurgeOut(purged_messages=len(expired_ids))
