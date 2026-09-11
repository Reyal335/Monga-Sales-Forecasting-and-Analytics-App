from ..llm.openrouter_client import get_llm_test_response
from ..llm.prompt_builder import build_sql_generation_prompt

async def generate_sql_query(user_prompt: str):
    sql_prompt = build_sql_generation_prompt(user_prompt)
    response = await get_llm_test_response(sql_prompt)
