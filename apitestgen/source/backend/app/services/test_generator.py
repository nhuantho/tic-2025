import json
import random
import string
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.models.test_case import TestCaseType, TestCasePriority

class TestGenerator:
    """Service to generate test cases from API specifications"""
    
    @staticmethod
    def generate_curl_command(endpoint: Dict[str, Any], base_url: str = "", test_data: Dict[str, Any] = None) -> str:
        """Generate CURL command for an endpoint"""
        method = endpoint['method']
        path = endpoint['path']
        url = f"{base_url}{path}"
        
        # Build CURL command
        curl_parts = [f"curl -X {method}"]
        
        # Add headers
        curl_parts.append('-H "Content-Type: application/json"')
        
        # Add authentication header if needed
        if test_data and test_data.get('auth_token'):
            curl_parts.append(f'-H "Authorization: Bearer {test_data["auth_token"]}"')
        
        # Add request body for POST/PUT/PATCH
        if method in ['POST', 'PUT', 'PATCH'] and test_data and test_data.get('body'):
            body_json = json.dumps(test_data['body'])
            curl_parts.append(f'-d \'{body_json}\'')
        
        # Add query parameters
        if test_data and test_data.get('query_params'):
            query_params = []
            for key, value in test_data['query_params'].items():
                query_params.append(f"{key}={value}")
            if query_params:
                url += "?" + "&".join(query_params)
        
        curl_parts.append(f'"{url}"')
        
        return " ".join(curl_parts)
    
    @staticmethod
    def generate_test_data(endpoint: Dict[str, Any], test_type: str = "normal") -> Dict[str, Any]:
        """Generate test data for an endpoint"""
        test_data = {
            'body': {},
            'query_params': {},
            'headers': {}
        }
        
        # Generate body data for POST/PUT/PATCH
        if endpoint['method'] in ['POST', 'PUT', 'PATCH'] and endpoint.get('request_body'):
            test_data['body'] = TestGenerator._generate_body_data(endpoint['request_body'], test_type)
        
        # Generate query parameters
        if endpoint.get('parameters'):
            test_data['query_params'] = TestGenerator._generate_query_params(endpoint['parameters'], test_type)
        
        return test_data
    
    @staticmethod
    def _generate_body_data(request_body: Dict[str, Any], test_type: str) -> Dict[str, Any]:
        """Generate request body data"""
        body_data = {}
        
        if 'content' in request_body:
            for content_type, content_spec in request_body['content'].items():
                if content_type == 'application/json' and 'schema' in content_spec:
                    schema = content_spec['schema']
                    body_data = TestGenerator._generate_from_schema(schema, test_type)
        
        return body_data
    
    @staticmethod
    def _generate_query_params(parameters: List[Dict[str, Any]], test_type: str) -> Dict[str, Any]:
        """Generate query parameters"""
        query_params = {}
        
        for param in parameters:
            if param.get('in') == 'query':
                param_name = param['name']
                param_schema = param.get('schema', {})
                query_params[param_name] = TestGenerator._generate_value_from_schema(param_schema, test_type)
        
        return query_params
    
    @staticmethod
    def _generate_from_schema(schema: Dict[str, Any], test_type: str) -> Dict[str, Any]:
        """Generate data from JSON schema"""
        if schema.get('type') == 'object':
            result = {}
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for prop_name, prop_schema in properties.items():
                if test_type == "edge_case" and prop_name in required:
                    # For edge cases, sometimes omit required fields
                    if random.random() < 0.3:
                        continue
                
                result[prop_name] = TestGenerator._generate_value_from_schema(prop_schema, test_type)
            
            return result
        else:
            return TestGenerator._generate_value_from_schema(schema, test_type)
    
    @staticmethod
    def _generate_value_from_schema(schema: Dict[str, Any], test_type: str) -> Any:
        """Generate a single value from schema"""
        schema_type = schema.get('type', 'string')
        
        if test_type == "edge_case":
            return TestGenerator._generate_edge_case_value(schema_type, schema)
        else:
            return TestGenerator._generate_normal_value(schema_type, schema)
    
    @staticmethod
    def _generate_normal_value(schema_type: str, schema: Dict[str, Any]) -> Any:
        """Generate normal test value"""
        if schema_type == 'string':
            if 'enum' in schema:
                return random.choice(schema['enum'])
            elif 'format' in schema:
                if schema['format'] == 'email':
                    return f"test{random.randint(1000, 9999)}@example.com"
                elif schema['format'] == 'date':
                    return datetime.now().strftime('%Y-%m-%d')
                elif schema['format'] == 'datetime':
                    return datetime.now().isoformat()
            else:
                return f"test_string_{random.randint(1000, 9999)}"
        
        elif schema_type == 'integer':
            minimum = schema.get('minimum', 1)
            maximum = schema.get('maximum', 100)
            return random.randint(minimum, maximum)
        
        elif schema_type == 'number':
            minimum = schema.get('minimum', 1.0)
            maximum = schema.get('maximum', 100.0)
            return round(random.uniform(minimum, maximum), 2)
        
        elif schema_type == 'boolean':
            return random.choice([True, False])
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            min_items = schema.get('minItems', 1)
            max_items = schema.get('maxItems', 3)
            count = random.randint(min_items, max_items)
            
            return [TestGenerator._generate_value_from_schema(items_schema, "normal") for _ in range(count)]
        
        return None
    
    @staticmethod
    def _generate_edge_case_value(schema_type: str, schema: Dict[str, Any]) -> Any:
        """Generate edge case test value"""
        if schema_type == 'string':
            if 'enum' in schema:
                # Return invalid enum value
                return "invalid_enum_value"
            elif 'format' in schema:
                if schema['format'] == 'email':
                    return "invalid-email-format"
                elif schema['format'] == 'date':
                    return "2023-13-45"  # Invalid date
                elif schema['format'] == 'datetime':
                    return "invalid-datetime"
            else:
                # Generate very long string or special characters
                if random.random() < 0.5:
                    return "x" * 10000  # Very long string
                else:
                    return "!@#$%^&*()_+-=[]{}|;':\",./<>?"  # Special characters
        
        elif schema_type == 'integer':
            # Return negative value or very large number
            if random.random() < 0.5:
                return -999999
            else:
                return 999999999
        
        elif schema_type == 'number':
            # Return very large or very small numbers instead of infinity/NaN
            if random.random() < 0.5:
                return 1e308  # Very large number
            else:
                return -1e308  # Very small number
        
        elif schema_type == 'boolean':
            return "not_boolean"  # Invalid boolean
        
        elif schema_type == 'array':
            # Return empty array or very large array
            if random.random() < 0.5:
                return []
            else:
                return [None] * 1000
        
        return None
    
    @staticmethod
    def generate_test_cases(endpoint: Dict[str, Any], base_url: str = "", api_spec: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Generate multiple test cases for an endpoint with RAG support"""
        
        # Try RAG generation first if API spec is provided
        if api_spec is not None:
            try:
                from app.core.ai_config import get_rag_generator
                
                # Get the appropriate RAG generator based on configuration
                rag_generator = get_rag_generator()
                
                if rag_generator:
                    rag_test_cases = rag_generator.generate_rag_test_cases(endpoint, api_spec, base_url)
                    
                    # If RAG generation succeeded and returned test cases, use them
                    if rag_test_cases and len(rag_test_cases) > 0:
                        return rag_test_cases
                    
            except Exception as e:
                # If RAG fails, fall back to rule-based generation
                print(f"RAG generation failed, falling back to rule-based: {str(e)}")
        
        # Fallback to original rule-based generation
        return TestGenerator._generate_rule_based_test_cases(endpoint, base_url)
    
    @staticmethod
    def _generate_rule_based_test_cases(endpoint: Dict[str, Any], base_url: str = "") -> List[Dict[str, Any]]:
        """Original rule-based test case generation (max 5 test cases)"""
        test_cases = []
        
        # Normal test case
        normal_data = TestGenerator.generate_test_data(endpoint, "normal")
        normal_curl = TestGenerator.generate_curl_command(endpoint, base_url, normal_data)
        
        test_cases.append({
            'name': f"Normal {endpoint['method']} {endpoint['path']}",
            'description': f"Test normal operation of {endpoint['method']} {endpoint['path']}",
            'test_type': TestCaseType.AUTOMATED,
            'priority': TestCasePriority.MEDIUM,
            'input_data': normal_data,
            'expected_status_code': 200,
            'curl_command': normal_curl
        })
        
        # Edge case test cases
        edge_data = TestGenerator.generate_test_data(endpoint, "edge_case")
        edge_curl = TestGenerator.generate_curl_command(endpoint, base_url, edge_data)
        
        test_cases.append({
            'name': f"Edge Case {endpoint['method']} {endpoint['path']}",
            'description': f"Test edge cases for {endpoint['method']} {endpoint['path']}",
            'test_type': TestCaseType.AUTOMATED,
            'priority': TestCasePriority.HIGH,
            'input_data': edge_data,
            'expected_status_code': 400,
            'curl_command': edge_curl
        })
        
        # Missing required fields test case
        if endpoint.get('request_body') or endpoint.get('parameters'):
            missing_data = TestGenerator.generate_test_data(endpoint, "missing_required")
            missing_curl = TestGenerator.generate_curl_command(endpoint, base_url, missing_data)
            
            test_cases.append({
                'name': f"Missing Required Fields {endpoint['method']} {endpoint['path']}",
                'description': f"Test missing required fields for {endpoint['method']} {endpoint['path']}",
                'test_type': TestCaseType.AUTOMATED,
                'priority': TestCasePriority.HIGH,
                'input_data': missing_data,
                'expected_status_code': 400,
                'curl_command': missing_curl
            })
        
        # Security test case
        security_data = TestGenerator.generate_test_data(endpoint, "security")
        security_curl = TestGenerator.generate_curl_command(endpoint, base_url, security_data)
        
        test_cases.append({
            'name': f"Security Test {endpoint['method']} {endpoint['path']}",
            'description': f"Test security vulnerabilities for {endpoint['method']} {endpoint['path']}",
            'test_type': TestCaseType.AUTOMATED,
            'priority': TestCasePriority.CRITICAL,
            'input_data': security_data,
            'expected_status_code': 400,
            'curl_command': security_curl
        })
        
        # Performance test case
        performance_data = TestGenerator.generate_test_data(endpoint, "performance")
        performance_curl = TestGenerator.generate_curl_command(endpoint, base_url, performance_data)
        
        test_cases.append({
            'name': f"Performance Test {endpoint['method']} {endpoint['path']}",
            'description': f"Test performance aspects for {endpoint['method']} {endpoint['path']}",
            'test_type': TestCaseType.AUTOMATED,
            'priority': TestCasePriority.MEDIUM,
            'input_data': performance_data,
            'expected_status_code': 200,
            'curl_command': performance_curl
        })
        
        # Limit to 5 test cases
        return test_cases[:5] 

    @staticmethod
    def generate_test_cases_for_all_endpoints(endpoints: List[Dict[str, Any]], base_url: str = "", api_spec: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Generate test cases for all endpoints in a single RAG request to avoid rate limiting"""
        from app.core.ai_config import get_rag_generator
        
        # Try to get RAG generator
        rag_generator = get_rag_generator()
        
        if rag_generator and hasattr(rag_generator, 'generate_rag_test_cases_for_all_endpoints'):
            # Use RAG generator for bulk generation
            return rag_generator.generate_rag_test_cases_for_all_endpoints(endpoints, api_spec, base_url)
        else:
            # Fallback to rule-based generation for each endpoint
            result = {}
            for endpoint in endpoints:
                endpoint_key = f"{endpoint['method']}_{endpoint['path']}"
                result[endpoint_key] = TestGenerator._generate_rule_based_test_cases(endpoint, base_url)
            return result 