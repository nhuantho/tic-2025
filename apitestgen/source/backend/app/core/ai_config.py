from typing import Optional
from pydantic_settings import BaseSettings
import os

class AIConfig(BaseSettings):
    """Configuration for AI features"""
    # AI Provider Settings
    AI_PROVIDER: str = os.environ.get("AI_PROVIDER", "gemini")

    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.environ.get("OPENAI_MAX_TOKENS", 1000))
    OPENAI_TEMPERATURE: float = float(os.environ.get("OPENAI_TEMPERATURE", 0.7))
    OPENAI_TIMEOUT: int = int(os.environ.get("OPENAI_TIMEOUT", 30))

    # DeepSeek Settings
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: str = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_MAX_TOKENS: int = int(os.environ.get("DEEPSEEK_MAX_TOKENS", 1000))
    DEEPSEEK_TEMPERATURE: float = float(os.environ.get("DEEPSEEK_TEMPERATURE", 0.7))
    DEEPSEEK_TIMEOUT: int = int(os.environ.get("DEEPSEEK_TIMEOUT", 30))
    DEEPSEEK_BASE_URL: str = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # AIMLAPI.com Settings
    AIMLAPI_API_KEY: Optional[str] = None
    AIMLAPI_MODEL: str = os.environ.get("AIMLAPI_MODEL", "gpt-3.5-turbo")
    AIMLAPI_MAX_TOKENS: int = int(os.environ.get("AIMLAPI_MAX_TOKENS", 1000))
    AIMLAPI_TEMPERATURE: float = float(os.environ.get("AIMLAPI_TEMPERATURE", 0.7))
    AIMLAPI_TIMEOUT: int = int(os.environ.get("AIMLAPI_TIMEOUT", 30))
    AIMLAPI_BASE_URL: str = os.environ.get("AIMLAPI_BASE_URL", "https://api.aimlapi.com")

    # Gemini 2.0 Flash Settings
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_MAX_TOKENS: int = int(os.environ.get("GEMINI_MAX_TOKENS", 1000))
    GEMINI_TEMPERATURE: float = float(os.environ.get("GEMINI_TEMPERATURE", 1.0))
    GEMINI_TIMEOUT: int = int(os.environ.get("GEMINI_TIMEOUT", 30))
    GEMINI_BASE_URL: str = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

    # RAG Settings - Mock RAG DISABLED
    USE_MOCK_RAG: bool = bool(int(os.environ.get("USE_MOCK_RAG", "0")))
    RAG_FALLBACK_TO_MOCK: bool = bool(int(os.environ.get("RAG_FALLBACK_TO_MOCK", "0")))
    RAG_FALLBACK_TO_RULE_BASED: bool = bool(int(os.environ.get("RAG_FALLBACK_TO_RULE_BASED", "1")))

    # Test Generation Settings
    MAX_TEST_CASES_PER_ENDPOINT: int = int(os.environ.get("MAX_TEST_CASES_PER_ENDPOINT", 4))
    ENABLE_SECURITY_TESTS: bool = bool(int(os.environ.get("ENABLE_SECURITY_TESTS", "1")))
    ENABLE_BUSINESS_LOGIC_TESTS: bool = bool(int(os.environ.get("ENABLE_BUSINESS_LOGIC_TESTS", "1")))

    class Config:
        env_file = ".env"

# Global AI config instance
ai_config = AIConfig()

def get_rag_generator():
    """Get the appropriate RAG generator based on configuration - Mock RAG disabled"""
    # Mock RAG is completely disabled
    if ai_config.USE_MOCK_RAG:
        print("Mock RAG is disabled in production")
        return None
    
    # Try the configured AI provider first
    if ai_config.AI_PROVIDER == "deepseek":
        try:
            from app.services.deepseek_rag_generator import DeepSeekRAGTestGenerator
            deepseek_generator = DeepSeekRAGTestGenerator()
            
            if deepseek_generator.is_available:
                return deepseek_generator
        except Exception as e:
            print(f"DeepSeek RAG not available: {str(e)}")
    
    elif ai_config.AI_PROVIDER == "openai":
        try:
            from app.services.rag_test_generator import RAGTestGenerator
            openai_generator = RAGTestGenerator()
            
            if openai_generator.is_available:
                return openai_generator
        except Exception as e:
            print(f"OpenAI RAG not available: {str(e)}")
    
    elif ai_config.AI_PROVIDER == "aimlapi":
        try:
            from app.services.aimlapi_rag_generator import AIMLAPIRAGTestGenerator
            aimlapi_generator = AIMLAPIRAGTestGenerator()
            
            if aimlapi_generator.is_available:
                return aimlapi_generator
        except Exception as e:
            print(f"AIMLAPI.com RAG not available: {str(e)}")
    
    elif ai_config.AI_PROVIDER == "gemini":
        try:
            from app.services.gemini_rag_generator import GeminiRAGTestGenerator
            gemini_generator = GeminiRAGTestGenerator()
            
            if gemini_generator.is_available:
                return gemini_generator
        except Exception as e:
            print(f"Gemini RAG not available: {str(e)}")
    
    # No AI generator available - will use automated test cases only
    print("No real AI generator available, will use automated test cases only")
    return None

def is_ai_available() -> bool:
    """Check if any real AI generation is available - Mock RAG not considered"""
    # Mock RAG is not considered as real AI
    if ai_config.USE_MOCK_RAG:
        return False
    
    # Check if any real AI provider is available
    try:
        if ai_config.AI_PROVIDER == "gemini":
            from app.services.gemini_rag_generator import GeminiRAGTestGenerator
            gemini_generator = GeminiRAGTestGenerator()
            return gemini_generator.is_available
        elif ai_config.AI_PROVIDER == "openai":
            from app.services.rag_test_generator import RAGTestGenerator
            openai_generator = RAGTestGenerator()
            return openai_generator.is_available
        elif ai_config.AI_PROVIDER == "deepseek":
            from app.services.deepseek_rag_generator import DeepSeekRAGTestGenerator
            deepseek_generator = DeepSeekRAGTestGenerator()
            return deepseek_generator.is_available
        elif ai_config.AI_PROVIDER == "aimlapi":
            from app.services.aimlapi_rag_generator import AIMLAPIRAGTestGenerator
            aimlapi_generator = AIMLAPIRAGTestGenerator()
            return aimlapi_generator.is_available
    except Exception:
        pass
    
    return False 