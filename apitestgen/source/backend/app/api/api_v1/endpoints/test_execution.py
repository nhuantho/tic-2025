from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import os
from datetime import datetime

from app.core.database import get_db
from app.schemas.test_case import TestCase, TestResult
from app.services.test_executor import TestExecutor
from app.services.report_generator import ReportGenerator
from app.models.test_case import TestCase as TestCaseModel, TestResult as TestResultModel
from app.models.api_spec import APISpec as APISpecModel, Endpoint as EndpointModel
from app.core.config import settings

router = APIRouter()

class ExecuteTestRequest(BaseModel):
    test_case_ids: List[int]
    base_url: str = ""

class ExecuteCurlRequest(BaseModel):
    curl_command: str

class RunTestRequest(BaseModel):
    test_case_ids: List[int]
    base_url: str = ""
    service_name: str = ""

class MultiServiceTestRequest(BaseModel):
    service_configs: Dict[str, Dict[str, Any]]  # { "service_name": { "base_url": "...", "api_spec_id": 1 } }
    test_case_ids: List[int] = []

@router.post("/multi-service", response_model=Dict[str, Any])
async def run_multi_service_tests(
    request: MultiServiceTestRequest,
    db: Session = Depends(get_db)
):
    """Run tests across multiple services with inter-service communication analysis"""
    
    # Get test cases if specific IDs provided, otherwise get all for the services
    if request.test_case_ids:
        test_cases = db.query(TestCaseModel).filter(TestCaseModel.id.in_(request.test_case_ids)).all()
    else:
        # Get all test cases for the specified services
        api_spec_ids = [config.get('api_spec_id') for config in request.service_configs.values() if config.get('api_spec_id')]
        test_cases = db.query(TestCaseModel).filter(TestCaseModel.api_spec_id.in_(api_spec_ids)).all()
    
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found for the specified services")
    
    # Convert test cases to dict format for executor
    test_case_dicts = []
    for test_case in test_cases:
        endpoint = db.query(EndpointModel).filter(EndpointModel.id == test_case.endpoint_id).first()
        test_case_dict = {
            'id': test_case.id,
            'name': test_case.name,
            'method': endpoint.method if endpoint else 'GET',
            'path': endpoint.path if endpoint else '',
            'priority': test_case.priority.value if test_case.priority else 'medium',
            'input_data': test_case.input_data,
            'expected_status_code': test_case.expected_status_code,
            'curl_command': test_case.curl_command,
            'base_url': next(
                (config.get('base_url', '') for config in request.service_configs.values() 
                 if config.get('api_spec_id') == test_case.api_spec_id), 
                ''
            )
        }
        test_case_dicts.append(test_case_dict)
    
    # Execute multi-service tests
    results = await TestExecutor.execute_multi_service_test(test_case_dicts, request.service_configs)
    
    # Save results to database
    saved_results = []
    for result in results.get('results', []):
        test_result = TestResultModel(
            test_case_id=result['test_case']['id'],
            status=result['status'],
            response_status_code=result.get('response_status_code'),
            response_body=result.get('response_body'),
            response_time=result.get('response_time', 0),
            error_message=result.get('error_message'),
            execution_log=result.get('execution_log')
        )
        db.add(test_result)
        saved_results.append(test_result)
    
    db.commit()
    
    # Generate and save multi-service report
    report_filepath = ReportGenerator.generate_multi_service_report(request.service_configs, results)
    
    return {
        "status": "completed",
        "report_filepath": report_filepath,
        "results": results,
        "results_count": len(saved_results)
    }

@router.post("/run", response_model=Dict[str, Any])
async def run_tests_and_save_report(
    request: RunTestRequest,
    db: Session = Depends(get_db)
):
    """Run test cases and save markdown report"""
    
    # Get test cases with endpoint and API spec info
    test_cases = db.query(TestCaseModel).filter(TestCaseModel.id.in_(request.test_case_ids)).all()
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found")
    
    # Get service name from first test case if not provided
    if not request.service_name:
        first_test_case = test_cases[0]
        api_spec = db.query(APISpecModel).filter(APISpecModel.id == first_test_case.api_spec_id).first()
        service_name = api_spec.name if api_spec else "unknown"
    else:
        service_name = request.service_name
    
    # Convert test cases to dict format for executor
    test_case_dicts = []
    for test_case in test_cases:
        endpoint = db.query(EndpointModel).filter(EndpointModel.id == test_case.endpoint_id).first()
        test_case_dict = {
            'id': test_case.id,
            'name': test_case.name,
            'method': endpoint.method if endpoint else 'GET',
            'path': endpoint.path if endpoint else '',
            'priority': test_case.priority.value if test_case.priority else 'medium',
            'input_data': test_case.input_data,
            'expected_status_code': test_case.expected_status_code,
            'curl_command': test_case.curl_command
        }
        test_case_dicts.append(test_case_dict)
    
    # Execute tests
    results = await TestExecutor.execute_test_suite(test_case_dicts, request.base_url)
    
    # Save results to database
    saved_results = []
    for result in results:
        test_result = TestResultModel(
            test_case_id=result['test_case']['id'],
            status=result['status'],
            response_status_code=result.get('response_status_code'),
            response_body=result.get('response_body'),
            response_time=result.get('response_time', 0),
            error_message=result.get('error_message'),
            execution_log=result.get('execution_log')
        )
        db.add(test_result)
        saved_results.append(test_result)
    
    db.commit()
    
    # Calculate execution summary
    total_tests = len(results)
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    errors = sum(1 for r in results if r['status'] == 'error')
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    avg_response_time = sum(r.get('response_time', 0) for r in results) / total_tests if total_tests > 0 else 0
    
    execution_summary = {
        'total_tests': total_tests,
        'passed': passed,
        'failed': failed,
        'errors': errors,
        'success_rate': success_rate,
        'average_response_time': avg_response_time
    }
    
    # Generate and save markdown report
    report_filepath = ReportGenerator.generate_test_report(service_name, results, execution_summary)
    
    return {
        "status": "completed",
        "service_name": service_name,
        "report_filepath": report_filepath,
        "execution_summary": execution_summary,
        "results": results,
        "results_count": len(saved_results)
    }

@router.post("/execute", response_model=Dict[str, Any])
async def execute_test_cases(
    request: ExecuteTestRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Execute test cases"""
    
    # Get test cases
    test_cases = db.query(TestCaseModel).filter(TestCaseModel.id.in_(request.test_case_ids)).all()
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found")
    
    # Convert test cases to dict format for executor
    test_case_dicts = []
    for test_case in test_cases:
        test_case_dict = {
            'id': test_case.id,
            'method': test_case.endpoint.method,
            'path': test_case.endpoint.path,
            'input_data': test_case.input_data,
            'expected_status_code': test_case.expected_status_code
        }
        test_case_dicts.append(test_case_dict)
    
    # Execute tests
    results = await TestExecutor.execute_test_suite(test_case_dicts, request.base_url)
    
    # Save results to database
    saved_results = []
    for result in results:
        test_result = TestResultModel(
            test_case_id=result['test_case']['id'],
            status=result['status'],
            response_status_code=result.get('response_status_code'),
            response_body=result.get('response_body'),
            response_time=result.get('response_time', 0),
            error_message=result.get('error_message'),
            execution_log=result.get('execution_log')
        )
        db.add(test_result)
        saved_results.append(test_result)
    
    db.commit()
    
    # Generate report
    report = TestExecutor.generate_test_report(results)
    
    # Save report to log file
    background_tasks.add_task(save_test_report, report, test_cases[0].api_spec.name if test_cases else "unknown")
    
    return {
        "report": report,
        "results_count": len(saved_results)
    }

@router.post("/execute-curl", response_model=Dict[str, Any])
async def execute_curl_command(
    request: ExecuteCurlRequest
):
    """Execute a CURL command"""
    
    result = await TestExecutor.execute_curl_command(request.curl_command)
    
    return {
        "status": result['status'],
        "output": result.get('output'),
        "error": result.get('error'),
        "response_time": result.get('response_time', 0)
    }

@router.get("/results", response_model=List[TestResult])
async def get_test_results(
    test_case_id: int = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get test execution results"""
    query = db.query(TestResultModel)
    
    if test_case_id:
        query = query.filter(TestResultModel.test_case_id == test_case_id)
    
    if status:
        query = query.filter(TestResultModel.status == status)
    
    results = query.order_by(TestResultModel.created_at.desc()).all()
    return results

@router.get("/results/{result_id}", response_model=TestResult)
async def get_test_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific test result"""
    result = db.query(TestResultModel).filter(TestResultModel.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Test result not found")
    return result

@router.get("/reports")
async def get_reports(service_name: str = None):
    """Get list of available test reports"""
    reports_dir = "logs/reports"
    
    if not os.path.exists(reports_dir):
        return {"reports": []}
    
    reports = []
    for filename in os.listdir(reports_dir):
        if filename.endswith('.md'):
            filepath = os.path.join(reports_dir, filename)
            stat = os.stat(filepath)
            
            # Extract service name from filename
            if filename.startswith('test_report_'):
                parts = filename.split('_')
                if len(parts) >= 3:
                    report_service_name = parts[2]
                else:
                    report_service_name = "unknown"
            elif filename.startswith('multi_service_report_'):
                report_service_name = "multi-service"
            else:
                report_service_name = "unknown"
            
            if not service_name or report_service_name == service_name:
                reports.append({
                    'service_name': report_service_name,
                    'filename': filename,
                    'filepath': filepath,
                    'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    
    # Sort by creation time (newest first)
    reports.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {"reports": reports}

@router.get("/reports/{api_spec_name}")
async def get_reports_by_api_spec(api_spec_name: str):
    """Get reports for a specific API specification"""
    reports_dir = "logs/reports"
    
    if not os.path.exists(reports_dir):
        return {"reports": []}
    
    reports = []
    for filename in os.listdir(reports_dir):
        if filename.startswith(f'test_report_{api_spec_name}_') and filename.endswith('.md'):
            filepath = os.path.join(reports_dir, filename)
            stat = os.stat(filepath)
            
            # Read report content
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                content = "Error reading report content"
            
            reports.append({
                'filename': filename,
                'content': content,
                'created_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
    
    # Sort by creation time (newest first)
    reports.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {"reports": reports}

@router.get("/download-report")
async def download_report(filepath: str):
    """Download a test report file"""
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    filename = os.path.basename(filepath)
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='text/markdown'
    )

async def save_test_report(report: Dict[str, Any], api_spec_name: str):
    """Save test report to log file"""
    logs_dir = settings.LOGS_DIR
    api_spec_logs_dir = os.path.join(logs_dir, "run_test", api_spec_name)
    
    # Create directory if it doesn't exist
    os.makedirs(api_spec_logs_dir, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{timestamp}.md"
    file_path = os.path.join(api_spec_logs_dir, filename)
    
    # Generate markdown report
    markdown_content = generate_markdown_report(report, api_spec_name)
    
    # Save to file
    with open(file_path, 'w') as f:
        f.write(markdown_content)

def generate_markdown_report(report: Dict[str, Any], api_spec_name: str) -> str:
    """Generate markdown report content"""
    summary = report.get('summary', {})
    
    content = f"""# Test Execution Report - {api_spec_name}

## Summary
- Total Tests: {summary.get('total_tests', 0)}
- Passed: {summary.get('passed', 0)}
- Failed: {summary.get('failed', 0)}
- Errors: {summary.get('errors', 0)}
- Success Rate: {summary.get('success_rate', 0):.1f}%

## Results
"""
    
    for result in report.get('results', []):
        status = result.get('status', 'unknown')
        content += f"- {result.get('test_case_name', 'Unknown')}: {status.upper()}\n"
    
    return content 