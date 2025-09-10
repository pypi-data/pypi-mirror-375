"""OpenAPI specification loader with normalization and serialization."""

import json
from ruamel import yaml
from typing import Dict, Any, Union, Optional, Tuple
from pathlib import Path
from pydantic import ValidationError
from .models import SpecModel

class SpecLoadError(Exception):
    """Exception raised when loading OpenAPI spec fails."""
    pass

class SpecLoader:
    """Loads and normalizes OpenAPI specifications."""
    
    def __init__(self):
        self.spec_model: Optional[SpecModel] = None
        self.yaml_parser = yaml.YAML(typ='safe', pure=True)
    
    def load_from_file(self, file_path: Union[str, Path]) -> SpecModel:
        file_path = Path(file_path)
        if not file_path.exists():
            raise SpecLoadError(f"Spec file not found: {file_path}")
        try:
            content = file_path.read_text(encoding='utf-8')
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                spec_dict = self.yaml_parser.load(content)
            elif file_path.suffix.lower() == '.json':
                spec_dict = json.loads(content)
            else:
                try:
                    spec_dict = json.loads(content)
                except json.JSONDecodeError:
                    spec_dict = self.yaml_parser.load(content)
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise SpecLoadError(f"Failed to parse spec file {file_path}: {e}")
        except Exception as e:
            raise SpecLoadError(f"Failed to read spec file {file_path}: {e}")
        return self.load_from_dict(spec_dict)
    
    def load_from_dict(self, spec_dict: Dict[str, Any]) -> SpecModel:
        try:
            normalized_dict = self._normalize_spec_dict(spec_dict)
            self.spec_model = SpecModel(**normalized_dict)
            return self.spec_model
        except ValidationError:
            raise
        except Exception as e:
            raise SpecLoadError(f"Failed to load spec: {e}")
    
    def load_from_url(self, url: str) -> SpecModel:
        try:
            import requests
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                spec_dict = response.json()
            else:
                spec_dict = yaml.safe_load(response.text)
            return self.load_from_dict(spec_dict)
        except ImportError:
            raise SpecLoadError("requests library is required to load specs from URLs")
        except Exception as e:
            raise SpecLoadError(f"Failed to load spec from URL {url}: {e}")
    
    def _normalize_spec_dict(self, spec_dict: Dict[str, Any]) -> Dict[str, Any]:
        normalized = spec_dict.copy()
        if 'openapi' not in normalized:
            if 'swagger' in normalized:
                raise SpecLoadError("Swagger 2.0 specs are not supported. Please use OpenAPI 3.0+")
            else:
                raise SpecLoadError("Missing 'openapi' field in spec")
        if 'paths' not in normalized:
            normalized['paths'] = {}
        
        # Resolve $ref references before processing
        normalized = self._resolve_references(normalized)
        
        normalized['paths'] = self._normalize_paths(normalized['paths'])
        if 'components' in normalized:
            normalized['components'] = self._normalize_components(normalized['components'])
        if 'info' not in normalized:
            raise SpecLoadError("Missing 'info' field in spec")
        return normalized
    
    def _resolve_references(self, spec_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve $ref references in the OpenAPI spec."""
        def resolve_ref(obj, components):
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref_path = obj['$ref']
                    if ref_path.startswith('#/components/schemas/'):
                        schema_name = ref_path.replace('#/components/schemas/', '')
                        if 'components' in components and 'schemas' in components['components']:
                            if schema_name in components['components']['schemas']:
                                resolved = components['components']['schemas'][schema_name].copy()
                                # Remove the $ref and replace with resolved content
                                return resolved
                    return obj  # Return as-is if can't resolve
                else:
                    # Recursively resolve references in nested objects
                    resolved_obj = {}
                    for key, value in obj.items():
                        resolved_obj[key] = resolve_ref(value, components)
                    return resolved_obj
            elif isinstance(obj, list):
                return [resolve_ref(item, components) for item in obj]
            else:
                return obj
        
        return resolve_ref(spec_dict, spec_dict)
    
    def _normalize_paths(self, paths: Dict[str, Any]) -> Dict[str, Any]:
        normalized_paths = {}
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            normalized_path_item = path_item.copy()
            for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options', 'trace']:
                if method in normalized_path_item:
                    operation = normalized_path_item[method]
                    if isinstance(operation, dict):
                        normalized_path_item[method] = self._normalize_operation(operation, method, path)
            normalized_paths[path] = normalized_path_item
        return normalized_paths
    
    def _normalize_operation(self, operation: Dict[str, Any], method: str, path: str) -> Dict[str, Any]:
        normalized = operation.copy()
        if 'responses' not in normalized:
            normalized['responses'] = {}
        if not any(code.startswith('2') for code in normalized['responses'].keys()):
            if method.lower() == 'post':
                normalized['responses']['201'] = {'description': 'Created'}
            else:
                normalized['responses']['200'] = {'description': 'Success'}
        if 'parameters' in normalized:
            normalized['parameters'] = [
                self._normalize_parameter(param) for param in normalized['parameters']
            ]
        if 'requestBody' in normalized:
            normalized['requestBody'] = self._normalize_request_body(normalized['requestBody'])
        return normalized
    
    def _normalize_parameter(self, parameter: Dict[str, Any]) -> Dict[str, Any]:
        normalized = parameter.copy()
        if 'name' not in normalized:
            raise SpecLoadError("Parameter missing 'name' field")
        if 'in' not in normalized:
            raise SpecLoadError(f"Parameter '{normalized['name']}' missing 'in' field")
        if normalized.get('in') == 'path':
            normalized['required'] = True
        elif 'required' not in normalized:
            normalized['required'] = False
        return normalized
    
    def _normalize_request_body(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        normalized = request_body.copy()
        if 'content' not in normalized:
            normalized['content'] = {}
        if 'required' not in normalized:
            normalized['required'] = False
        return normalized
    
    def _normalize_components(self, components: Dict[str, Any]) -> Dict[str, Any]:
        normalized = components.copy()
        if 'securitySchemes' not in normalized:
            normalized['securitySchemes'] = {}
        return normalized
    
    def to_normalized_json(self, spec_model: SpecModel = None) -> str:
        if spec_model is None:
            spec_model = self.spec_model
        if spec_model is None:
            raise SpecLoadError("No spec model available for serialization")
        spec_dict = spec_model.model_dump(by_alias=True, exclude_none=True)
        return json.dumps(spec_dict, indent=2, sort_keys=True, ensure_ascii=False)
    
    def to_normalized_dict(self, spec_model: SpecModel = None) -> Dict[str, Any]:
        if spec_model is None:
            spec_model = self.spec_model
        if spec_model is None:
            raise SpecLoadError("No spec model available for conversion")
        return spec_model.model_dump(by_alias=True, exclude_none=True)

# Convenience functions
def load_spec_from_file(file_path: Union[str, Path]) -> SpecModel:
    loader = SpecLoader()
    return loader.load_from_file(file_path)

def load_spec_from_dict(spec_dict: Dict[str, Any]) -> SpecModel:
    loader = SpecLoader()
    return loader.load_from_dict(spec_dict)

def load_spec_from_url(url: str) -> SpecModel:
    loader = SpecLoader()
    return loader.load_from_url(url)

def normalize_spec_to_json(spec_model: SpecModel) -> str:
    loader = SpecLoader()
    return loader.to_normalized_json(spec_model)

def load_as_dict(file_path: Union[str, Path]) -> Tuple[Dict[str, Any], str]:
    loader = SpecLoader()
    spec_model = loader.load_from_file(file_path)
    p = Path(file_path)
    normalized_path = p.with_name(p.stem + ".normalized.json")
    normalized_json = loader.to_normalized_json(spec_model)
    normalized_path.write_text(normalized_json, encoding="utf-8")
    spec_dict = loader.to_normalized_dict(spec_model)
    return spec_dict, str(normalized_path)

def load_model(file_path: Union[str, Path]) -> Tuple[SpecModel, str]:
    loader = SpecLoader()
    spec_model = loader.load_from_file(file_path)
    p = Path(file_path)
    normalized_path = p.with_name(p.stem + ".normalized.json")
    normalized_json = loader.to_normalized_json(spec_model)
    normalized_path.write_text(normalized_json, encoding="utf-8")
    return spec_model, str(normalized_path)

load = load_model

def normalize_spec_dict(spec_dict: Dict[str, Any], out_path: Path) -> Path:
    """
    Normalize a spec dict and write to out_path, returning the path.
    Reuses existing normalization/validation logic.
    """
    loader = SpecLoader()
    spec_model = loader.load_from_dict(spec_dict)
    normalized_json = loader.to_normalized_json(spec_model)
    out_path.write_text(normalized_json, encoding="utf-8")
    return out_path