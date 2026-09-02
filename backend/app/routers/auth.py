from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import Context, current_user
from app.models import User
from app.schemas import CurrentUser, LoginRequest, RefreshRequest, TokenPair
from app.security import (
    create_access_token,
    create_refresh_session,
    revoke_refresh_session,
    rotate_refresh_session,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenPair:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
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
