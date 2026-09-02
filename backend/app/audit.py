from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.dependencies import RequestContext
from app.models import AuditEvent


def record_audit(
    db: Session,
    context: RequestContext,
    action: str,
    resource_type: str,
    resource_id: str,
    details: Optional[dict[str, object]] = None,
) -> None:
    db.add(
        AuditEvent(
            tenant_id=context.tenant_id,
            actor_user_id=context.user.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )
    )
