import json
import random
import string
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import openai
from app.models.test_case import TestCaseType, TestCasePriority
from app.core.config import settings
from app.core.ai_config import ai_config
import logging

logger = logging.getLogger(__name__)

class RAGTestGenerator:
    """RAG-based test generator using OpenAI and OpenAPI context"""
    
    def __init__(self):
        self.openai_client = None
        self.is_available = False
        if hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                # Test the API key with a simple request
                self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                self.is_available = True
                logger.info("OpenAI API is available and working")
            except Exception as e:
                logger.warning(f"OpenAI API not available: {str(e)}")
                self.is_available = False
    
    def generate_rag_test_cases(self, endpoint: Dict[str, Any], api_spec: Dict[str, Any], base_url: str = "") -> List[Dict[str, Any]]:
        """Generate test cases using RAG approach with OpenAPI context"""
        if not self.is_available:
            logger.warning("OpenAI API not available, falling back to rule-based generation")
            return self._fallback_generation(endpoint, base_url)
        
        try:
            # Create context from OpenAPI spec
            context = self._create_api_context(endpoint, api_spec)
            
            # Generate test cases using RAG
            test_cases = []
            
            # Normal test case with RAG
            normal_case = self._generate_rag_test_case(endpoint, context, "normal", base_url)
            if normal_case:
                test_cases.append(normal_case)
            
            # Edge case with RAG
            edge_case = self._generate_rag_test_case(endpoint, context, "edge_case", base_url)
            if edge_case:
                test_cases.append(edge_case)
            
            # Security test case with RAG
            security_case = self._generate_rag_test_case(endpoint, context, "security", base_url)
            if security_case:
                test_cases.append(security_case)
            
            # Business logic test case with RAG
            business_case = self._generate_rag_test_case(endpoint, context, "business_logic", base_url)
            if business_case:
                test_cases.append(business_case)
            
            return test_cases
            
        except Exception as e:
            logger.error(f"RAG generation failed: {str(e)}, falling back to rule-based")
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
    
    def _generate_rag_test_case(self, endpoint: Dict[str, Any], context: str, test_type: str, base_url: str) -> Optional[Dict[str, Any]]:
        """Generate a single test case using RAG"""
        
        # Create prompt based on test type
        if test_type == "normal":
            prompt = self._create_normal_test_prompt(endpoint, context)
        elif test_type == "edge_case":
            prompt = self._create_edge_case_prompt(endpoint, context)
        elif test_type == "security":
            prompt = self._create_security_test_prompt(endpoint, context)
        elif test_type == "business_logic":
            prompt = self._create_business_logic_prompt(endpoint, context)
        else:
            return None
        
        try:
            response = self.openai_client.chat.completions.create(
                model=ai_config.OPENAI_MODEL,
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
                temperature=ai_config.OPENAI_TEMPERATURE,
                max_tokens=ai_config.OPENAI_MAX_TOKENS,
                timeout=ai_config.OPENAI_TIMEOUT
            )
            
            # Parse the response
            content = response.choices[0].message.content
            test_data = json.loads(content)
            
            # Generate CURL command
            curl_command = self._generate_curl_command(endpoint, base_url, test_data.get('input_data', {}))
            
            return {
                'name': test_data.get('name', f"{test_type.title()} {endpoint['method']} {endpoint['path']}"),
                'description': test_data.get('description', f"AI-generated {test_type} test for {endpoint['method']} {endpoint['path']}"),
                'test_type': TestCaseType.AI_GENERATED,
                'priority': self._map_priority(test_data.get('priority', 'medium')),
                'input_data': test_data.get('input_data', {}),
                'expected_status_code': test_data.get('expected_status_code', 200),
                'curl_command': curl_command,
                'test_script': test_data.get('test_script', '')
            }
            
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            return None
        except openai.QuotaExceededError as e:
            logger.error(f"OpenAI quota exceeded: {str(e)}")
            return None
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI authentication failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Failed to generate {test_type} test case: {str(e)}")
            return None
    
    def _create_normal_test_prompt(self, endpoint: Dict[str, Any], context: str) -> str:
        """Create prompt for normal test case generation"""
        return f"""
Based on the following OpenAPI specification context, generate a realistic NORMAL test case for this endpoint.

Context:
{context}

Generate a JSON response with the following structure:
{{
    "name": "Descriptive test name",
    "description": "What this test validates",
    "priority": "low|medium|high|critical",
    "input_data": {{
        "body": {{ /* realistic request body data */ }},
        "query_params": {{ /* realistic query parameters */ }},
        "headers": {{ /* realistic headers */ }}
    }},
    "expected_status_code": 200,
    "test_script": "Optional test script description"
}}

Focus on:
- Realistic, valid data that would be used in production
- Proper data types and formats
- Business logic that makes sense for this endpoint
- Expected successful responses
"""
    
    def _create_edge_case_prompt(self, endpoint: Dict[str, Any], context: str) -> str:
        """Create prompt for edge case test generation"""
        return f"""
Based on the following OpenAPI specification context, generate a realistic EDGE CASE test for this endpoint.

Context:
{context}

Generate a JSON response with the following structure:
{{
    "name": "Descriptive edge case test name",
    "description": "What edge case this test validates",
    "priority": "high|critical",
    "input_data": {{
        "body": {{ /* edge case request body data */ }},
        "query_params": {{ /* edge case query parameters */ }},
        "headers": {{ /* edge case headers */ }}
    }},
    "expected_status_code": 400,
    "test_script": "Optional test script description"
}}

Focus on:
- Boundary values (min/max limits)
- Invalid data types or formats
- Missing required fields
- Extreme values that might cause issues
- Data that tests validation logic
"""
    
    def _create_security_test_prompt(self, endpoint: Dict[str, Any], context: str) -> str:
        """Create prompt for security test generation"""
        return f"""
Based on the following OpenAPI specification context, generate a SECURITY test case for this endpoint.

Context:
{context}

Generate a JSON response with the following structure:
{{
    "name": "Descriptive security test name",
    "description": "What security vulnerability this test validates",
    "priority": "critical",
    "input_data": {{
        "body": {{ /* security test request body data */ }},
        "query_params": {{ /* security test query parameters */ }},
        "headers": {{ /* security test headers */ }}
    }},
    "expected_status_code": 400,
    "test_script": "Optional test script description"
}}

Focus on:
- SQL injection attempts
- XSS payloads
- Authentication bypass attempts
- Authorization testing
- Input validation bypass
- Rate limiting tests
- Sensitive data exposure
"""
    
    def _create_business_logic_prompt(self, endpoint: Dict[str, Any], context: str) -> str:
        """Create prompt for business logic test generation"""
        return f"""
Based on the following OpenAPI specification context, generate a BUSINESS LOGIC test case for this endpoint.

Context:
{context}

Generate a JSON response with the following structure:
{{
    "name": "Descriptive business logic test name",
    "description": "What business rule this test validates",
    "priority": "high",
    "input_data": {{
        "body": {{ /* business logic test request body data */ }},
        "query_params": {{ /* business logic test query parameters */ }},
        "headers": {{ /* business logic test headers */ }}
    }},
    "expected_status_code": 200,
    "test_script": "Optional test script description"
}}

Focus on:
- Business rule validation
- Workflow testing
- State transitions
- Data consistency
- Business constraints
- Domain-specific logic
- Real-world scenarios
"""
    
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
        """Fallback to rule-based generation when AI is not available"""
        from app.services.test_generator import TestGenerator
        return TestGenerator._generate_rule_based_test_cases(endpoint, base_url) 