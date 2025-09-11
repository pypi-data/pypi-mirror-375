"""FastAPI code-first OpenAPI extraction."""

from __future__ import annotations
import importlib
import sys
from typing import Any, Dict


def extract_openapi(module_app: str) -> Dict[str, Any]:
    """
    Import module:app, verify it is a FastAPI app by checking it has a callable .openapi().
    Return the dict from app.openapi().
    Raise RuntimeError with helpful messages on import errors or wrong format.
    
    Args:
        module_app: String in format 'pkg.module:attr' (e.g., 'examples.fastapi_buggy.main:app')
        
    Returns:
        OpenAPI spec dictionary from FastAPI app
        
    Raises:
        RuntimeError: If module cannot be imported, app not found, or not a FastAPI app
        
    Example:
        >>> spec = extract_openapi('examples.fastapi_buggy.main:app')
        >>> print(spec['info']['title'])
        'Buggy API'
    """
    if ':' not in module_app:
        raise RuntimeError(f"Invalid module:app format: '{module_app}'. Expected format: 'module:app'")
    
    try:
        module_name, app_attr = module_app.split(':', 1)
        
        # Add current directory to Python path to help with relative imports
        import os
        cwd = os.getcwd()
        if cwd not in sys.path:
            sys.path.insert(0, cwd)
        
        # Import the module
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            raise RuntimeError(f"Cannot import module '{module_name}': {e}")
        
        # Get the app attribute
        try:
            app = getattr(module, app_attr)
        except AttributeError:
            raise RuntimeError(f"Module '{module_name}' has no attribute '{app_attr}'")
        
        # Validate it's a FastAPI app
        if not hasattr(app, 'openapi'):
            raise RuntimeError(f"Object '{module_app}' is not a FastAPI app (missing 'openapi' method)")
        
        if not callable(app.openapi):
            raise RuntimeError(f"Object '{module_app}' openapi attribute is not callable")
        
        # Extract OpenAPI spec
        try:
            openapi_spec = app.openapi()
            if not isinstance(openapi_spec, dict):
                raise RuntimeError(f"FastAPI app '{module_app}' openapi() returned {type(openapi_spec)}, expected dict")
            
            if 'paths' not in openapi_spec:
                raise RuntimeError(f"FastAPI app '{module_app}' openapi() returned invalid spec (missing 'paths')")
                
            return openapi_spec
            
        except Exception as e:
            raise RuntimeError(f"Error calling openapi() on '{module_app}': {e}")
            
    except RuntimeError:
        # Re-raise RuntimeError as-is
        raise
    except Exception as e:
        raise RuntimeError(f"Unexpected error extracting OpenAPI from '{module_app}': {e}")
