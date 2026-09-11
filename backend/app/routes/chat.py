from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_active_user
from app.schemas.chat import ChatTestRequest, ChatTestResponse
from app.services.chat_service import LLMUpstreamError, get_llm_test_response

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

@router.post("/test", response_model=ChatTestResponse)
async def test_chat(
    body: ChatTestRequest,
    _: Annotated[object, Depends(get_current_active_user)],
) -> ChatTestResponse:
    try:
        result = await get_llm_test_response(body.prompt)
    except LLMUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to get a response from the language service.",
        ) from exc
    return ChatTestResponse(response=result)
