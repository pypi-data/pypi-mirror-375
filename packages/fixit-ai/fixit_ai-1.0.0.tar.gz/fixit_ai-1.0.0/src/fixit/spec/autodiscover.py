"""HTTP autodiscovery for OpenAPI specs."""

from __future__ import annotations
import json
from typing import Any, Dict, Optional
import httpx
from ruamel.yaml import YAML


def try_fetch_known_spec(base_url: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """
    Try to fetch OpenAPI spec from common endpoints.
    
    Args:
        base_url: Base URL of the API server (e.g., 'http://localhost:8000')
        timeout: Request timeout in seconds
        
    Returns:
        OpenAPI spec dict if found, None otherwise
        
    Example:
        >>> spec = try_fetch_known_spec('http://localhost:8000')
        >>> if spec:
        ...     print(spec['info']['title'])
    """
    # Normalize base URL
    base_url = base_url.rstrip('/')
    
    # Common OpenAPI spec endpoints, in order of preference
    endpoints = [
        '/openapi.json',
        '/openapi.yaml', 
        '/swagger.json',
        '/v3/api-docs',
        '/api-docs',
        '/docs/openapi.json',
        '/api/openapi.json',
        '/api/v1/openapi.json'
    ]
    
    yaml_parser = YAML(typ='safe')
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        
        try:
            with httpx.Client(
                timeout=timeout,
                follow_redirects=True,
                headers={'Accept': 'application/json, application/yaml, text/yaml'}
            ) as client:
                response = client.get(url)
                
                if response.status_code != 200:
                    continue
                    
                content_type = response.headers.get('content-type', '').lower()
                text_content = response.text.strip()
                
                if not text_content:
                    continue
                
                # Try parsing as JSON first
                spec_dict = None
                try:
                    spec_dict = response.json()
                except (json.JSONDecodeError, ValueError):
                    # Try parsing as YAML
                    try:
                        spec_dict = yaml_parser.load(text_content)
                    except Exception:
                        continue
                
                if not isinstance(spec_dict, dict):
                    continue
                
                # Basic validation - must have paths
                if 'paths' not in spec_dict:
                    continue
                
                # Additional validation for minimal OpenAPI structure
                if not _is_valid_openapi_lite(spec_dict):
                    continue
                
                return spec_dict
                
        except (httpx.RequestError, httpx.HTTPError, Exception):
            # Continue trying other endpoints
            continue
    
    return None


def _is_valid_openapi_lite(spec: Dict[str, Any]) -> bool:
    """
    Validate minimal OpenAPI structure.
    
    Args:
        spec: Potential OpenAPI spec dictionary
        
    Returns:
        True if it looks like a valid OpenAPI spec
    """
    # Must have paths
    if not isinstance(spec.get('paths'), dict):
        return False
    
    # Check if it has some basic OpenAPI structure
    has_openapi_version = 'openapi' in spec or 'swagger' in spec
    has_info = isinstance(spec.get('info'), dict)
    
    # If it has openapi/swagger version, it should have info
    if has_openapi_version and not has_info:
        return False
    
    # Check that paths contain valid-looking HTTP methods
    valid_methods = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'}
    
    for path, path_spec in spec['paths'].items():
        if not isinstance(path_spec, dict):
            continue
            
        # At least one method should be a valid HTTP method
        methods = set(path_spec.keys()) & valid_methods
        if methods:
            return True
    
    return False
