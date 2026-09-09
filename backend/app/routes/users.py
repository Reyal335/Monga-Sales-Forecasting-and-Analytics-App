from fastapi import APIRouter, Depends

from ..dependencies.auth import get_current_active_user
from ..schemas.users import User, CreateUser

from typing import Annotated

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/", tags=["users"])
async def read_users():
    return [{"message": "Hi"}]

@router.get("/me", tags=["users"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@router.post("/create", tags=["users"])
async def create_users(
    user: CreateUser
):
    pass
