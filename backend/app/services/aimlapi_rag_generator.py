import json
from openai import OpenAI
from typing import Dict, List, Any, Optional
from app.models.test_case import TestCaseType, TestCasePriority
from app.core.ai_config import ai_config
import logging

logger = logging.getLogger(__name__)

class AIMLAPIRAGTestGenerator:
    """RAG test generator using AIMLAPI.com API with OpenAI client"""
    
    def __init__(self):
        self.aimlapi_client = None
        self.is_available = False
        
        if ai_config.AIMLAPI_API_KEY:
            try:
                # Initialize OpenAI client with AIMLAPI endpoint
                self.aimlapi_client = OpenAI(
                    base_url=f"{ai_config.AIMLAPI_BASE_URL}/v1",
                    api_key=ai_config.AIMLAPI_API_KEY
                )
                
                # Test the API key with a simple request
                test_response = self.aimlapi_client.chat.completions.create(
                    model=ai_config.AIMLAPI_MODEL,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                
                if test_response.choices:
                    self.is_available = True
                    logger.info("AIMLAPI.com API is available and working")
                else:
                    logger.warning("AIMLAPI.com API test failed: No response choices")
                    self.is_available = False
                    
            except Exception as e:
                logger.warning(f"AIMLAPI.com API not available: {str(e)}")
                self.is_available = False
        else:
            logger.warning("AIMLAPI.com API key not configured")
    
    def generate_rag_test_cases(self, endpoint: Dict[str, Any], api_spec: Dict[str, Any], base_url: str = "") -> List[Dict[str, Any]]:
        """Generate test cases using RAG approach with AIMLAPI.com (max 5 test cases)"""
        if not self.is_available:
            logger.warning("AIMLAPI.com API not available, falling back to rule-based generation")
            return self._fallback_generation(endpoint, base_url)
        
        # Create context from OpenAPI spec
        context = self._create_api_context(endpoint, api_spec)
        
        # Generate test cases using AIMLAPI.com (limited to 5)
        test_cases = []
        
        # Define test types to generate (max 5)
        test_types = ["normal", "edge_case", "security", "business_logic", "performance"]
        
        for test_type in test_types[:5]:  # Ensure max 5 test cases
            test_case = self._generate_test_case(endpoint, context, test_type, base_url)
            if test_case:
                test_cases.append(test_case)
            
            # Stop if we have 5 test cases
            if len(test_cases) >= 5:
                break
        
        return test_cases
    
    def _create_api_context(self, endpoint: Dict[str, Any], api_spec: Dict[str, Any]) -> str:
        """Create context string from OpenAPI specification"""
        context_parts = []
        
        # API Info
        info = api_spec.get('info', {})
        context_parts.append(f"API: {info.get('title', 'Unknown API')}")
        context_parts.append(f"Version: {info.get('version', 'Unknown')}")
        context_parts.append(f"Description: {info.get('description', 'No description')}")
        
        # Endpoint details
        context_parts.append(f"\nEndpoint: {endpoint['method']} {endpoint['path']}")
        context_parts.append(f"Summary: {endpoint.get('summary', 'No summary')}")
        context_parts.append(f"Description: {endpoint.get('description', 'No description')}")
        
        # Parameters
        if endpoint.get('parameters'):
            context_parts.append("\nParameters:")
            for param in endpoint['parameters']:
                param_info = f"  - {param.get('name')} ({param.get('in', 'unknown')}): {param.get('type', 'unknown')}"
                if param.get('required'):
                    param_info += " [REQUIRED]"
                if param.get('description'):
                    param_info += f" - {param['description']}"
                context_parts.append(param_info)
        
        # Request body schema
        if endpoint.get('request_body'):
            context_parts.append("\nRequest Body Schema:")
            schema = self._extract_schema_from_request_body(endpoint['request_body'])
            if schema:
                context_parts.append(json.dumps(schema, indent=2))
        
        # Response schemas
        if endpoint.get('responses'):
            context_parts.append("\nResponse Schemas:")
            for status_code, response in endpoint['responses'].items():
                context_parts.append(f"  {status_code}: {response.get('description', 'No description')}")
                schema = self._extract_schema_from_response(response)
                if schema:
                    context_parts.append(f"    Schema: {json.dumps(schema, indent=4)}")
        
        # Tags and categories
        if endpoint.get('tags'):
            context_parts.append(f"\nTags: {', '.join(endpoint['tags'])}")
        
        return "\n".join(context_parts)
    
    def _extract_schema_from_request_body(self, request_body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract JSON schema from request body"""
        if 'content' in request_body:
            for content_type, content_spec in request_body['content'].items():
                if content_type == 'application/json' and 'schema' in content_spec:
                    return content_spec['schema']
        return None
    
    def _extract_schema_from_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract JSON schema from response"""
        if 'content' in response:
            for content_type, content_spec in response['content'].items():
                if content_type == 'application/json' and 'schema' in content_spec:
                    return content_spec['schema']
        return None
    
    def _generate_test_case(self, endpoint: Dict[str, Any], context: str, test_type: str, base_url: str) -> Optional[Dict[str, Any]]:
        """Generate a test case using AIMLAPI.com API"""
        
        # Create prompt based on test type
        if test_type == "normal":
            prompt = f"""Based on this API specification context:

{context}

Generate a NORMAL test case for the endpoint {endpoint['method']} {endpoint['path']}. 
Focus on realistic business scenarios with valid data.

Return a JSON object with this structure:
{{
    "name": "Descriptive test name",
    "description": "What this test validates",
    "priority": "medium",
    "input_data": {{
        "body": {{}},
        "query_params": {{}},
        "headers": {{}}
    }},
    "expected_status_code": 200,
    "test_script": "Brief description of test logic"
}}"""
            
        elif test_type == "edge_case":
            prompt = f"""Based on this API specification context:

{context}

Generate an EDGE CASE test case for the endpoint {endpoint['method']} {endpoint['path']}. 
Focus on boundary conditions, invalid inputs, and edge scenarios.

Return a JSON object with this structure:
{{
    "name": "Descriptive test name",
    "description": "What edge case this test validates",
    "priority": "high",
    "input_data": {{
        "body": {{}},
        "query_params": {{}},
        "headers": {{}}
    }},
    "expected_status_code": 400,
    "test_script": "Brief description of test logic"
}}"""
            
        elif test_type == "security":
            prompt = f"""Based on this API specification context:

{context}

Generate a SECURITY test case for the endpoint {endpoint['method']} {endpoint['path']}. 
Focus on security vulnerabilities like SQL injection, XSS, authentication bypass, etc.

Return a JSON object with this structure:
{{
    "name": "Descriptive security test name",
    "description": "What security vulnerability this test validates",
    "priority": "critical",
    "input_data": {{
        "body": {{}},
        "query_params": {{}},
        "headers": {{}}
    }},
    "expected_status_code": 400,
    "test_script": "Brief description of security test logic"
}}"""
            
        elif test_type == "business_logic":
            prompt = f"""Based on this API specification context:

{context}

Generate a BUSINESS LOGIC test case for the endpoint {endpoint['method']} {endpoint['path']}. 
Focus on business rules, workflow scenarios, and domain-specific validations.

Return a JSON object with this structure:
{{
    "name": "Descriptive business logic test name",
    "description": "What business rule this test validates",
    "priority": "high",
    "input_data": {{
        "body": {{}},
        "query_params": {{}},
        "headers": {{}}
    }},
    "expected_status_code": 200,
    "test_script": "Brief description of business logic test"
}}"""
            
        elif test_type == "performance":
            prompt = f"""Based on this API specification context:

{context}

Generate a PERFORMANCE test case for the endpoint {endpoint['method']} {endpoint['path']}. 
Focus on load testing, stress testing, and performance validation.

Return a JSON object with this structure:
{{
    "name": "Descriptive performance test name",
    "description": "What performance aspect this test validates",
    "priority": "medium",
    "input_data": {{
        "body": {{}},
        "query_params": {{}},
        "headers": {{}}
    }},
    "expected_status_code": 200,
    "test_script": "Brief description of performance test"
}}"""
            
        else:
            return None
        
        try:
            response = self.aimlapi_client.chat.completions.create(
                model=ai_config.AIMLAPI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert API testing engineer. Generate realistic test cases based on the provided OpenAPI specification context. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=ai_config.AIMLAPI_TEMPERATURE,
                max_tokens=ai_config.AIMLAPI_MAX_TOKENS
            )
            
            if not response.choices:
                logger.error("AIMLAPI.com API request failed: No response choices")
                return None
            
            # Parse the response
            content = response.choices[0].message.content
            test_data = json.loads(content)
            
            # Generate CURL command
            curl_command = self._generate_curl_command(endpoint, base_url, test_data.get('input_data', {}))
            
            return {
                'name': test_data.get('name', f"{test_type.title()} {endpoint['method']} {endpoint['path']}"),
                'description': test_data.get('description', f"AIMLAPI.com AI-generated {test_type} test for {endpoint['method']} {endpoint['path']}"),
                'test_type': TestCaseType.AI_GENERATED,
                'priority': self._map_priority(test_data.get('priority', 'medium')),
                'input_data': test_data.get('input_data', {}),
                'expected_status_code': test_data.get('expected_status_code', 200),
                'curl_command': curl_command,
                'test_script': test_data.get('test_script', '')
            }
            
        except Exception as e:
            logger.error(f"Failed to generate {test_type} test case with AIMLAPI.com: {str(e)}")
            return None
    
    def _generate_curl_command(self, endpoint: Dict[str, Any], base_url: str, test_data: Dict[str, Any]) -> str:
        """Generate CURL command for the test case"""
        method = endpoint['method']
        path = endpoint['path']
        url = f"{base_url}{path}"
        
        curl_parts = [f"curl -X {method}"]
        curl_parts.append('-H "Content-Type: application/json"')
        
        # Add headers
        if test_data.get('headers'):
            for key, value in test_data['headers'].items():
                curl_parts.append(f'-H "{key}: {value}"')
        
        # Add request body
        if method in ['POST', 'PUT', 'PATCH'] and test_data.get('body'):
            body_json = json.dumps(test_data['body'])
            curl_parts.append(f'-d \'{body_json}\'')
        
        # Add query parameters
        if test_data.get('query_params'):
            query_params = []
            for key, value in test_data['query_params'].items():
                query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        
        curl_parts.append(f'"{url}"')
        return " ".join(curl_parts)
    
    def _map_priority(self, priority_str: str) -> TestCasePriority:
        """Map string priority to enum"""
        priority_map = {
            'low': TestCasePriority.LOW,
            'medium': TestCasePriority.MEDIUM,
            'high': TestCasePriority.HIGH,
            'critical': TestCasePriority.CRITICAL
        }
        return priority_map.get(priority_str.lower(), TestCasePriority.MEDIUM)
    
    def _fallback_generation(self, endpoint: Dict[str, Any], base_url: str) -> List[Dict[str, Any]]:
        """Fallback to rule-based generation when AIMLAPI.com is not available"""
        from app.services.test_generator import TestGenerator
        return TestGenerator._generate_rule_based_test_cases(endpoint, base_url) 