from fastapi import HTTPException, status
from .sql_pipeline import generate_sql_query, analyze_results

from typing import Annotated

from ..schemas.chat import ChatTestRequest, ChatTestResponse
from ..llm.openrouter_client import LLMUpstreamError, get_llm_test_response
from ..llm.sql_guard import postgres_query

from sqlalchemy.orm import Session

class ChatService:
    def __init__ (self, db):
        self.db = db

    async def process_sql_response(self, user_prompt: str):
        try:
            prompt = await generate_sql_query(user_prompt)
            print(f"prompt {prompt}")
            print('before postgres quey')
            
            pg_query = postgres_query(prompt["llm_query"])
            result = await analyze_results(self.db, pg_query)
            return ChatTestResponse(response=str(result))
        except LLMUpstreamError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unable to get a response from the language service.",
            ) from exc


    async def process_doc_response(self, document_id: int):
        pass

    async def process_chat_message(self, user_chat: str, document_id: str | None = None) -> dict:
        if not document_id:
            return await self.process_sql_response(user_chat)
        return await self.process_doc_response(document_id)

