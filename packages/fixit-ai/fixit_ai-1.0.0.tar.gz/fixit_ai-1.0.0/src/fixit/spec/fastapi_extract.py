"""FastAPI code-first OpenAPI extraction."""

from __future__ import annotations
import importlib
import sys
from typing import Any, Dict, Optional


def extract_openapi(module_app: str) -> Optional[Dict[str, Any]]:
    """
    Import module:app, return app.openapi() dict.
    
    Args:
        module_app: String in format 'pkg.module:attr' (e.g., 'examples.fastapi_buggy.main:app')
        
    Returns:
        OpenAPI spec dictionary from FastAPI app, or None if extraction fails
        
    Example:
        >>> spec = extract_openapi('examples.fastapi_buggy.main:app')
        >>> if spec:
        ...     print(spec['info']['title'])
        'Buggy API'
    """
    if ':' not in module_app:
        return None
    
    try:
        module_name, app_attr = module_app.split(':', 1)
        
        # Import the module
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            return None
        
        # Get the app attribute
        try:
            app = getattr(module, app_attr)
        except AttributeError:
            return None
        
        # Validate it's a FastAPI app
        if not hasattr(app, 'openapi'):
            return None
        
        # Extract OpenAPI spec
        try:
            openapi_spec = app.openapi()
            if isinstance(openapi_spec, dict) and 'paths' in openapi_spec:
                return openapi_spec
            return None
        except Exception:
            return None
            
    except Exception:
        return None
