from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from sqlalchemy import case
import json
import os

from app.core.database import get_db
from app.schemas.test_case import TestCase, TestCaseCreate, TestCaseUpdate, TestResult
from app.services.test_generator import TestGenerator
from app.services.api_parser import APIParser
from app.models.test_case import TestCase as TestCaseModel, TestResult as TestResultModel
from app.models.api_spec import APISpec as APISpecModel, Endpoint as EndpointModel
from app.models.test_case import TestCaseType

router = APIRouter()

class GenerateTestCasesRequest(BaseModel):
    api_spec_id: int
    endpoint_path: str = None
    method: str = None
    base_url: str = ""

@router.post("/generate", response_model=List[TestCase])
async def generate_test_cases(
    request: GenerateTestCasesRequest,
    db: Session = Depends(get_db)
):
    """Generate test cases for an API specification"""
    
    # Get API spec and endpoints
    api_spec = db.query(APISpecModel).filter(APISpecModel.id == request.api_spec_id).first()
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    
    endpoints = db.query(EndpointModel).filter(EndpointModel.api_spec_id == request.api_spec_id).all()
    if not endpoints:
        raise HTTPException(status_code=404, detail="No endpoints found for this API specification")
    
    generated_test_cases = []
    
    for endpoint in endpoints:
        # Convert endpoint model to dict
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
        
        # Load API spec content for RAG generation
        api_spec_content = {}
        if api_spec.file_path and os.path.exists(api_spec.file_path):
            try:
                spec_info = APIParser.validate_spec_file(api_spec.file_path)
                api_spec_content = spec_info.get('content', {})
            except Exception as e:
                print(f"Failed to load API spec content: {str(e)}")
        
        # Generate test cases for this endpoint with RAG support
        test_cases = TestGenerator.generate_test_cases(endpoint_dict, request.base_url, api_spec_content)
        
        for test_case_data in test_cases:
            # Create test case record
            test_case = TestCaseModel(
                api_spec_id=request.api_spec_id,
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
            generated_test_cases.append(test_case)
    
    db.commit()
    
    # Refresh all test cases to get IDs
    for test_case in generated_test_cases:
        db.refresh(test_case)
    
    return generated_test_cases

@router.post("/generate-rag", response_model=List[TestCase])
async def generate_rag_test_cases(
    request: GenerateTestCasesRequest,
    db: Session = Depends(get_db)
):
    """Generate automated test cases first, then optionally add AI-powered ones if available"""
    
    # Get API spec
    api_spec = db.query(APISpecModel).filter(APISpecModel.id == request.api_spec_id).first()
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    
    # Load API spec content for RAG generation
    api_spec_content = {}
    if api_spec.file_path and os.path.exists(api_spec.file_path):
        try:
            spec_info = APIParser.validate_spec_file(api_spec.file_path)
            api_spec_content = spec_info.get('content', {})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load API spec content: {str(e)}")
    
    # Get endpoints - either specific endpoint or all endpoints
    if request.endpoint_path and request.method:
        # Generate for specific endpoint only
        endpoints = db.query(EndpointModel).filter(
            EndpointModel.api_spec_id == request.api_spec_id,
            EndpointModel.path == request.endpoint_path,
            EndpointModel.method == request.method.upper()
        ).all()
        
        if not endpoints:
            raise HTTPException(status_code=404, detail=f"Endpoint {request.method} {request.endpoint_path} not found")
    else:
        # Generate for all endpoints in the API spec
        endpoints = db.query(EndpointModel).filter(EndpointModel.api_spec_id == request.api_spec_id).all()
        
        if not endpoints:
            raise HTTPException(status_code=404, detail="No endpoints found for this API specification")
    
    generated_test_cases = []
    
    # ALWAYS generate automated test cases first (guaranteed to work)
    print("🔧 Generating automated test cases first...")
    for endpoint in endpoints:
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
        
        # Generate automated test cases (this always works)
        automated_test_cases = TestGenerator._generate_rule_based_test_cases(endpoint_dict, request.base_url)
        
        # Save automated test cases
        for test_case_data in automated_test_cases:
            test_case = TestCaseModel(
                api_spec_id=request.api_spec_id,
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
            generated_test_cases.append(test_case)
    
    # OPTIONALLY try to add AI-generated test cases (if available)
    print("🤖 Attempting to add AI-generated test cases...")
    try:
        from app.core.ai_config import get_rag_generator
        rag_generator = get_rag_generator()
        
        if rag_generator and rag_generator.is_available:
            # Try to generate AI test cases for each endpoint
            for endpoint in endpoints:
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
                
                # Try to generate AI test cases
                ai_test_cases = rag_generator.generate_rag_test_cases(endpoint_dict, api_spec_content, request.base_url)
                
                if ai_test_cases:
                    # Filter out duplicates by comparing with existing automated test cases
                    existing_names = set()
                    for existing_case in generated_test_cases:
                        if existing_case.endpoint_id == endpoint.id:
                            existing_names.add(existing_case.name)
                    
                    # Add unique AI test cases
                    for test_case_data in ai_test_cases:
                        if test_case_data['name'] not in existing_names:
                            test_case = TestCaseModel(
                                api_spec_id=request.api_spec_id,
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
                            generated_test_cases.append(test_case)
                            existing_names.add(test_case_data['name'])
                    
                    print(f"✅ Added {len([tc for tc in ai_test_cases if tc['name'] not in existing_names])} AI test cases for {endpoint.method} {endpoint.path}")
                else:
                    print(f"⚠️  No AI test cases generated for {endpoint.method} {endpoint.path} (quota/limit reached)")
        else:
            print("⚠️  AI generator not available, skipping AI test case generation")
            
    except Exception as e:
        print(f"⚠️  AI generation failed: {str(e)}, continuing with automated test cases only")
    
    db.commit()
    
    # Refresh all test cases to get IDs
    for test_case in generated_test_cases:
        db.refresh(test_case)
    
    # Count results
    automated_count = sum(1 for tc in generated_test_cases if tc.test_type == TestCaseType.AUTOMATED)
    ai_count = sum(1 for tc in generated_test_cases if tc.test_type == TestCaseType.AI_GENERATED)
    
    print(f"🎉 Generation complete: {automated_count} automated + {ai_count} AI-generated = {len(generated_test_cases)} total test cases")
    
    return generated_test_cases

@router.post("/generate-rag-bulk", response_model=List[TestCase])
async def generate_rag_test_cases_bulk(
    request: GenerateTestCasesRequest,
    db: Session = Depends(get_db)
):
    """Generate automated test cases first for ALL endpoints, then optionally add AI-powered ones if available"""
    
    # Get API spec
    api_spec = db.query(APISpecModel).filter(APISpecModel.id == request.api_spec_id).first()
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    
    # Load API spec content for RAG generation
    api_spec_content = {}
    if api_spec.file_path and os.path.exists(api_spec.file_path):
        try:
            spec_info = APIParser.validate_spec_file(api_spec.file_path)
            api_spec_content = spec_info.get('content', {})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load API spec content: {str(e)}")
    
    # Get ALL endpoints in the API spec
    endpoints = db.query(EndpointModel).filter(EndpointModel.api_spec_id == request.api_spec_id).all()
    
    if not endpoints:
        raise HTTPException(status_code=404, detail="No endpoints found for this API specification")
    
    generated_test_cases = []
    
    # ALWAYS generate automated test cases first for all endpoints (guaranteed to work)
    print("🔧 Generating automated test cases for all endpoints first...")
    for endpoint in endpoints:
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
        
        # Generate automated test cases (this always works)
        automated_test_cases = TestGenerator._generate_rule_based_test_cases(endpoint_dict, request.base_url)
        
        # Save automated test cases
        for test_case_data in automated_test_cases:
            test_case = TestCaseModel(
                api_spec_id=request.api_spec_id,
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
            generated_test_cases.append(test_case)
    
    # OPTIONALLY try to add AI-generated test cases for all endpoints (if available)
    print("🤖 Attempting to add AI-generated test cases for all endpoints...")
    try:
        from app.core.ai_config import get_rag_generator
        rag_generator = get_rag_generator()
        
        if rag_generator and rag_generator.is_available:
            # Convert all endpoints to dict format for bulk generation
            all_endpoints = []
            for endpoint in endpoints:
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
                all_endpoints.append(endpoint_dict)
            
            # Try bulk AI generation
            if hasattr(rag_generator, 'generate_rag_test_cases_for_all_endpoints'):
                all_ai_test_cases = rag_generator.generate_rag_test_cases_for_all_endpoints(all_endpoints, api_spec_content, request.base_url)
            else:
                # Fallback to individual generation
                all_ai_test_cases = {}
                for endpoint_dict in all_endpoints:
                    endpoint_key = f"{endpoint_dict['method']}_{endpoint_dict['path']}"
                    ai_cases = rag_generator.generate_rag_test_cases(endpoint_dict, api_spec_content, request.base_url)
                    if ai_cases:
                        all_ai_test_cases[endpoint_key] = ai_cases
            
            # Map AI test cases back to endpoints and add unique ones
            endpoint_map = {f"{ep.method}_{ep.path}": ep for ep in endpoints}
            
            for endpoint_key, ai_test_cases in all_ai_test_cases.items():
                if endpoint_key in endpoint_map:
                    endpoint = endpoint_map[endpoint_key]
                    
                    # Filter out duplicates by comparing with existing automated test cases
                    existing_names = set()
                    for existing_case in generated_test_cases:
                        if existing_case.endpoint_id == endpoint.id:
                            existing_names.add(existing_case.name)
                    
                    # Add unique AI test cases
                    added_count = 0
                    for test_case_data in ai_test_cases:
                        if test_case_data['name'] not in existing_names:
                            test_case = TestCaseModel(
                                api_spec_id=request.api_spec_id,
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
                            generated_test_cases.append(test_case)
                            existing_names.add(test_case_data['name'])
                            added_count += 1
                    
                    if added_count > 0:
                        print(f"✅ Added {added_count} AI test cases for {endpoint.method} {endpoint.path}")
                    else:
                        print(f"⚠️  No unique AI test cases added for {endpoint.method} {endpoint.path}")
        else:
            print("⚠️  AI generator not available, skipping AI test case generation")
            
    except Exception as e:
        print(f"⚠️  AI generation failed: {str(e)}, continuing with automated test cases only")
    
    db.commit()
    
    # Refresh all test cases to get IDs
    for test_case in generated_test_cases:
        db.refresh(test_case)
    
    # Count results
    automated_count = sum(1 for tc in generated_test_cases if tc.test_type == TestCaseType.AUTOMATED)
    ai_count = sum(1 for tc in generated_test_cases if tc.test_type == TestCaseType.AI_GENERATED)
    
    print(f"🎉 Bulk generation complete: {automated_count} automated + {ai_count} AI-generated = {len(generated_test_cases)} total test cases")
    
    return generated_test_cases

@router.get("/", response_model=List[TestCase])
async def list_test_cases(
    api_spec_id: int = None,
    endpoint_id: int = None,
    test_type: str = None,
    priority: str = None,
    sort: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List test cases with optional filtering and sorting by priority"""
    query = db.query(TestCaseModel)
    
    if api_spec_id:
        query = query.filter(TestCaseModel.api_spec_id == api_spec_id)
    
    if endpoint_id:
        query = query.filter(TestCaseModel.endpoint_id == endpoint_id)
    
    if test_type:
        # Convert test_type to uppercase to match database enum values
        test_type_upper = test_type.upper()
        query = query.filter(TestCaseModel.test_type == test_type_upper)
    
    if priority:
        query = query.filter(TestCaseModel.priority == priority)
    
    # Add sorting by priority if requested
    if sort == "priority":
        priority_order = case(
            (TestCaseModel.priority == "CRITICAL", 1),
            (TestCaseModel.priority == "HIGH", 2),
            (TestCaseModel.priority == "MEDIUM", 3),
            (TestCaseModel.priority == "LOW", 4),
            else_=5
        )
        query = query.order_by(priority_order)
    
    test_cases = query.offset(skip).limit(limit).all()
    return test_cases

@router.get("/{test_case_id}", response_model=TestCase)
async def get_test_case(
    test_case_id: int,
    db: Session = Depends(get_db)
):
    """Get test case by ID"""
    test_case = db.query(TestCaseModel).filter(TestCaseModel.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case

@router.put("/{test_case_id}", response_model=TestCase)
async def update_test_case(
    test_case_id: int,
    test_case_update: TestCaseUpdate,
    db: Session = Depends(get_db)
):
    """Update test case"""
    test_case = db.query(TestCaseModel).filter(TestCaseModel.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    update_data = test_case_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test_case, field, value)
    
    db.commit()
    db.refresh(test_case)
    return test_case

@router.delete("/{test_case_id}")
async def delete_test_case(
    test_case_id: int,
    db: Session = Depends(get_db)
):
    """Delete test case"""
    test_case = db.query(TestCaseModel).filter(TestCaseModel.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    db.delete(test_case)
    db.commit()
    
    return {"message": "Test case deleted successfully"}

@router.get("/{test_case_id}/results", response_model=List[TestResult])
async def get_test_case_results(
    test_case_id: int,
    db: Session = Depends(get_db)
):
    """Get test results for a test case"""
    results = db.query(TestResultModel).filter(TestResultModel.test_case_id == test_case_id).all()
    return results 