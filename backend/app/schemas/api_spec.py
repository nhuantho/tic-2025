from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class APISpecBase(BaseModel):
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    file_type: str

class APISpecCreate(APISpecBase):
    file_path: str

class APISpecUpdate(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class APISpec(APISpecBase):
    id: int
    file_path: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EndpointBase(BaseModel):
    path: str
    method: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    request_body: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class EndpointCreate(EndpointBase):
    api_spec_id: int

class Endpoint(EndpointBase):
    id: int
    api_spec_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 