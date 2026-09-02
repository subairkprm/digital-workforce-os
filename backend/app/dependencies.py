from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Optional

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Membership, User
from app.security import decode_access_token

bearer = HTTPBearer(auto_error=False)
Db = Annotated[Session, Depends(get_db)]


@dataclass(frozen=True)
class RequestContext:
    user: User
    membership: Membership
    tenant_id: str
    permissions: frozenset[str]


def current_user(
    db: Db, credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer)]
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication required"
        )
    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        ) from exc
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="inactive user")
    return user


def request_context(
    db: Db,
    user: Annotated[User, Depends(current_user)],
    tenant_id: Annotated[Optional[str], Header(alias="X-Tenant-ID")] = None,
) -> RequestContext:
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Tenant-ID required")
    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.tenant_id == tenant_id,
            Membership.is_active.is_(True),
        )
    )
    if membership is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="tenant access denied")
    permissions = frozenset(
        permission.code for role in membership.roles for permission in role.permissions
    )
    return RequestContext(
        user=user, membership=membership, tenant_id=tenant_id, permissions=permissions
    )


Context = Annotated[RequestContext, Depends(request_context)]


def require_permission(code: str) -> Callable[[RequestContext], RequestContext]:
    def dependency(context: Context) -> RequestContext:
        if code not in context.permissions and "tenant.owner" not in context.permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
        return context

    return dependency
