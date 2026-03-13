from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "nl2sql-poc"
    LLM_MODEL: str = "gpt-4o-mini"
    DATABASE_URL: str = "sqlite:///./data.db"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "nl2sql_docs"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    MAX_RETRIES: int = 3
    SQL_RESULT_LIMIT: int = 100

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

if settings.OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY