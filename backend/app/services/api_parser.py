import yaml
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from app.core.config import settings

class APIParser:
    """Service to parse OpenAPI and Postman specifications"""
    
    @staticmethod
    def parse_openapi_spec(file_path: str) -> Dict[str, Any]:
        """Parse OpenAPI specification file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                content = yaml.safe_load(file)
            else:
                content = json.load(file)
        
        return content
    
    @staticmethod
    def parse_postman_collection(file_path: str) -> Dict[str, Any]:
        """Parse Postman collection file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = json.load(file)
        
        return content
    
    @staticmethod
    def extract_endpoints_from_openapi(spec_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoints from OpenAPI specification"""
        endpoints = []
        
        # Extract paths
        paths = spec_content.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    endpoint = {
                        'path': path,
                        'method': method.upper(),
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody', {}),
                        'responses': details.get('responses', {}),
                        'tags': details.get('tags', [])
                    }
                    endpoints.append(endpoint)
        
        return endpoints
    
    @staticmethod
    def extract_endpoints_from_postman(collection_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract endpoints from Postman collection"""
        endpoints = []
        
        def process_item(item: Dict[str, Any]):
            if 'request' in item:
                request = item['request']
                url = request.get('url', {})
                
                # Handle different URL formats
                if isinstance(url, str):
                    path = url
                elif isinstance(url, dict):
                    path = url.get('raw', '')
                    # Extract path from URL
                    if 'path' in url:
                        path = '/' + '/'.join(url['path'])
                
                endpoint = {
                    'path': path,
                    'method': request.get('method', 'GET').upper(),
                    'summary': item.get('name', ''),
                    'description': item.get('description', ''),
                    'parameters': request.get('url', {}).get('query', []),
                    'request_body': request.get('body', {}),
                    'responses': {},  # Postman doesn't include responses in collection
                    'tags': [item.get('name', '')]
                }
                endpoints.append(endpoint)
            
            # Process nested items
            if 'item' in item:
                for sub_item in item['item']:
                    process_item(sub_item)
        
        # Process collection items
        if 'item' in collection_content:
            for item in collection_content['item']:
                process_item(item)
        
        return endpoints
    
    @staticmethod
    def get_base_url_from_openapi(spec_content: Dict[str, Any]) -> str:
        """Extract base URL from OpenAPI specification"""
        servers = spec_content.get('servers', [])
        return servers[0].get('url', '') if servers else ''
    
    @staticmethod
    def validate_spec_file(file_path: str) -> Dict[str, Any]:
        """Validate and determine specification type"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension in ['.yaml', '.yml', '.json']:
                # Try to parse as OpenAPI
                content = APIParser.parse_openapi_spec(file_path)
                
                # Check if it's OpenAPI spec
                if 'openapi' in content or 'swagger' in content:
                    return {
                        'type': 'openapi',
                        'content': content,
                        'version': content.get('openapi') or content.get('swagger')
                    }
                else:
                    # Try as Postman collection
                    if 'info' in content and 'item' in content:
                        return {
                            'type': 'postman',
                            'content': content,
                            'version': content.get('info', {}).get('schema')
                        }
            
            raise ValueError(f"Unsupported file format: {file_extension}")
            
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}") 