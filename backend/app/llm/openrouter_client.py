import httpx
from app.core.config import settings


class LLMUpstreamError(Exception):
    """Raised when the configured LLM provider cannot produce a response."""

async def get_llm_test_response(prompt: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise LLMUpstreamError("The language service is unavailable. Please try again.") from exc

    if not isinstance(content, str) or not content.strip():
        raise LLMUpstreamError("The language service returned an empty response.")
    return content