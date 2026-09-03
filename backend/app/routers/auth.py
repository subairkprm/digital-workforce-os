from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import Context, current_user
from app.models import RefreshSession, User
from app.rate_limit import enforce_rate_limit
from app.schemas import CurrentUser, LoginRequest, RefreshRequest, SessionOut, TokenPair
from app.security import (
    create_access_token,
    create_refresh_session,
    revoke_refresh_session,
    rotate_refresh_session,
    verify_password,
)
from app.security_events import record_security_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
def login(
    payload: LoginRequest, request: Request, db: Annotated[Session, Depends(get_db)]
) -> TokenPair:
    try:
        enforce_rate_limit(
            "auth-login",
            f"{request.client.host if request.client else 'unknown'}:{payload.email.lower()}",
            get_settings().auth_rate_limit,
        )
    except HTTPException:
        record_security_event(
            db,
            "rate.limit",
            "denied",
            metadata={"scope": "auth-login"},
        )
        db.commit()
        raise
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        record_security_event(
            db,
            "authentication.failed",
            "denied",
            actor_user_id=user.id if user else None,
            metadata={"method": "password"},
        )
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    refresh, _ = create_refresh_session(db, user)
    db.commit()
    return TokenPair(access_token=create_access_token(user.id), refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> TokenPair:
    try:
        user, new_refresh = rotate_refresh_session(db, payload.refresh_token)
        db.commit()
    except ValueError as exc:
        if str(exc) == "refresh token reuse detected":
            record_security_event(db, "refresh.reuse", "denied", metadata={"family_revoked": True})
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return TokenPair(access_token=create_access_token(user.id), refresh_token=new_refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: RefreshRequest,
    db: Annotated[Session, Depends(get_db)],
    _user: Annotated[User, Depends(current_user)],
) -> None:
    revoke_refresh_session(db, payload.refresh_token)
    db.commit()


@router.get("/me", response_model=CurrentUser)
def me(context: Context) -> CurrentUser:
    return CurrentUser(
        id=context.user.id,
        email=context.user.email,
        tenant_id=context.tenant_id,
        permissions=sorted(context.permissions),
    )


@router.get("/sessions", response_model=list[SessionOut])
def sessions(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(current_user)],
) -> list[RefreshSession]:
    return list(
        db.scalars(
            select(RefreshSession)
            .where(RefreshSession.user_id == user.id)
            .order_by(RefreshSession.created_at.desc())
            .limit(100)
        )
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(
    session_id: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(current_user)],
) -> None:
    session = db.scalar(
        select(RefreshSession).where(
            RefreshSession.id == session_id, RefreshSession.user_id == user.id
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    if session.revoked_at is None:
        from datetime import datetime, timezone

        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
