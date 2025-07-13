from sqlalchemy import Column, String, Text, JSON, Boolean, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel

class TestCaseType(enum.Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    AI_GENERATED = "ai_generated"

class TestCasePriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TestCase(BaseModel):
    __tablename__ = "test_cases"
    
    api_spec_id = Column(Integer, ForeignKey("api_specs.id"))
    endpoint_id = Column(Integer, ForeignKey("endpoints.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    test_type = Column(Enum(TestCaseType), nullable=False)
    priority = Column(Enum(TestCasePriority), default=TestCasePriority.MEDIUM)
    
    # Test data
    input_data = Column(JSON)
    expected_output = Column(JSON)
    expected_status_code = Column(Integer)
    
    # Test execution
    curl_command = Column(Text)
    test_script = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    api_spec = relationship("APISpec", back_populates="test_cases")
    endpoint = relationship("Endpoint", back_populates="test_cases")
    test_results = relationship("TestResult", back_populates="test_case")

class TestResult(BaseModel):
    __tablename__ = "test_results"
    
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    status = Column(String(50), nullable=False)  # passed, failed, error
    response_status_code = Column(Integer)
    response_body = Column(Text)
    response_time = Column(Integer)  # milliseconds
    error_message = Column(Text)
    execution_log = Column(Text)
    
    # Relationships
    test_case = relationship("TestCase", back_populates="test_results") 