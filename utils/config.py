"""Settings loaded from .env"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"

    NCBI_EMAIL: str = "deepresearch@example.com"
    NCBI_API_KEY: str = ""
    SEMANTIC_SCHOLAR_API_KEY: str = ""

    MAX_PAPERS: int = 20          # reduced from 40
    MAX_TOKENS: int = 2048        # reduced from 4096
    TEMPERATURE: float = 0.2
    EFFICIENT_MODE: bool = True   # token-saving mode on by default
    VECTOR_STORE_PATH: str = "./data/vector_store"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
