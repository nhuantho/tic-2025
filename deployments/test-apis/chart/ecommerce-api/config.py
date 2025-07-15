from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./ecommerce_api.db"
    # Sử dụng Docker service name khi chạy trong container, localhost khi chạy local
    USER_API_URL: str = os.getenv("USER_API_URL", "http://localhost:8001")
    
    class Config:
        env_file = ".env"

settings = Settings() 