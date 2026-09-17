from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_active_user
from app.schemas.chat import ChatTestRequest, ChatTestResponse
from ..llm.openrouter_client import LLMUpstreamError, get_llm_test_response

from ..services.chat_service import ChatService

from ..database.database import get_db

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

db_session = Annotated[Session, Depends(get_db)]

@router.post("/test", response_model=ChatTestResponse)
async def test_chat(
    body: ChatTestRequest,
    _: Annotated[object, Depends(get_current_active_user)],
    db: db_session
) -> ChatTestResponse:
    try:
        service = ChatService(db)
        return await service.process_chat_message(body.prompt, body.document_id)
    except LLMUpstreamError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to get a response from the language service.",
        ) from exc

