import os
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from .schemas import LoginCommand
from .service import profile, open_session
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from .access import COOKIE_NAME, ROLE_ACCESS, current_user, token_hash, verify_password
from .models import AccessSession, User
from app.core.commands import utcnow
from app.core.config import COOKIE_SECURE

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(command: LoginCommand, response: Response, db: Session = Depends(get_db)):
    user, session, token = open_session(db, command)
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="strict",
        secure=COOKIE_SECURE,
        max_age=28800,
        path="/api",
    )
    return profile(user, session)


@router.get("/me")
def me(request: Request, user: User = Depends(current_user)):
    return profile(user, request.state.access_session)


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    response: Response,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    db.delete(request.state.access_session)
    db.commit()
    response.delete_cookie(COOKIE_NAME, path="/api")
