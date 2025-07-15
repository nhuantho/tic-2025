from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime
import logging

from app.core.database import get_db
from app.schemas.api_spec import APISpec, APISpecCreate, APISpecUpdate, Endpoint
from app.services.api_parser import APIParser
from app.services.test_generator import TestGenerator
from app.models.api_spec import APISpec as APISpecModel, Endpoint as EndpointModel
from app.core.config import settings
from app.models.test_case import TestCase as TestCaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/import", response_model=APISpec)
async def import_api_spec(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import API specification file"""
    
    # Validate file type
    allowed_extensions = ['.yaml', '.yml', '.json']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Save uploaded file
        api_docs_dir = settings.API_DOCS_DIR
        os.makedirs(api_docs_dir, exist_ok=True)
        
        file_path = os.path.join(api_docs_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse and validate the file
        spec_info = APIParser.validate_spec_file(file_path)
        
        # Create API spec record
        api_spec_data = APISpecCreate(
            name=os.path.splitext(file.filename)[0],
            version=spec_info.get('version', '1.0.0'),
            description=f"Imported from {file.filename}",
            file_type=spec_info['type'],
            file_path=file_path
        )
        
        db_api_spec = APISpecModel(**api_spec_data.dict())
        db.add(db_api_spec)
        db.commit()
        db.refresh(db_api_spec)
        
        # Extract and save endpoints
        if spec_info['type'] == 'openapi':
            endpoints = APIParser.extract_endpoints_from_openapi(spec_info['content'])
        else:  # postman
            endpoints = APIParser.extract_endpoints_from_postman(spec_info['content'])
        
        # Valid fields for EndpointModel
        valid_endpoint_fields = {
            'path', 'method', 'summary', 'description', 
            'parameters', 'request_body', 'responses', 'tags'
        }
        
        endpoint_count = 0
        endpoint_ids = []
        for endpoint_data in endpoints:
            # Filter out any invalid fields
            filtered_data = {k: v for k, v in endpoint_data.items() if k in valid_endpoint_fields}
            endpoint = EndpointModel(
                api_spec_id=db_api_spec.id,
                **filtered_data
            )
            db.add(endpoint)
            db.flush()  # get endpoint.id
            endpoint_count += 1
            endpoint_ids.append(endpoint.id)
        db.commit()
        db.refresh(db_api_spec)

        # Auto-generate test cases for each endpoint if not already present
        for endpoint_id in endpoint_ids:
            endpoint = db.query(EndpointModel).filter(EndpointModel.id == endpoint_id).first()
            # Check if test cases already exist
            existing = db.query(TestCaseModel).filter(TestCaseModel.endpoint_id == endpoint_id).first()
            if not existing:
                endpoint_dict = {
                    'method': endpoint.method,
                    'path': endpoint.path,
                    'summary': endpoint.summary,
                    'description': endpoint.description,
                    'parameters': endpoint.parameters,
                    'request_body': endpoint.request_body,
                    'responses': endpoint.responses,
                    'tags': endpoint.tags
                }
                # Pass API spec content for RAG generation
                api_spec_content = spec_info.get('content', {})
                test_cases = TestGenerator.generate_test_cases(endpoint_dict, "", api_spec_content)
                for test_case_data in test_cases:
                    test_case = TestCaseModel(
                        api_spec_id=db_api_spec.id,
                        endpoint_id=endpoint.id,
                        name=test_case_data['name'],
                        description=test_case_data['description'],
                        test_type=test_case_data['test_type'],
                        priority=test_case_data['priority'],
                        input_data=test_case_data['input_data'],
                        expected_output=test_case_data.get('expected_output'),
                        expected_status_code=test_case_data['expected_status_code'],
                        curl_command=test_case_data['curl_command'],
                        test_script=test_case_data.get('test_script')
                    )
                    db.add(test_case)
        db.commit()
        
        # Update status based on endpoint creation
        if endpoint_count > 0:
            db_api_spec.status = 'success'
        else:
            db_api_spec.status = 'failed'
        
        db.commit()
        db.refresh(db_api_spec)
        
        return db_api_spec
        
    except Exception as e:
        # Clean up file if error occurs
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        # If we have a created API spec, update its status to failed
        if 'db_api_spec' in locals():
            db_api_spec.status = 'failed'
            db.commit()
        
        logger.error(f"Error during import: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[APISpec])
async def list_api_specs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all API specifications"""
    api_specs = db.query(APISpecModel).offset(skip).limit(limit).all()
    return api_specs

@router.get("/{api_spec_id}", response_model=APISpec)
async def get_api_spec(
    api_spec_id: int,
    db: Session = Depends(get_db)
):
    """Get API specification by ID"""
    api_spec = db.query(APISpecModel).filter(APISpecModel.id == api_spec_id).first()
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    return api_spec

@router.get("/{api_spec_id}/endpoints", response_model=List[Endpoint])
async def get_api_spec_endpoints(
    api_spec_id: int,
    db: Session = Depends(get_db)
):
    """Get all endpoints for an API specification"""
    endpoints = db.query(EndpointModel).filter(EndpointModel.api_spec_id == api_spec_id).all()
    return endpoints

@router.put("/{api_spec_id}", response_model=APISpec)
async def update_api_spec(
    api_spec_id: int,
    api_spec_update: APISpecUpdate,
    db: Session = Depends(get_db)
):
    """Update API specification"""
    api_spec = db.query(APISpecModel).filter(APISpecModel.id == api_spec_id).first()
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    
    update_data = api_spec_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(api_spec, field, value)
    
    db.commit()
    db.refresh(api_spec)
    return api_spec

@router.delete("/{api_spec_id}")
async def delete_api_spec(
    api_spec_id: int,
    db: Session = Depends(get_db)
):
    """Delete API specification"""
    api_spec = db.query(APISpecModel).filter(APISpecModel.id == api_spec_id).first()
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    
    # Delete associated file
    if os.path.exists(api_spec.file_path):
        os.remove(api_spec.file_path)
    
    db.delete(api_spec)
    db.commit()
    
    return {"message": "API specification deleted successfully"} 