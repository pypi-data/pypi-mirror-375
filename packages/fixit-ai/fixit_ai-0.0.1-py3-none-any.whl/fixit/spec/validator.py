"""OpenAPI specification validator with path-aware error reporting."""

from typing import List, Dict, Any, Optional, Union
from pydantic import ValidationError
from dataclasses import dataclass

from .models import SpecModel, Operation, Parameter, Schema
from .loader import SpecLoader

@dataclass
class ValidationIssue:
    """Represents a validation issue with path-aware context."""
    path: str
    message: str
    severity: str = "error"  # error, warning, info
    code: Optional[str] = None
    json_pointer: Optional[str] = None  # <-- NEW FIELD

    def __str__(self) -> str:
        pointer = f" [{self.json_pointer}]" if self.json_pointer else ""
        prefix = f"[{self.severity.upper()}]" if self.severity != "error" else ""
        code_suffix = f" ({self.code})" if self.code else ""
        return f"{prefix} {self.path}{pointer}: {self.message}{code_suffix}"

def to_json_pointer(parts: list) -> str:
    """Convert a list of path parts to a JSON Pointer string."""
    pointer = ""
    for part in parts:
        if isinstance(part, int):
            pointer += f"/{part}"
        else:
            pointer += "/" + str(part).replace("~", "~0").replace("/", "~1")
    return pointer or "/"

class SpecValidator:
    """Validates OpenAPI specifications with detailed path-aware error reporting."""

    def __init__(self):
        self.issues: List[ValidationIssue] = []

    def validate_spec(self, spec: Union[SpecModel, Dict[str, Any], str]) -> List[ValidationIssue]:
        self.issues = []

        # Load spec if needed
        if isinstance(spec, str):
            try:
                loader = SpecLoader()
                spec_model = loader.load_from_file(spec)
            except Exception as e:
                self.issues.append(ValidationIssue(
                    path="<root>",
                    message=f"Failed to load spec: {e}",
                    code="SPEC_LOAD_ERROR",
                    json_pointer="/"
                ))
                return self.issues
        elif isinstance(spec, dict):
            try:
                loader = SpecLoader()
                spec_model = loader.load_from_dict(spec)
            except ValidationError as e:
                self._parse_pydantic_errors(e.errors())
                return self.issues
            except Exception as e:
                self.issues.append(ValidationIssue(
                    path="<root>",
                    message=f"Failed to parse spec: {e}",
                    code="SPEC_PARSE_ERROR",
                    json_pointer="/"
                ))
                return self.issues
        else:
            spec_model = spec

        self._validate_spec_model(spec_model)
        return self.issues

    def _parse_pydantic_errors(self, errors: List[Dict[str, Any]]) -> None:
        for error in errors:
            path_parts = []
            for loc_part in error.get('loc', []):
                path_parts.append(loc_part)
            path = ".".join(str(p) for p in path_parts) if path_parts else "<root>"
            message = error.get('msg', 'Validation error')
            error_type = error.get('type', 'unknown')
            self.issues.append(ValidationIssue(
                path=path,
                message=message,
                code=f"PYDANTIC_{error_type.upper()}",
                json_pointer=to_json_pointer(path_parts)
            ))

    def _validate_spec_model(self, spec: SpecModel) -> None:
        self._validate_info(spec)
        self._validate_servers(spec)
        self._validate_paths(spec)
        self._validate_components(spec)
        self._validate_security(spec)
        self._validate_references(spec)

    def _validate_info(self, spec: SpecModel) -> None:
        if not spec.info.title.strip():
            self.issues.append(ValidationIssue(
                path="info.title",
                message="Title cannot be empty",
                code="EMPTY_TITLE",
                json_pointer="/info/title"
            ))
        if not spec.info.version.strip():
            self.issues.append(ValidationIssue(
                path="info.version",
                message="Version cannot be empty",
                code="EMPTY_VERSION",
                json_pointer="/info/version"
            ))

    def _validate_servers(self, spec: SpecModel) -> None:
        if spec.servers:
            for i, server in enumerate(spec.servers):
                if not server.url.strip():
                    self.issues.append(ValidationIssue(
                        path=f"servers[{i}].url",
                        message="Server URL cannot be empty",
                        code="EMPTY_SERVER_URL",
                        json_pointer=f"/servers/{i}/url"
                    ))

    def _validate_paths(self, spec: SpecModel) -> None:
        if not spec.paths:
            self.issues.append(ValidationIssue(
                path="paths",
                message="No paths defined in specification",
                severity="warning",
                code="NO_PATHS",
                json_pointer="/paths"
            ))
            return
        for path, path_item in spec.paths.items():
            self._validate_path(path, path_item, spec)

    def _validate_path(self, path: str, path_item: Any, spec: SpecModel) -> None:
        path_prefix = f"paths.{path}"
        pointer_prefix = f"/paths/{path.lstrip('/')}"
        if not path.startswith('/'):
            self.issues.append(ValidationIssue(
                path=path_prefix,
                message="Path should start with '/'",
                code="INVALID_PATH_FORMAT",
                json_pointer=pointer_prefix
            ))
        path_params = self._extract_path_parameters(path)
        operations = spec.get_all_operations()
        for operation in operations:
            if operation.path == path:
                self._validate_operation(
                    operation, path_params,
                    f"{path_prefix}.{operation.method.value}",
                    f"{pointer_prefix}/{operation.method.value}"
                )

    def _validate_operation(self, operation: Operation, path_params: List[str], path_prefix: str, pointer_prefix: str) -> None:
        defined_path_params = {p.name for p in operation.path_parameters}
        for param_name in path_params:
            if param_name not in defined_path_params:
                self.issues.append(ValidationIssue(
                    path=f"{path_prefix}.parameters",
                    message=f"Path parameter '{param_name}' not defined in parameters",
                    code="MISSING_PATH_PARAMETER",
                    json_pointer=f"{pointer_prefix}/parameters"
                ))
        for param in operation.path_parameters:
            if param.name not in path_params:
                self.issues.append(ValidationIssue(
                    path=f"{path_prefix}.parameters",
                    message=f"Path parameter '{param.name}' defined but not used in path",
                    severity="warning",
                    code="UNUSED_PATH_PARAMETER",
                    json_pointer=f"{pointer_prefix}/parameters"
                ))
        for i, param in enumerate(operation.all_parameters):
            self._validate_parameter(param, f"{path_prefix}.parameters[{i}]", f"{pointer_prefix}/parameters/{i}")
        if not operation.responses:
            self.issues.append(ValidationIssue(
                path=f"{path_prefix}.responses",
                message="No responses defined",
                code="NO_RESPONSES",
                json_pointer=f"{pointer_prefix}/responses"
            ))
        else:
            self._validate_responses(operation.responses, f"{path_prefix}.responses", f"{pointer_prefix}/responses")
        if operation.request_body:
            self._validate_request_body(operation.request_body, f"{path_prefix}.requestBody", f"{pointer_prefix}/requestBody")
        if operation.operation_id:
            if not operation.operation_id.strip():
                self.issues.append(ValidationIssue(
                    path=f"{path_prefix}.operationId",
                    message="Operation ID cannot be empty",
                    code="EMPTY_OPERATION_ID",
                    json_pointer=f"{pointer_prefix}/operationId"
                ))

    def _validate_parameter(self, parameter: Parameter, path_prefix: str, pointer_prefix: str) -> None:
        if not parameter.name.strip():
            self.issues.append(ValidationIssue(
                path=f"{path_prefix}.name",
                message="Parameter name cannot be empty",
                code="EMPTY_PARAMETER_NAME",
                json_pointer=f"{pointer_prefix}/name"
            ))
        if parameter.schema_:
            self._validate_schema(parameter.schema_, f"{path_prefix}.schema", f"{pointer_prefix}/schema")

    def _validate_responses(self, responses: Dict[str, Any], path_prefix: str, pointer_prefix: str) -> None:
        has_success_response = any(
            code.startswith('2') or code == 'default'
            for code in responses.keys()
        )
        if not has_success_response:
            self.issues.append(ValidationIssue(
                path=path_prefix,
                message="No success response (2xx) defined",
                severity="warning",
                code="NO_SUCCESS_RESPONSE",
                json_pointer=pointer_prefix
            ))
        for code, response in responses.items():
            if code != 'default' and not code.isdigit():
                self.issues.append(ValidationIssue(
                    path=f"{path_prefix}.{code}",
                    message=f"Invalid response code: {code}",
                    code="INVALID_RESPONSE_CODE",
                    json_pointer=f"{pointer_prefix}/{code}"
                ))

    def _validate_request_body(self, request_body: Any, path_prefix: str, pointer_prefix: str) -> None:
        if hasattr(request_body, 'content') and not request_body.content:
            self.issues.append(ValidationIssue(
                path=f"{path_prefix}.content",
                message="Request body content cannot be empty",
                code="EMPTY_REQUEST_BODY_CONTENT",
                json_pointer=f"{pointer_prefix}/content"
            ))

    def _validate_schema(self, schema: Schema, path_prefix: str, pointer_prefix: str) -> None:
        if schema.type == "array" and not schema.items:
            self.issues.append(ValidationIssue(
                path=f"{path_prefix}.items",
                message="Array schema must define items",
                code="ARRAY_MISSING_ITEMS",
                json_pointer=f"{pointer_prefix}/items"
            ))
        if schema.type == "object" and schema.additional_properties is False and not schema.properties:
            self.issues.append(ValidationIssue(
                path=path_prefix,
                message="Object schema with additionalProperties=false should define properties",
                severity="warning",
                code="OBJECT_NO_PROPERTIES",
                json_pointer=pointer_prefix
            ))
        if schema.enum and not isinstance(schema.enum, list):
            self.issues.append(ValidationIssue(
                path=f"{path_prefix}.enum",
                message="Enum values must be an array",
                code="INVALID_ENUM",
                json_pointer=f"{pointer_prefix}/enum"
            ))
        if schema.minimum is not None and schema.maximum is not None:
            if schema.minimum > schema.maximum:
                self.issues.append(ValidationIssue(
                    path=path_prefix,
                    message="Minimum value cannot be greater than maximum",
                    code="INVALID_NUMERIC_RANGE",
                    json_pointer=pointer_prefix
                ))
        if schema.min_length is not None and schema.max_length is not None:
            if schema.min_length > schema.max_length:
                self.issues.append(ValidationIssue(
                    path=path_prefix,
                    message="minLength cannot be greater than maxLength",
                    code="INVALID_STRING_LENGTH_RANGE",
                    json_pointer=pointer_prefix
                ))

    def _validate_components(self, spec: SpecModel) -> None:
        if not spec.components:
            return
        if spec.components.security_schemes:
            for name, scheme in spec.components.security_schemes.items():
                self._validate_security_scheme(scheme, f"components.securitySchemes.{name}", f"/components/securitySchemes/{name}")

    def _validate_security_scheme(self, scheme: Any, path_prefix: str, pointer_prefix: str) -> None:
        if hasattr(scheme, 'type'):
            if scheme.type == "apiKey":
                if not hasattr(scheme, 'name') or not scheme.name:
                    self.issues.append(ValidationIssue(
                        path=f"{path_prefix}.name",
                        message="API key security scheme must define 'name'",
                        code="APIKEY_MISSING_NAME",
                        json_pointer=f"{pointer_prefix}/name"
                    ))
                if not hasattr(scheme, 'location') or not scheme.location:
                    self.issues.append(ValidationIssue(
                        path=f"{path_prefix}.in",
                        message="API key security scheme must define 'in'",
                        code="APIKEY_MISSING_IN",
                        json_pointer=f"{pointer_prefix}/in"
                    ))
            elif scheme.type == "http":
                if not hasattr(scheme, 'scheme') or not scheme.scheme:
                    self.issues.append(ValidationIssue(
                        path=f"{path_prefix}.scheme",
                        message="HTTP security scheme must define 'scheme'",
                        code="HTTP_MISSING_SCHEME",
                        json_pointer=f"{pointer_prefix}/scheme"
                    ))

    def _validate_security(self, spec: SpecModel) -> None:
        pass

    def _validate_references(self, spec: SpecModel) -> None:
        pass

    def _extract_path_parameters(self, path: str) -> List[str]:
        import re
        pattern = r'\{([^}]+)\}'
        return re.findall(pattern, path)

def validate_spec_file(file_path: str) -> List[ValidationIssue]:
    validator = SpecValidator()
    return validator.validate_spec(file_path)

def validate_spec_dict(spec_dict: Dict[str, Any]) -> List[ValidationIssue]:
    validator = SpecValidator()
    return validator.validate_spec(spec_dict)

def validate_spec_model(spec_model: SpecModel) -> List[ValidationIssue]:
    validator = SpecValidator()
    return validator.validate_spec(spec_model)