from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import RequestContext, require_permission
from app.models import AuditEvent
from app.schemas import AuditOut

router = APIRouter(prefix="/audit-events", tags=["audit"])


@router.get("", response_model=list[AuditOut])
def list_audit_events(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("audit.read"))],
) -> list[AuditEvent]:
    query = (
        select(AuditEvent)
        .where(AuditEvent.tenant_id == context.tenant_id)
        .order_by(AuditEvent.created_at.desc())
        .limit(200)
    )
    return list(db.scalars(query))
