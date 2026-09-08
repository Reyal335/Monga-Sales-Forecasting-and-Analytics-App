from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/", tags=["users"])
async def read_users():
    return [{"message": "Hi"}]