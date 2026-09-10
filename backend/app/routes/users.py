from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pydantic import ValidationError 

from ..dependencies.auth import get_current_active_user
from ..schemas.users import UserResponse, UserCreate

from ..services.users_service import UserService
from ..database.database import get_db

from typing import Annotated

router = APIRouter(prefix="/api/v1/users", tags=["users"])

db_session = Annotated[Session, Depends(get_db)]

@router.get("/", tags=["users"])
async def read_users():
    return [{"message": "Hi"}]

@router.get("/me", tags=["users"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_users(
    db: db_session,
    user: UserCreate,
):
    try:
        
        service = UserService(db)
        results = service.create_user(user)
        
        return results
    except IntegrityError as e:
        db.rollback()  # Always rollback the session after an error
        
        # Check if it's a unique constraint violation (PostgreSQL code 23505)
        if "23505" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already exists."
            )
            
        # Handle other integrity constraints (e.g., foreign keys 23503)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Database integrity error."
        )
    except ValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_list": err.errors()
            }
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Value Error"
            }
        )
    except Exception as err: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "An error occurred"
            }
        )
