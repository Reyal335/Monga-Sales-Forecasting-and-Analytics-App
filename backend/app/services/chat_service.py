import httpx
from app.core.config import settings
from sql_pipeline import generate_sql_query

async def process_sql_response(user_prompt: str):
    await generate_sql_query(user_prompt)

async def process_doc_response(document_id: int):
    pass

async def process_chat_message(user_chat: str, document_id: int | None = None) -> dict:
    if not document_id:
        return await process_sql_response()
    return await process_doc_response(document_id)

