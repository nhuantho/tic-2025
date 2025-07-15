from fastapi import APIRouter
from app.api.api_v1.endpoints import api_specs, test_cases, test_execution

api_router = APIRouter()

api_router.include_router(api_specs.router, prefix="/api-specs", tags=["API Specifications"])
api_router.include_router(test_cases.router, prefix="/test-cases", tags=["Test Cases"])
api_router.include_router(test_execution.router, prefix="/test-execution", tags=["Test Execution"]) 