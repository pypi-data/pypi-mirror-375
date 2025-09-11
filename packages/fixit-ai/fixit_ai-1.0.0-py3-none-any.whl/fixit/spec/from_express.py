"""Express.js introspection for OpenAPI spec generation."""

from __future__ import annotations
import ast
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import json


def extract_express_routes(project_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract routes from an Express.js application and generate OpenAPI spec.
    
    Args:
        project_path: Path to Express.js project root
        
    Returns:
        OpenAPI spec dict if successful, None otherwise
        
    Example:
        >>> spec = extract_express_routes('./my-express-app')
        >>> if spec:
        ...     print(spec['paths'])
    """
    project_path = Path(project_path).resolve()
    
    # Find the main entry point
    main_file = _find_express_main(project_path)
    if not main_file:
        return None
    
    # Parse the main file and dependencies
    routes = _parse_express_routes(main_file, project_path)
    if not routes:
        return None
    
    # Convert routes to OpenAPI spec
    openapi_spec = _routes_to_openapi(routes, project_path)
    return openapi_spec


def _find_express_main(project_path: Path) -> Optional[Path]:
    """Find the main Express.js entry point."""
    
    # Check package.json for main entry
    package_json = project_path / 'package.json'
    if package_json.exists():
        try:
            with open(package_json, encoding='utf-8') as f:
                pkg_data = json.load(f)
            
            # Check scripts.start or main field
            main_script = None
            
            # Priority 1: scripts.start
            scripts = pkg_data.get('scripts', {})
            start_cmd = scripts.get('start', '')
            if start_cmd:
                # Extract file from "node server.js" or "npm start"
                match = re.search(r'node\s+([^\s]+\.js)', start_cmd)
                if match:
                    main_script = match.group(1)
            
            # Priority 2: main field
            if not main_script:
                main_script = pkg_data.get('main', '')
            
            if main_script:
                main_file = project_path / main_script
                if main_file.exists():
                    return main_file
                    
        except (json.JSONDecodeError, OSError):
            pass
    
    # Common fallback entry points
    candidates = [
        'app.js', 'server.js', 'index.js', 'main.js',
        'src/app.js', 'src/server.js', 'src/index.js',
        'server/app.js', 'server/index.js'
    ]
    
    for candidate in candidates:
        main_file = project_path / candidate
        if main_file.exists():
            # Check if it looks like an Express app
            if _file_looks_like_express(main_file):
                return main_file
    
    return None


def _file_looks_like_express(file_path: Path) -> bool:
    """Check if a JS file imports/uses Express."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        # Look for Express patterns
        express_patterns = [
            r'require\([\'"]express[\'"]\)',
            r'import\s+.*\s+from\s+[\'"]express[\'"]',
            r'\.use\s*\(',
            r'\.get\s*\(',
            r'\.post\s*\(',
            r'\.listen\s*\('
        ]
        
        for pattern in express_patterns:
            if re.search(pattern, content):
                return True
        
        return False
        
    except (OSError, UnicodeDecodeError):
        return False


def _parse_express_routes(main_file: Path, project_path: Path) -> List[Dict[str, Any]]:
    """Parse Express.js routes from the main file and imports."""
    
    routes = []
    
    try:
        with open(main_file, encoding='utf-8') as f:
            content = f.read()
        
        # Extract direct routes from the main file
        routes.extend(_extract_routes_from_content(content))
        
        # Look for router imports and parse those files
        router_files = _find_router_imports(content, main_file.parent)
        for router_file in router_files:
            try:
                with open(router_file, encoding='utf-8') as f:
                    router_content = f.read()
                routes.extend(_extract_routes_from_content(router_content))
            except (OSError, UnicodeDecodeError):
                continue
        
        return routes
        
    except (OSError, UnicodeDecodeError):
        return []


def _extract_routes_from_content(content: str) -> List[Dict[str, Any]]:
    """Extract route definitions from JavaScript content."""
    
    routes = []
    
    # Patterns for different route definition styles
    patterns = [
        # app.get('/path', handler)
        r'(?:app|router)\.(get|post|put|patch|delete|options|head)\s*\(\s*[\'"]([^\'"]+)[\'"]',
        # router.route('/path').get(handler).post(handler)
        r'(?:app|router)\.route\s*\(\s*[\'"]([^\'"]+)[\'"]\)\s*\.(\w+)\s*\(',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            if len(match.groups()) == 2:
                method, path = match.groups()
                routes.append({
                    'method': method.upper(),
                    'path': path,
                    'summary': f'{method.upper()} {path}',
                    'description': f'Auto-generated from Express route: {method.upper()} {path}'
                })
    
    # Handle chained route methods
    route_chains = re.finditer(
        r'(?:app|router)\.route\s*\(\s*[\'"]([^\'"]+)[\'"]\)((?:\.\w+\s*\([^)]*\))+)',
        content,
        re.MULTILINE
    )
    
    for match in route_chains:
        path = match.group(1)
        chain = match.group(2)
        
        # Extract chained methods
        method_matches = re.finditer(r'\.(\w+)\s*\(', chain)
        for method_match in method_matches:
            method = method_match.group(1).upper()
            if method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD']:
                routes.append({
                    'method': method,
                    'path': path,
                    'summary': f'{method} {path}',
                    'description': f'Auto-generated from Express route: {method} {path}'
                })
    
    return routes


def _find_router_imports(content: str, base_dir: Path) -> List[Path]:
    """Find router files imported in the main file."""
    
    router_files = []
    
    # Patterns for router imports
    import_patterns = [
        r'require\([\'"]([^\'\"]+)[\'\"]\)',
        r'import\s+.*\s+from\s+[\'"]([^\'\"]+)[\'"]'
    ]
    
    for pattern in import_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            import_path = match.group(1)
            
            # Skip node_modules and built-in modules
            if import_path.startswith('.') or import_path.startswith('/'):
                # Resolve relative path
                if import_path.startswith('./') or import_path.startswith('../'):
                    resolved_path = (base_dir / import_path).resolve()
                else:
                    resolved_path = Path(import_path)
                
                # Try with and without .js extension
                candidates = [
                    resolved_path,
                    resolved_path.with_suffix('.js'),
                    resolved_path / 'index.js'
                ]
                
                for candidate in candidates:
                    if candidate.exists() and _file_looks_like_router(candidate):
                        router_files.append(candidate)
                        break
    
    return router_files


def _file_looks_like_router(file_path: Path) -> bool:
    """Check if a file defines Express routes."""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        # Look for route definitions
        route_patterns = [
            r'\.get\s*\(',
            r'\.post\s*\(',
            r'\.put\s*\(',
            r'\.patch\s*\(',
            r'\.delete\s*\(',
            r'\.route\s*\('
        ]
        
        for pattern in route_patterns:
            if re.search(pattern, content):
                return True
        
        return False
        
    except (OSError, UnicodeDecodeError):
        return False


def _routes_to_openapi(routes: List[Dict[str, Any]], project_path: Path) -> Dict[str, Any]:
    """Convert extracted routes to OpenAPI specification."""
    
    # Try to get project name from package.json
    project_name = "Express API"
    package_json = project_path / 'package.json'
    if package_json.exists():
        try:
            with open(package_json, encoding='utf-8') as f:
                pkg_data = json.load(f)
            project_name = pkg_data.get('name', project_name)
        except (json.JSONDecodeError, OSError):
            pass
    
    openapi_spec = {
        'openapi': '3.0.3',
        'info': {
            'title': project_name,
            'version': '1.0.0',
            'description': 'Auto-generated OpenAPI spec from Express.js routes'
        },
        'servers': [
            {'url': 'http://localhost:3000', 'description': 'Development server'}
        ],
        'paths': {}
    }
    
    # Group routes by path
    paths_dict = {}
    for route in routes:
        path = route['path']
        method = route['method'].lower()
        
        if path not in paths_dict:
            paths_dict[path] = {}
        
        # Convert Express path parameters to OpenAPI format
        openapi_path = _convert_express_path_to_openapi(path)
        
        # Basic operation definition
        operation = {
            'summary': route.get('summary', f'{method.upper()} {path}'),
            'description': route.get('description', f'Auto-generated from Express route'),
            'responses': {
                '200': {
                    'description': 'Successful response',
                    'content': {
                        'application/json': {
                            'schema': {'type': 'object'}
                        }
                    }
                }
            }
        }
        
        # Add parameters for path parameters
        path_params = _extract_path_parameters(openapi_path)
        if path_params:
            operation['parameters'] = [
                {
                    'name': param,
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                    'description': f'Path parameter: {param}'
                }
                for param in path_params
            ]
        
        # Add request body for POST/PUT/PATCH
        if method in ['post', 'put', 'patch']:
            operation['requestBody'] = {
                'content': {
                    'application/json': {
                        'schema': {'type': 'object'}
                    }
                }
            }
        
        paths_dict[openapi_path] = paths_dict.get(openapi_path, {})
        paths_dict[openapi_path][method] = operation
    
    openapi_spec['paths'] = paths_dict
    return openapi_spec


def _convert_express_path_to_openapi(express_path: str) -> str:
    """Convert Express path parameters to OpenAPI format."""
    # Convert :param to {param}
    return re.sub(r':(\w+)', r'{\1}', express_path)


def _extract_path_parameters(openapi_path: str) -> List[str]:
    """Extract parameter names from OpenAPI path."""
    return re.findall(r'\{(\w+)\}', openapi_path)
