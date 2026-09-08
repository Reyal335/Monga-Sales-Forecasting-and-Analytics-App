from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ..schemas.users import UserInDB
from ..dependencies.auth import get_current_active_user, fake_users_db, hash_password
from typing import Annotated

router = APIRouter(prefix="api/v1/auth", tags=["auth"])

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username"
        )
    user = UserInDB(**user_dict)
    hashed_password = hash_password(user.hashed_password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}
    