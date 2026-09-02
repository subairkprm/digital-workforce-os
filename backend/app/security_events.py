from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import SecurityEvent


def record_security_event(
    db: Session,
    category: str,
    outcome: str,
    *,
    tenant_id: Optional[str] = None,
    actor_user_id: Optional[str] = None,
    metadata: Optional[dict[str, object]] = None,
) -> None:
    db.add(
        SecurityEvent(
            tenant_id=tenant_id,
            actor_user_id=actor_user_id,
            category=category,
            outcome=outcome,
            metadata_=metadata or {},
        )
    )
