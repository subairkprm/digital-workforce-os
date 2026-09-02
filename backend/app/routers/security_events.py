from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import RequestContext, require_permission
from app.models import SecurityEvent
from app.schemas import SecurityEventOut

router = APIRouter(prefix="/security-events", tags=["security"])


@router.get("", response_model=list[SecurityEventOut])
def list_security_events(
    db: Annotated[Session, Depends(get_db)],
    context: Annotated[RequestContext, Depends(require_permission("security.read"))],
) -> list[SecurityEventOut]:
    events = db.scalars(
        select(SecurityEvent)
        .where(SecurityEvent.tenant_id == context.tenant_id)
        .order_by(SecurityEvent.created_at.desc())
    )
    return [
        SecurityEventOut(
            id=e.id,
            category=e.category,
            outcome=e.outcome,
            metadata=e.metadata_,
            created_at=e.created_at,
        )
        for e in events
    ]
