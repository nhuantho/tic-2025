import asyncio
import httpx
import json
import time
import subprocess
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models.test_case import TestResult
from app.core.config import settings

class TestExecutor:
    """Service to execute test cases with multi-service support"""
    
    @staticmethod
    async def execute_test_case(test_case: Dict[str, Any], base_url: str = "", service_configs: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute a single test case with multi-service support"""
        start_time = time.time()
        
        try:
            # Execute the test with service context
            result = await TestExecutor._execute_http_request(test_case, base_url, service_configs)
            
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)  # milliseconds
            
            # Determine test status
            status = TestExecutor._determine_test_status(result, test_case)
            
            return {
                'status': status,
                'response_status_code': result.get('status_code'),
                'response_body': result.get('body'),
                'response_time': response_time,
                'error_message': result.get('error'),
                'execution_log': result.get('log'),
                'service_calls': result.get('service_calls', [])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'response_status_code': None,
                'response_body': None,
                'response_time': int((time.time() - start_time) * 1000),
                'error_message': f"Test execution failed: {str(e)}",
                'execution_log': f"Exception occurred during test execution: {str(e)}",
                'service_calls': []
            }
    
    @staticmethod
    def _fix_localhost_url(base_url: str) -> str:
        """Convert localhost to host.docker.internal when running in Docker"""
        # Check if we're running in Docker (common Docker environment variables)
        is_docker = os.environ.get('DOCKER_CONTAINER') or os.path.exists('/.dockerenv')
        
        if is_docker and 'localhost' in base_url:
            # Replace localhost with host.docker.internal for Docker containers
            return base_url.replace('localhost', 'host.docker.internal')
        
        return base_url
    
    @staticmethod
    async def _execute_http_request(test_case: Dict[str, Any], base_url: str, service_configs: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute HTTP request for test case with multi-service support"""
        input_data = test_case.get('input_data', {})
        method = test_case.get('method', 'GET')
        path = test_case.get('path', '')
        service_calls = []
        
        # Validate base URL
        if not base_url:
            return {
                'status_code': None,
                'body': None,
                'error': 'Base URL is required. Please provide a valid API endpoint URL (e.g., http://localhost:8001)',
                'log': f"Request: {method} {path}\nError: No base URL provided",
                'service_calls': service_calls
            }
        
        # Ensure base URL has proper format
        if not base_url.startswith(('http://', 'https://')):
            base_url = f"http://{base_url}"
        
        # Fix localhost URL for Docker containers
        base_url = TestExecutor._fix_localhost_url(base_url)
        
        url = f"{base_url}{path}"
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add authentication header if provided
        if input_data.get('auth_token'):
            headers['Authorization'] = f"Bearer {input_data['auth_token']}"
        
        # Add custom headers
        if input_data.get('headers'):
            headers.update(input_data['headers'])
        
        # Add service context headers for inter-service communication
        if service_configs:
            headers['X-Service-Context'] = json.dumps({
                'source_service': 'apitestgen',
                'target_service': TestExecutor._extract_service_name_from_url(base_url),
                'available_services': list(service_configs.keys())
            })
        
        # Prepare query parameters
        params = input_data.get('query_params', {})
        
        # Prepare request body
        data = None
        if method in ['POST', 'PUT', 'PATCH'] and input_data.get('body'):
            data = json.dumps(input_data['body'])
        
        # Execute request
        async with httpx.AsyncClient(timeout=settings.TEST_TIMEOUT) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=data
                )
                
                # Track service calls if response indicates inter-service communication
                if 'X-Service-Calls' in response.headers:
                    try:
                        service_calls = json.loads(response.headers['X-Service-Calls'])
                    except:
                        service_calls = []
                
                return {
                    'status_code': response.status_code,
                    'body': response.text,
                    'headers': dict(response.headers),
                    'log': f"Request: {method} {url}\nResponse: {response.status_code}",
                    'service_calls': service_calls
                }
                
            except httpx.TimeoutException:
                return {
                    'status_code': None,
                    'body': None,
                    'error': f'Request timeout after {settings.TEST_TIMEOUT} seconds. The API server may be slow or unresponsive.',
                    'log': f"Request: {method} {url}\nError: Timeout after {settings.TEST_TIMEOUT}s",
                    'service_calls': service_calls
                }
            except httpx.ConnectError:
                return {
                    'status_code': None,
                    'body': None,
                    'error': f'Connection failed. Please check if the API server is running at {base_url}',
                    'log': f"Request: {method} {url}\nError: Connection failed - server may not be running",
                    'service_calls': service_calls
                }
            except httpx.RequestError as e:
                return {
                    'status_code': None,
                    'body': None,
                    'error': f'Request error: {str(e)}. Please verify the API endpoint and network connectivity.',
                    'log': f"Request: {method} {url}\nError: {str(e)}",
                    'service_calls': service_calls
                }
    
    @staticmethod
    def _extract_service_name_from_url(url: str) -> str:
        """Extract service name from URL for tracking"""
        try:
            # Extract hostname and port
            from urllib.parse import urlparse
            parsed = urlparse(url)
            hostname = parsed.hostname or ''
            port = parsed.port or ''
            
            # Map common ports to service names
            port_service_map = {
                '8001': 'user-api',
                '8002': 'ecommerce-api',
                '8000': 'apitestgen'
            }
            
            if port and str(port) in port_service_map:
                return port_service_map[str(port)]
            
            # Try to extract from hostname
            if 'user' in hostname.lower():
                return 'user-api'
            elif 'ecommerce' in hostname.lower() or 'shop' in hostname.lower():
                return 'ecommerce-api'
            else:
                return hostname or 'unknown'
        except:
            return 'unknown'
    
    @staticmethod
    def _determine_test_status(result: Dict[str, Any], test_case: Dict[str, Any]) -> str:
        """Determine if test passed, failed, or had an error"""
        if result.get('error'):
            return 'error'
        
        expected_status = test_case.get('expected_status_code')
        actual_status = result.get('status_code')
        
        if expected_status and actual_status != expected_status:
            return 'failed'
        
        return 'passed'
    
    @staticmethod
    async def execute_curl_command(curl_command: str) -> Dict[str, Any]:
        """Execute a CURL command and return results"""
        start_time = time.time()
        
        try:
            # Execute CURL command
            process = await asyncio.create_subprocess_shell(
                curl_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            response_time = int((time.time() - start_time) * 1000)
            
            if process.returncode == 0:
                return {
                    'status': 'passed',
                    'output': stdout.decode(),
                    'error': stderr.decode() if stderr else None,
                    'response_time': response_time
                }
            else:
                return {
                    'status': 'failed',
                    'output': stdout.decode(),
                    'error': stderr.decode(),
                    'response_time': response_time
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'output': None,
                'error': str(e),
                'response_time': int((time.time() - start_time) * 1000)
            }
    
    @staticmethod
    async def execute_test_suite(test_cases: List[Dict[str, Any]], base_url: str = "", service_configs: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Execute multiple test cases concurrently with multi-service support"""
        # Limit concurrent executions
        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_TESTS)
        
        async def execute_with_semaphore(test_case):
            async with semaphore:
                return await TestExecutor.execute_test_case(test_case, base_url, service_configs)
        
        # Execute all test cases
        tasks = [execute_with_semaphore(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'test_case': test_cases[i],
                    'status': 'error',
                    'error_message': f"Test execution failed: {str(result)}",
                    'response_time': 0,
                    'service_calls': []
                })
            else:
                processed_results.append({
                    'test_case': test_cases[i],
                    **result
                })
        
        return processed_results
    
    @staticmethod
    async def execute_multi_service_test(test_cases: List[Dict[str, Any]], service_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tests across multiple services"""
        all_results = []
        service_results = {}
        
        for service_name, service_config in service_configs.items():
            # Filter test cases for this service
            service_test_cases = [
                tc for tc in test_cases 
                if TestExecutor._extract_service_name_from_url(service_config.get('base_url', '')) == service_name
            ]
            
            if service_test_cases:
                results = await TestExecutor.execute_test_suite(
                    service_test_cases, 
                    service_config.get('base_url', ''),
                    service_configs
                )
                service_results[service_name] = results
                all_results.extend(results)
        
        # Generate inter-service communication report
        inter_service_report = TestExecutor._generate_inter_service_report(all_results, service_configs)
        
        return {
            'results': all_results,
            'service_results': service_results,
            'inter_service_report': inter_service_report
        }
    
    @staticmethod
    def _generate_inter_service_report(results: List[Dict[str, Any]], service_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report for inter-service communication"""
        service_calls = []
        service_dependencies = {}
        
        for result in results:
            calls = result.get('service_calls', [])
            service_calls.extend(calls)
            
            # Track dependencies
            test_case = result.get('test_case', {})
            service_name = TestExecutor._extract_service_name_from_url(test_case.get('base_url', ''))
            if service_name not in service_dependencies:
                service_dependencies[service_name] = set()
            
            for call in calls:
                service_dependencies[service_name].add(call.get('target_service', 'unknown'))
        
        return {
            'total_service_calls': len(service_calls),
            'service_calls': service_calls,
            'service_dependencies': {k: list(v) for k, v in service_dependencies.items()},
            'communication_patterns': TestExecutor._analyze_communication_patterns(service_calls)
        }
    
    @staticmethod
    def _analyze_communication_patterns(service_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze communication patterns between services"""
        patterns = {
            'synchronous_calls': 0,
            'asynchronous_calls': 0,
            'error_propagation': 0,
            'circular_dependencies': []
        }
        
        for call in service_calls:
            if call.get('type') == 'sync':
                patterns['synchronous_calls'] += 1
            elif call.get('type') == 'async':
                patterns['asynchronous_calls'] += 1
            
            if call.get('error_propagated'):
                patterns['error_propagation'] += 1
        
        return patterns 