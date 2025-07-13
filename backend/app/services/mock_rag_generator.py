import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.models.test_case import TestCaseType, TestCasePriority
import logging

logger = logging.getLogger(__name__)

class MockRAGTestGenerator:
    """Mock RAG test generator that simulates AI-generated test cases without OpenAI API"""
    
    def __init__(self):
        self.is_available = True
        logger.info("Mock RAG Generator initialized - no OpenAI API required")
    
    def generate_rag_test_cases(self, endpoint: Dict[str, Any], api_spec: Dict[str, Any], base_url: str = "") -> List[Dict[str, Any]]:
        """Generate mock AI test cases that simulate RAG output"""
        try:
            # Create context from OpenAPI spec
            context = self._create_api_context(endpoint, api_spec)
            
            # Generate test cases using mock AI
            test_cases = []
            
            # Normal test case with mock AI
            normal_case = self._generate_mock_test_case(endpoint, context, "normal", base_url)
            if normal_case:
                test_cases.append(normal_case)
            
            # Edge case with mock AI
            edge_case = self._generate_mock_test_case(endpoint, context, "edge_case", base_url)
            if edge_case:
                test_cases.append(edge_case)
            
            # Security test case with mock AI
            security_case = self._generate_mock_test_case(endpoint, context, "security", base_url)
            if security_case:
                test_cases.append(security_case)
            
            # Business logic test case with mock AI
            business_case = self._generate_mock_test_case(endpoint, context, "business_logic", base_url)
            if business_case:
                test_cases.append(business_case)
            
            return test_cases
            
        except Exception as e:
            logger.error(f"Mock RAG generation failed: {str(e)}, falling back to rule-based")
            return self._fallback_generation(endpoint, base_url)
    
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
    
    def _generate_mock_test_case(self, endpoint: Dict[str, Any], context: str, test_type: str, base_url: str) -> Optional[Dict[str, Any]]:
        """Generate a mock test case that simulates AI output"""
        
        # Generate realistic test data based on endpoint and context
        if test_type == "normal":
            test_data = self._generate_mock_normal_data(endpoint)
            name = f"Realistic {endpoint['method']} {endpoint['path']} - Business Scenario"
            description = f"Tests realistic business scenario for {endpoint['method']} {endpoint['path']} with valid production-like data"
            expected_status = 200
            priority = "medium"
            
        elif test_type == "edge_case":
            test_data = self._generate_mock_edge_data(endpoint)
            name = f"Edge Case {endpoint['method']} {endpoint['path']} - Boundary Testing"
            description = f"Tests boundary conditions and edge cases for {endpoint['method']} {endpoint['path']}"
            expected_status = 400
            priority = "high"
            
        elif test_type == "security":
            test_data = self._generate_mock_security_data(endpoint)
            name = f"Security Test {endpoint['method']} {endpoint['path']} - Vulnerability Assessment"
            description = f"Tests security vulnerabilities for {endpoint['method']} {endpoint['path']}"
            expected_status = 400
            priority = "critical"
            
        elif test_type == "business_logic":
            test_data = self._generate_mock_business_data(endpoint)
            name = f"Business Logic {endpoint['method']} {endpoint['path']} - Workflow Testing"
            description = f"Tests business logic and workflow scenarios for {endpoint['method']} {endpoint['path']}"
            expected_status = 200
            priority = "high"
            
        else:
            return None
        
        # Generate CURL command
        curl_command = self._generate_curl_command(endpoint, base_url, test_data)
        
        return {
            'name': name,
            'description': description,
            'test_type': TestCaseType.AI_GENERATED,
            'priority': self._map_priority(priority),
            'input_data': test_data,
            'expected_status_code': expected_status,
            'curl_command': curl_command,
            'test_script': f"Mock AI-generated {test_type} test script"
        }
    
    def _generate_mock_normal_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic normal test data"""
        data = {
            'body': {},
            'query_params': {},
            'headers': {}
        }
        
        # Generate realistic business data
        if endpoint['method'] in ['POST', 'PUT', 'PATCH'] and endpoint.get('request_body'):
            schema = self._extract_schema_from_request_body(endpoint['request_body'])
            if schema and schema.get('properties'):
                for prop_name, prop_schema in schema['properties'].items():
                    data['body'][prop_name] = self._generate_realistic_value(prop_schema, "normal")
        
        # Generate realistic query parameters
        if endpoint.get('parameters'):
            for param in endpoint['parameters']:
                if param.get('in') == 'query':
                    param_name = param['name']
                    param_schema = param.get('schema', {})
                    data['query_params'][param_name] = self._generate_realistic_value(param_schema, "normal")
        
        return data
    
    def _generate_mock_edge_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate edge case test data"""
        data = {
            'body': {},
            'query_params': {},
            'headers': {}
        }
        
        # Generate edge case data
        if endpoint['method'] in ['POST', 'PUT', 'PATCH'] and endpoint.get('request_body'):
            schema = self._extract_schema_from_request_body(endpoint['request_body'])
            if schema and schema.get('properties'):
                for prop_name, prop_schema in schema['properties'].items():
                    data['body'][prop_name] = self._generate_realistic_value(prop_schema, "edge_case")
        
        return data
    
    def _generate_mock_security_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security test data"""
        data = {
            'body': {},
            'query_params': {},
            'headers': {}
        }
        
        # Generate security test payloads
        security_payloads = [
            "'; DROP TABLE users; --",
            "<script>alert('XSS')</script>",
            "../../../etc/passwd",
            "admin' OR '1'='1",
            "javascript:alert('XSS')"
        ]
        
        if endpoint['method'] in ['POST', 'PUT', 'PATCH'] and endpoint.get('request_body'):
            schema = self._extract_schema_from_request_body(endpoint['request_body'])
            if schema and schema.get('properties'):
                for prop_name, prop_schema in schema['properties'].items():
                    if prop_schema.get('type') == 'string':
                        data['body'][prop_name] = random.choice(security_payloads)
                    else:
                        data['body'][prop_name] = self._generate_realistic_value(prop_schema, "edge_case")
        
        return data
    
    def _generate_mock_business_data(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business logic test data"""
        data = {
            'body': {},
            'query_params': {},
            'headers': {}
        }
        
        # Generate business scenario data
        if endpoint['method'] in ['POST', 'PUT', 'PATCH'] and endpoint.get('request_body'):
            schema = self._extract_schema_from_request_body(endpoint['request_body'])
            if schema and schema.get('properties'):
                for prop_name, prop_schema in schema['properties'].items():
                    data['body'][prop_name] = self._generate_realistic_value(prop_schema, "business_logic")
        
        return data
    
    def _generate_realistic_value(self, schema: Dict[str, Any], value_type: str) -> Any:
        """Generate realistic values based on schema"""
        schema_type = schema.get('type', 'string')
        
        if schema_type == 'string':
            if 'enum' in schema:
                return random.choice(schema['enum'])
            elif 'format' in schema:
                if schema['format'] == 'email':
                    domains = ['gmail.com', 'yahoo.com', 'company.com', 'business.org']
                    names = ['john.doe', 'jane.smith', 'admin', 'user']
                    return f"{random.choice(names)}@{random.choice(domains)}"
                elif schema['format'] == 'date':
                    return datetime.now().strftime('%Y-%m-%d')
                elif schema['format'] == 'datetime':
                    return datetime.now().isoformat()
            else:
                realistic_strings = [
                    "realistic_test_data",
                    "business_value",
                    "production_like",
                    "user_friendly"
                ]
                return random.choice(realistic_strings)
        
        elif schema_type == 'integer':
            if value_type == "edge_case":
                return random.choice([-999999, 999999999, 0])
            else:
                return random.randint(1, 100)
        
        elif schema_type == 'number':
            if value_type == "edge_case":
                return random.choice([1e308, -1e308, 0.0])
            else:
                return round(random.uniform(1.0, 100.0), 2)
        
        elif schema_type == 'boolean':
            return random.choice([True, False])
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            count = random.randint(1, 3)
            return [self._generate_realistic_value(items_schema, value_type) for _ in range(count)]
        
        return "mock_value"
    
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
        """Fallback to rule-based generation when mock AI is not available"""
        from app.services.test_generator import TestGenerator
        return TestGenerator._generate_rule_based_test_cases(endpoint, base_url) 