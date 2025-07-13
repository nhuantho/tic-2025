from pydantic_settings import BaseSettings
from fastapi.security import OAuth2PasswordBearer
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./user_api.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 