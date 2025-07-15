import json
import requests
from typing import Dict, List, Any, Optional
from app.models.test_case import TestCaseType, TestCasePriority
from app.core.ai_config import ai_config
import logging

logger = logging.getLogger(__name__)

class GeminiRAGTestGenerator:
    """RAG test generator using Google Gemini 2.0 Flash API"""
    
    def __init__(self):
        self.gemini_client = None
        self.is_available = False
        
        if ai_config.GEMINI_API_KEY:
            try:
                # Test the API key with a simple request
                test_response = requests.post(
                    f"{ai_config.GEMINI_BASE_URL}/models/{ai_config.GEMINI_MODEL}:generateContent",
                    headers={
                        "x-goog-api-key": ai_config.GEMINI_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "contents": [{
                            "parts": [{"text": "Hello"}]
                        }],
                        "generationConfig": {
                            "maxOutputTokens": 5
                        }
                    },
                    timeout=ai_config.GEMINI_TIMEOUT
                )
                
                if test_response.status_code == 200:
                    self.is_available = True
                    logger.info("Gemini 2.0 Flash API is available and working")
                else:
                    logger.warning(f"Gemini API test failed: {test_response.status_code}")
                    self.is_available = False
                    
            except Exception as e:
                logger.warning(f"Gemini API not available: {str(e)}")
                self.is_available = False
        else:
            logger.warning("Gemini API key not configured")
    
    def generate_rag_test_cases(self, endpoint: Dict[str, Any], api_spec: Dict[str, Any], base_url: str = "") -> List[Dict[str, Any]]:
        """Generate test cases using RAG approach with Gemini 2.0 Flash (max 5 test cases)"""
        if not self.is_available:
            logger.warning("Gemini API not available, falling back to rule-based generation")
            return self._fallback_generation(endpoint, base_url)
        
        # Create context from OpenAPI spec
        context = self._create_api_context(endpoint, api_spec)
        
        # Generate all test cases in a single request to avoid rate limiting
        test_cases = self._generate_all_test_cases_single_request(endpoint, context, base_url)
        
        return test_cases[:5]  # Ensure max 5 test cases
    
    def generate_rag_test_cases_for_all_endpoints(self, endpoints: List[Dict[str, Any]], api_spec: Dict[str, Any], base_url: str = "") -> Dict[str, List[Dict[str, Any]]]:
        """Generate test cases for all endpoints in a single Gemini request to avoid rate limiting"""
        if not self.is_available:
            logger.warning("Gemini API not available, falling back to rule-based generation")
            return self._fallback_generation_for_all_endpoints(endpoints, base_url)
        
        # Create context from OpenAPI spec
        context = self._create_api_context_for_all_endpoints(endpoints, api_spec)
        
        # Generate all test cases in a single request
        all_test_cases = self._generate_all_endpoints_test_cases_single_request(endpoints, context, base_url)
        
        return all_test_cases
    
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
    
    def _create_api_context_for_all_endpoints(self, endpoints: List[Dict[str, Any]], api_spec: Dict[str, Any]) -> str:
        """Create context string from OpenAPI specification for all endpoints"""
        context_parts = []
        
        # API Info
        info = api_spec.get('info', {})
        context_parts.append(f"API: {info.get('title', 'Unknown API')}")
        context_parts.append(f"Version: {info.get('version', 'Unknown')}")
        context_parts.append(f"Description: {info.get('description', 'No description')}")
        
        # All endpoints details
        context_parts.append(f"\nEndpoints to generate test cases for:")
        for i, endpoint in enumerate(endpoints, 1):
            context_parts.append(f"\n{i}. {endpoint['method']} {endpoint['path']}")
            context_parts.append(f"   Summary: {endpoint.get('summary', 'No summary')}")
            context_parts.append(f"   Description: {endpoint.get('description', 'No description')}")
            
            # Parameters
            if endpoint.get('parameters'):
                context_parts.append("   Parameters:")
                for param in endpoint['parameters']:
                    param_info = f"     - {param.get('name')} ({param.get('in', 'unknown')}): {param.get('type', 'unknown')}"
                    if param.get('required'):
                        param_info += " [REQUIRED]"
                    context_parts.append(param_info)
            
            # Request body schema
            if endpoint.get('request_body'):
                context_parts.append("   Request Body Schema:")
                schema = self._extract_schema_from_request_body(endpoint['request_body'])
                if schema:
                    context_parts.append(f"     {json.dumps(schema, indent=6)}")
            
            # Response schemas
            if endpoint.get('responses'):
                context_parts.append("   Response Schemas:")
                for status_code, response in endpoint['responses'].items():
                    context_parts.append(f"     {status_code}: {response.get('description', 'No description')}")
            
            # Tags
            if endpoint.get('tags'):
                context_parts.append(f"   Tags: {', '.join(endpoint['tags'])}")
        
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
    
    def _generate_all_test_cases_single_request(self, endpoint: Dict[str, Any], context: str, base_url: str) -> List[Dict[str, Any]]:
        """Generate all test cases in a single Gemini request to avoid rate limiting"""
        
        prompt = f"""Based on this API specification context:

{context}

Generate exactly 5 test cases for this endpoint in the following categories:
1. Normal test case - realistic business scenarios with valid data
2. Edge case test - boundary conditions, invalid inputs, edge scenarios  
3. Security test - security vulnerabilities like SQL injection, XSS, authentication bypass
4. Business logic test - business rules and validation scenarios
5. Performance test - load testing and performance scenarios

IMPORTANT RULES:
- Return ONLY a valid JSON array with exactly 5 test case objects
- Use ONLY valid JSON values (strings, numbers, booleans, objects, arrays)
- DO NOT use Python expressions like "A" * 8192 - use actual string values instead
- DO NOT use any programming language syntax in JSON values
- All string values must be properly quoted
- No additional text or explanations outside the JSON

[
    {{
        "name": "Normal test name",
        "description": "What this normal test validates",
        "priority": "medium",
        "input_data": {{
            "body": {{}},
            "query_params": {{}},
            "headers": {{}}
        }},
        "expected_status_code": 200,
        "test_script": "Brief description of normal test logic"
    }},
    {{
        "name": "Edge case test name", 
        "description": "What edge case this test validates",
        "priority": "high",
        "input_data": {{
            "body": {{}},
            "query_params": {{}},
            "headers": {{}}
        }},
        "expected_status_code": 400,
        "test_script": "Brief description of edge case test logic"
    }},
    {{
        "name": "Security test name",
        "description": "What security vulnerability this test validates", 
        "priority": "critical",
        "input_data": {{
            "body": {{}},
            "query_params": {{}},
            "headers": {{}}
        }},
        "expected_status_code": 400,
        "test_script": "Brief description of security test logic"
    }},
    {{
        "name": "Business logic test name",
        "description": "What business rule this test validates",
        "priority": "high", 
        "input_data": {{
            "body": {{}},
            "query_params": {{}},
            "headers": {{}}
        }},
        "expected_status_code": 200,
        "test_script": "Brief description of business logic test"
    }},
    {{
        "name": "Performance test name",
        "description": "What performance aspect this test validates",
        "priority": "medium",
        "input_data": {{
            "body": {{}},
            "query_params": {{}},
            "headers": {{}}
        }},
        "expected_status_code": 200,
        "test_script": "Brief description of performance test"
    }}
]"""
        
        try:
            response = requests.post(
                f"{ai_config.GEMINI_BASE_URL}/models/{ai_config.GEMINI_MODEL}:generateContent",
                headers={
                    "x-goog-api-key": ai_config.GEMINI_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": ai_config.GEMINI_TEMPERATURE,
                        "maxOutputTokens": ai_config.GEMINI_MAX_TOKENS * 2,  # Increase tokens for multiple test cases
                        "topP": 0.95,
                        "topK": 64
                    }
                },
                timeout=ai_config.GEMINI_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API request failed: {response.status_code} - {response.text}")
                return self._fallback_generation(endpoint, base_url)
            
            # Parse the response
            response_data = response.json()
            content = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # Debug: Log the actual response content
            logger.info(f"Gemini response content: {content}")
            
            # Try to extract JSON from the response using improved parsing
            test_cases_data = self._parse_gemini_json_response(content)
            if test_cases_data is None:
                return self._fallback_generation(endpoint, base_url)
            
            # Convert to test case objects
            test_cases = []
            for test_data in test_cases_data:
                if isinstance(test_data, dict):
                    # Generate CURL command
                    curl_command = self._generate_curl_command(endpoint, base_url, test_data.get('input_data', {}))
                    
                    test_case = {
                        'name': test_data.get('name', f"AI Generated {endpoint['method']} {endpoint['path']}"),
                        'description': test_data.get('description', f"Gemini 2.0 Flash AI-generated test for {endpoint['method']} {endpoint['path']}"),
                        'test_type': TestCaseType.AI_GENERATED,
                        'priority': self._map_priority(test_data.get('priority', 'medium')),
                        'input_data': test_data.get('input_data', {}),
                        'expected_status_code': test_data.get('expected_status_code', 200),
                        'curl_command': curl_command,
                        'test_script': test_data.get('test_script', '')
                    }
                    test_cases.append(test_case)
            
            logger.info(f"Successfully generated {len(test_cases)} test cases with Gemini 2.0 Flash")
            return test_cases
            
        except requests.exceptions.Timeout:
            logger.error("Gemini API timeout for test case generation")
            return self._fallback_generation(endpoint, base_url)
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            return self._fallback_generation(endpoint, base_url)
        except Exception as e:
            logger.error(f"Failed to generate test cases with Gemini: {str(e)}")
            return self._fallback_generation(endpoint, base_url)
    
    def _generate_all_endpoints_test_cases_single_request(self, endpoints: List[Dict[str, Any]], context: str, base_url: str) -> Dict[str, List[Dict[str, Any]]]:
        """Generate test cases for all endpoints in a single Gemini request"""
        
        prompt = f"""Based on this API specification context:

{context}

Generate exactly 3 test cases for each endpoint in the following categories:
1. Normal test case - realistic business scenarios with valid data
2. Edge case test - boundary conditions, invalid inputs, edge scenarios  
3. Security test - security vulnerabilities like SQL injection, XSS, authentication bypass

IMPORTANT RULES:
- Return ONLY a valid JSON object with endpoint keys and test case arrays
- Use ONLY valid JSON values (strings, numbers, booleans, objects, arrays)
- DO NOT use Python expressions like "A" * 8192 - use actual string values instead
- DO NOT use any programming language syntax in JSON values
- All string values must be properly quoted
- No additional text or explanations outside the JSON

{{
    "GET_/": [
        {{
            "name": "Normal test name",
            "description": "What this normal test validates",
            "priority": "medium",
            "input_data": {{
                "body": {{}},
                "query_params": {{}},
                "headers": {{}}
            }},
            "expected_status_code": 200,
            "test_script": "Brief description of normal test logic"
        }},
        {{
            "name": "Edge case test name",
            "description": "What edge case this test validates",
            "priority": "high",
            "input_data": {{
                "body": {{}},
                "query_params": {{}},
                "headers": {{}}
            }},
            "expected_status_code": 400,
            "test_script": "Brief description of edge case test logic"
        }},
        {{
            "name": "Security test name",
            "description": "What security vulnerability this test validates",
            "priority": "critical",
            "input_data": {{
                "body": {{}},
                "query_params": {{}},
                "headers": {{}}
            }},
            "expected_status_code": 400,
            "test_script": "Brief description of security test logic"
        }}
    ]
}}"""
        
        try:
            response = requests.post(
                f"{ai_config.GEMINI_BASE_URL}/models/{ai_config.GEMINI_MODEL}:generateContent",
                headers={
                    "x-goog-api-key": ai_config.GEMINI_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": ai_config.GEMINI_TEMPERATURE,
                        "maxOutputTokens": ai_config.GEMINI_MAX_TOKENS * 3,  # Increase tokens for multiple endpoints
                        "topP": 0.95,
                        "topK": 64
                    }
                },
                timeout=ai_config.GEMINI_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API request failed: {response.status_code} - {response.text}")
                return self._fallback_generation_for_all_endpoints(endpoints, base_url)
            
            # Parse the response
            response_data = response.json()
            content = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # Debug: Log the actual response content
            logger.info(f"Gemini bulk response content: {content}")
            
            # Try to extract JSON from the response
            try:
                # First try direct JSON parsing
                all_test_cases_data = json.loads(content)
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the text
                import re
                
                # Remove markdown code blocks if present
                content_clean = content.strip()
                if content_clean.startswith('```json'):
                    content_clean = content_clean[7:]  # Remove ```json
                if content_clean.startswith('```'):
                    content_clean = content_clean[3:]  # Remove ```
                if content_clean.endswith('```'):
                    content_clean = content_clean[:-3]  # Remove trailing ```
                
                content_clean = content_clean.strip()
                
                try:
                    # Try parsing the cleaned content
                    all_test_cases_data = json.loads(content_clean)
                except json.JSONDecodeError:
                    # If still fails, try to extract JSON object from the text
                    json_match = re.search(r'\{.*\}', content_clean, re.DOTALL)
                    if json_match:
                        try:
                            all_test_cases_data = json.loads(json_match.group())
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse JSON from cleaned Gemini bulk response: {content_clean}")
                            return self._fallback_generation_for_all_endpoints(endpoints, base_url)
                    else:
                        logger.error(f"No JSON object found in cleaned Gemini bulk response: {content_clean}")
                        return self._fallback_generation_for_all_endpoints(endpoints, base_url)
            
            # Convert to test case objects for each endpoint
            result = {}
            for endpoint in endpoints:
                endpoint_key = f"{endpoint['method']}_{endpoint['path']}"
                endpoint_test_cases = all_test_cases_data.get(endpoint_key, [])
                
                test_cases = []
                for test_data in endpoint_test_cases:
                    if isinstance(test_data, dict):
                        # Generate CURL command
                        curl_command = self._generate_curl_command(endpoint, base_url, test_data.get('input_data', {}))
                        
                        test_case = {
                            'name': test_data.get('name', f"AI Generated {endpoint['method']} {endpoint['path']}"),
                            'description': test_data.get('description', f"Gemini 2.0 Flash AI-generated test for {endpoint['method']} {endpoint['path']}"),
                            'test_type': TestCaseType.AI_GENERATED,
                            'priority': self._map_priority(test_data.get('priority', 'medium')),
                            'input_data': test_data.get('input_data', {}),
                            'expected_status_code': test_data.get('expected_status_code', 200),
                            'curl_command': curl_command,
                            'test_script': test_data.get('test_script', '')
                        }
                        test_cases.append(test_case)
                
                result[endpoint_key] = test_cases
            
            logger.info(f"Successfully generated test cases for {len(result)} endpoints with Gemini 2.0 Flash")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Gemini API timeout for bulk test case generation")
            return self._fallback_generation_for_all_endpoints(endpoints, base_url)
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            return self._fallback_generation_for_all_endpoints(endpoints, base_url)
        except Exception as e:
            logger.error(f"Failed to generate bulk test cases with Gemini: {str(e)}")
            return self._fallback_generation_for_all_endpoints(endpoints, base_url)
    
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
        """Fallback to rule-based generation when Gemini is not available"""
        from app.services.test_generator import TestGenerator
        return TestGenerator._generate_rule_based_test_cases(endpoint, base_url) 
    
    def _fallback_generation_for_all_endpoints(self, endpoints: List[Dict[str, Any]], base_url: str) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback to rule-based generation for all endpoints when Gemini is not available"""
        from app.services.test_generator import TestGenerator
        result = {}
        for endpoint in endpoints:
            endpoint_key = f"{endpoint['method']}_{endpoint['path']}"
            result[endpoint_key] = TestGenerator._generate_rule_based_test_cases(endpoint, base_url)
        return result 

    def _fix_json_content(self, json_content: str) -> str:
        """Fix common JSON parsing issues in Gemini responses"""
        import re
        
        # Remove any trailing commas before closing brackets/braces
        json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
        
        # Fix Python expressions like "A" * 8192
        json_content = re.sub(r'"([^"]*)"\s*\*\s*(\d+)', r'"\1"', json_content)
        
        # Fix Python expressions like "A" * 8192 in different formats
        json_content = re.sub(r'"([^"]*)"\s*\*\s*(\d+)', lambda m: f'"{m.group(1) * int(m.group(2))}"', json_content)
        
        # Fix any remaining unescaped quotes at the end of strings
        json_content = re.sub(r'(?<!\\)"(?=\s*[,}\]])', r'\\"', json_content)
        
        # Fix any remaining unescaped quotes in the middle of strings
        json_content = re.sub(r'(?<!\\)"(?=.*")', r'\\"', json_content)
        
        # Fix any remaining unescaped quotes before colons
        json_content = re.sub(r'(?<!\\)"(?=.*":)', r'\\"', json_content)
        
        # Remove any null bytes or invalid characters
        json_content = json_content.replace('\x00', '')
        
        # Fix any remaining Python expressions
        json_content = re.sub(r'(\w+)\s*\*\s*(\d+)', lambda m: f'"{m.group(1) * int(m.group(2))}"', json_content)
        
        return json_content 

    def _parse_gemini_json_response(self, content: str) -> Optional[List[Dict[str, Any]]]:
        """Parse Gemini JSON response with improved error handling"""
        import re
        
        try:
            # First try direct JSON parsing
            test_cases_data = json.loads(content)
            logger.info("Successfully parsed JSON directly")
            return test_cases_data
        except json.JSONDecodeError as e:
            logger.warning(f"Direct JSON parsing failed: {str(e)}")
        
        # If that fails, try to extract JSON from the text
        # Remove markdown code blocks if present
        content_clean = content.strip()
        if content_clean.startswith('```json'):
            content_clean = content_clean[7:]  # Remove ```json
        if content_clean.startswith('```'):
            content_clean = content_clean[3:]  # Remove ```
        if content_clean.endswith('```'):
            content_clean = content_clean[:-3]  # Remove trailing ```
        
        content_clean = content_clean.strip()
        logger.info(f"Cleaned content: {content_clean[:200]}...")
        
        try:
            # Try parsing the cleaned content
            test_cases_data = json.loads(content_clean)
            logger.info("Successfully parsed cleaned JSON")
            return test_cases_data
        except json.JSONDecodeError as e:
            logger.warning(f"Cleaned JSON parsing failed: {str(e)}")
        
        # If still fails, try to extract JSON array from the text
        json_match = re.search(r'\[.*\]', content_clean, re.DOTALL)
        if json_match:
            try:
                test_cases_data = json.loads(json_match.group())
                logger.info("Successfully parsed extracted JSON array")
                return test_cases_data
            except json.JSONDecodeError as e:
                logger.warning(f"Extracted JSON parsing failed: {str(e)}")
                # Try to fix common JSON issues
                fixed_content = self._fix_json_content(json_match.group())
                try:
                    test_cases_data = json.loads(fixed_content)
                    logger.info("Successfully parsed fixed JSON")
                    return test_cases_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON after fixing: {str(e)}")
                    logger.error(f"Original content: {content}")
                    logger.error(f"Cleaned content: {content_clean}")
                    logger.error(f"Fixed content: {fixed_content}")
                    return None
        else:
            logger.error(f"No JSON array found in cleaned Gemini response: {content_clean}")
            return None 