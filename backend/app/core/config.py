from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    LLM_MODEL: str = "deepseek/deepseek-v4-flash-0731"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = Path(__file__).resolve().parents[3] / ".env"
        extra = "ignore"

settings = Settings()