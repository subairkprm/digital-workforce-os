from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import RefreshSession, User

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    return password_hash.verify(password, encoded)


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": user_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_minutes),
        },
        settings.jwt_secret,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=[ALGORITHM])
    if payload.get("type") != "access" or not payload.get("sub"):
        raise jwt.InvalidTokenError("invalid access token")
    return str(payload["sub"])


def digest_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_session(
    db: Session, user: User, family_id: Optional[str] = None
) -> tuple[str, RefreshSession]:
    raw = secrets.token_urlsafe(48)
    session = RefreshSession(
        user_id=user.id,
        family_id=family_id or str(uuid.uuid4()),
        token_digest=digest_token(raw),
        expires_at=datetime.now(timezone.utc) + timedelta(days=get_settings().refresh_token_days),
    )
    db.add(session)
    db.flush()
    return raw, session


def rotate_refresh_session(db: Session, raw: str) -> tuple[User, str]:
    current = db.scalar(
        select(RefreshSession).where(RefreshSession.token_digest == digest_token(raw))
    )
    now = datetime.now(timezone.utc)
    if current is None:
        raise ValueError("invalid refresh token")
    if current.revoked_at is not None:
        db.execute(
            update(RefreshSession)
            .where(
                RefreshSession.family_id == current.family_id, RefreshSession.revoked_at.is_(None)
            )
            .values(revoked_at=now)
        )
        raise ValueError("refresh token reuse detected")
    expires_at = current.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise ValueError("refresh token expired")
    user = db.get(User, current.user_id)
    if user is None or not user.is_active:
        raise ValueError("inactive user")
    current.revoked_at = now
    new_raw, replacement = create_refresh_session(db, user, current.family_id)
    current.replaced_by_id = replacement.id
    return user, new_raw


def revoke_refresh_session(db: Session, raw: str) -> None:
    session = db.scalar(
        select(RefreshSession).where(RefreshSession.token_digest == digest_token(raw))
    )
    if session is not None and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
