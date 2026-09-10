from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.users import UserInDB
from ..dependencies.auth import (
    create_access_token, 
    create_refresh_token,
    authenticate_user, 
    Token,
    DbSession,
)
from typing import Annotated

from datetime import timedelta

import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    db: DbSession,
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expire = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(
        data={"sub": str(user.user_id)}, expires_delta=access_token_expire
    )

    refresh_token_expire = timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS))
    refresh_token = create_refresh_token(
        data={"sub": str(user.user_id)}, expires_delta=refresh_token_expire
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=int(refresh_token_expire.total_seconds()),
        httponly=True,
        secure = os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite="lax"
    )

    return Token(access_token=access_token, token_type="bearer")
    