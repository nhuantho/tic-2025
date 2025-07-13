from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import BaseModel

class APISpec(BaseModel):
    __tablename__ = "api_specs"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50))
    file_path = Column(String(500))
    file_type = Column(String(50))  # 'openapi', 'postman'
    status = Column(String(50), default='active')  # 'active', 'inactive', 'error'
    
    # Service configuration for microservices
    service_config = Column(JSON, default={})  # { "base_url": "...", "dependencies": ["service1", "service2"] }
    
    # Relationships - using string references to avoid circular imports
    endpoints = relationship("Endpoint", back_populates="api_spec", cascade="all, delete-orphan")
    test_cases = relationship("TestCase", back_populates="api_spec", cascade="all, delete-orphan")

class Endpoint(BaseModel):
    __tablename__ = "endpoints"
    
    api_spec_id = Column(Integer, ForeignKey("api_specs.id"))
    path = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    summary = Column(String(255))
    description = Column(Text)
    parameters = Column(JSON)
    request_body = Column(JSON)
    responses = Column(JSON)
    tags = Column(JSON)
    
    # Inter-service communication info
    service_dependencies = Column(JSON, default=[])  # List of services this endpoint depends on
    external_calls = Column(JSON, default=[])  # List of external API calls made by this endpoint
    
    # Relationships - using string references to avoid circular imports
    api_spec = relationship("APISpec", back_populates="endpoints")
    test_cases = relationship("TestCase", back_populates="endpoint", cascade="all, delete-orphan") 