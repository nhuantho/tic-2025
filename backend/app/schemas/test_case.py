from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.test_case import TestCaseType, TestCasePriority

class TestCaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    test_type: TestCaseType
    priority: TestCasePriority = TestCasePriority.MEDIUM
    input_data: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None
    expected_status_code: Optional[int] = None

class TestCaseCreate(TestCaseBase):
    api_spec_id: int
    endpoint_id: int
    curl_command: Optional[str] = None
    test_script: Optional[str] = None

class TestCaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TestCasePriority] = None
    input_data: Optional[Dict[str, Any]] = None
    expected_output: Optional[Dict[str, Any]] = None
    expected_status_code: Optional[int] = None
    curl_command: Optional[str] = None
    test_script: Optional[str] = None
    is_active: Optional[bool] = None

class TestCase(TestCaseBase):
    id: int
    api_spec_id: int
    endpoint_id: int
    curl_command: Optional[str] = None
    test_script: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TestResultBase(BaseModel):
    status: str
    response_status_code: Optional[int] = None
    response_body: Optional[str] = None
    response_time: Optional[int] = None
    error_message: Optional[str] = None
    execution_log: Optional[str] = None

class TestResultCreate(TestResultBase):
    test_case_id: int

class TestResult(TestResultBase):
    id: int
    test_case_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 