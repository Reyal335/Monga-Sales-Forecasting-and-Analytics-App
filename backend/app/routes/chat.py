from fastapi import APIRouter
from app.schemas.chat import ChatTestRequest, ChatTestResponse
from app.services.chat_service import get_llm_test_response

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/test", response_model=ChatTestResponse)
async def test_chat(body: ChatTestRequest):
    result = await get_llm_test_response(body.prompt)
    return ChatTestResponse(response=result)