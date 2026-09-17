import json
from sqlalchemy import text

from ..llm.openrouter_client import get_llm_test_response
from ..llm.prompt_builder import build_sql_generation_prompt

async def generate_sql_query(user_prompt: str):
    sql_prompt = build_sql_generation_prompt(user_prompt)
    response = await get_llm_test_response(sql_prompt)

    return {
        "llm_query": response,
        "user_prompt": user_prompt
    }

async def analyze_results(db, sql_query: str):
    result = db.execute(text(sql_query))
    return [dict(row) for row in result.mappings().all()]