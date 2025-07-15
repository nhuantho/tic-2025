import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    
    # Redis
    REDIS_URL: str = os.environ.get("REDIS_URL", "")
    
    # Security
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # Default can remain
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY", "")
    
    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = os.environ.get("DEEPSEEK_API_KEY", "")
    
    # File paths (non-sensitive, can have defaults)
    API_DOCS_DIR: str = os.environ.get("API_DOCS_DIR", "api-docs")
    LOGS_DIR: str = os.environ.get("LOGS_DIR", "logs")
    
    # Test settings (non-sensitive, can have defaults)
    MAX_CONCURRENT_TESTS: int = 10
    TEST_TIMEOUT: int = 30  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 