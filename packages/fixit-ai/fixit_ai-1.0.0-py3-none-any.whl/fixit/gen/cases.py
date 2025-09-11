"""Generate test plans and test cases from OpenAPI specifications."""

import hashlib
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from ..spec.models import SpecModel, Operation, Parameter, Schema, SecurityScheme, HttpMethod


class TestCaseType(str, Enum):
    """Types of test cases."""
    HAPPY_PATH = "happy_path"
    MISSING_REQUIRED = "missing_required"
    INVALID_ENUM = "invalid_enum"
    INVALID_TYPE = "invalid_type"
    BOUNDARY_VALUE = "boundary_value"
    UNAUTHORIZED = "unauthorized"


@dataclass
class TestCase:
    """Represents a single test case."""
    id: str
    name: str
    description: str
    case_type: TestCaseType
    method: str
    path: str
    endpoint_id: str
    expected_status: int
    headers: Dict[str, str]
    path_params: Dict[str, Any]
    query_params: Dict[str, Any]
    request_body: Optional[Dict[str, Any]]
    tags: List[str]
    operation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class TestPlan:
    """Test plan containing multiple test cases."""
    schema_version: str = "v1"
    spec_hash: str = ""
    plan_hash: str = ""
    title: str = ""
    description: str = ""
    base_url: str = ""
    framework: str = "unknown"  # Add framework detection
    security_schemes: Dict[str, Dict[str, Any]] = None
    test_cases: List[TestCase] = None
    
    def __post_init__(self):
        if self.security_schemes is None:
            self.security_schemes = {}
        if self.test_cases is None:
            self.test_cases = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "schema_version": self.schema_version,
            "spec_hash": self.spec_hash,
            "plan_hash": self.plan_hash,
            "title": self.title,
            "description": self.description,
            "base_url": self.base_url,
            "security_schemes": self.security_schemes,
            "test_cases": [tc.to_dict() for tc in self.test_cases]
        }


class TestPlanGenerator:
    """Generates test plans from OpenAPI specifications."""
    
    def __init__(self, spec: SpecModel):
        self.spec = spec
        self.test_cases: List[TestCase] = []
        
    def generate_test_plan(self, include_edge_cases: bool = True) -> TestPlan:
        """Generate a complete test plan from the OpenAPI spec.
        
        Args:
            include_edge_cases: Whether to include edge case test scenarios
            
        Returns:
            TestPlan object containing all generated test cases
        """
        self.test_cases = []
        
        # Generate test cases for each operation
        operations = self.spec.get_all_operations()
        for operation in operations:
            self._generate_operation_test_cases(operation, include_edge_cases)
        
        # Create the test plan
        test_plan = TestPlan(
            spec_hash=self._compute_spec_hash(),
            title=f"Test Plan for {self.spec.info.title}",
            description=f"Generated test plan for {self.spec.info.title} v{self.spec.info.version}",
            base_url=self._get_base_url(),
            framework=self._detect_framework(),
            security_schemes=self._extract_security_schemes(),
            test_cases=self.test_cases
        )
        
        # Compute plan hash
        test_plan.plan_hash = self._compute_plan_hash(test_plan)
        
        return test_plan
    
    def _generate_operation_test_cases(self, operation: Operation, include_edge_cases: bool) -> None:
        """Generate test cases for a single operation."""
        # Happy path test case
        happy_case = self._create_happy_path_test_case(operation)
        self.test_cases.append(happy_case)
        
        if include_edge_cases:
            # Missing required parameter test cases
            self.test_cases.extend(self._create_missing_required_test_cases(operation))
            
            # Invalid enum test cases
            self.test_cases.extend(self._create_invalid_enum_test_cases(operation))
            
            # Invalid type test cases
            self.test_cases.extend(self._create_invalid_type_test_cases(operation))
            
            # Boundary value test cases
            self.test_cases.extend(self._create_boundary_value_test_cases(operation))
            
            # Unauthorized test cases
            if self._has_security_requirements(operation):
                self.test_cases.extend(self._create_unauthorized_test_cases(operation))
    
    def _create_happy_path_test_case(self, operation: Operation) -> TestCase:
        """Create a happy path test case for an operation."""
        test_case_id = f"{operation.endpoint_id.replace(' ', '_').lower()}_happy_path"
        
        return TestCase(
            id=test_case_id,
            name=f"{operation.method.value.upper()} {operation.path} - Happy Path",
            description=f"Test successful {operation.method.value.upper()} request to {operation.path}",
            case_type=TestCaseType.HAPPY_PATH,
            method=operation.method.value.upper(),
            path=operation.path,
            endpoint_id=operation.endpoint_id,
            expected_status=int(operation.primary_success_status),
            headers=self._generate_headers(operation),
            path_params=self._generate_path_params(operation.path_parameters),
            query_params=self._generate_query_params(operation.query_parameters),
            request_body=self._generate_request_body(operation),
            tags=operation.tags or [],
            operation_id=operation.operation_id
        )
    
    def _create_missing_required_test_cases(self, operation: Operation) -> List[TestCase]:
        """Create test cases for missing required parameters."""
        test_cases = []
        
        # Missing required query parameters
        for param in operation.query_parameters:
            if param.required:
                test_case_id = f"{operation.endpoint_id.replace(' ', '_').lower()}_missing_{param.name}"
                
                # Generate query params without this required parameter
                query_params = self._generate_query_params(operation.query_parameters)
                if param.name in query_params:
                    del query_params[param.name]
                
                test_cases.append(TestCase(
                    id=test_case_id,
                    name=f"{operation.method.value.upper()} {operation.path} - Missing {param.name}",
                    description=f"Test {operation.method.value.upper()} request missing required parameter '{param.name}'",
                    case_type=TestCaseType.MISSING_REQUIRED,
                    method=operation.method.value.upper(),
                    path=operation.path,
                    endpoint_id=operation.endpoint_id,
                    expected_status=400,
                    headers=self._generate_headers(operation),
                    path_params=self._generate_path_params(operation.path_parameters),
                    query_params=query_params,
                    request_body=self._generate_request_body(operation),
                    tags=operation.tags or [],
                    operation_id=operation.operation_id
                ))
        
        # Missing required request body
        if operation.request_body and operation.request_body.required:
            test_case_id = f"{operation.endpoint_id.replace(' ', '_').lower()}_missing_body"
            
            test_cases.append(TestCase(
                id=test_case_id,
                name=f"{operation.method.value.upper()} {operation.path} - Missing Request Body",
                description=f"Test {operation.method.value.upper()} request missing required request body",
                case_type=TestCaseType.MISSING_REQUIRED,
                method=operation.method.value.upper(),
                path=operation.path,
                endpoint_id=operation.endpoint_id,
                expected_status=400,
                headers=self._generate_headers(operation),
                path_params=self._generate_path_params(operation.path_parameters),
                query_params=self._generate_query_params(operation.query_parameters),
                request_body=None,
                tags=operation.tags or [],
                operation_id=operation.operation_id
            ))
        
        return test_cases
    
    def _create_invalid_enum_test_cases(self, operation: Operation) -> List[TestCase]:
        """Create test cases for invalid enum values."""
        test_cases = []
        
        for param in operation.all_parameters:
            if param.schema_ and param.schema_.enum:
                test_case_id = f"{operation.endpoint_id.replace(' ', '_').lower()}_invalid_{param.name}_enum"
                
                # Generate parameters with invalid enum value
                if param.location.value == "query":
                    query_params = self._generate_query_params(operation.query_parameters)
                    query_params[param.name] = "INVALID_ENUM_VALUE"
                    path_params = self._generate_path_params(operation.path_parameters)
                else:
                    query_params = self._generate_query_params(operation.query_parameters)
                    path_params = self._generate_path_params(operation.path_parameters)
                    if param.location.value == "path":
                        path_params[param.name] = "INVALID_ENUM_VALUE"
                
                test_cases.append(TestCase(
                    id=test_case_id,
                    name=f"{operation.method.value.upper()} {operation.path} - Invalid {param.name} Enum",
                    description=f"Test {operation.method.value.upper()} request with invalid enum value for '{param.name}'",
                    case_type=TestCaseType.INVALID_ENUM,
                    method=operation.method.value.upper(),
                    path=operation.path,
                    endpoint_id=operation.endpoint_id,
                    expected_status=400,
                    headers=self._generate_headers(operation),
                    path_params=path_params,
                    query_params=query_params,
                    request_body=self._generate_request_body(operation),
                    tags=operation.tags or [],
                    operation_id=operation.operation_id
                ))
        
        return test_cases
    
    def _create_invalid_type_test_cases(self, operation: Operation) -> List[TestCase]:
        """Create test cases for invalid parameter types."""
        test_cases = []
        
        for param in operation.all_parameters:
            if param.schema_ and param.schema_.type:
                invalid_value = self._get_invalid_value_for_type(param.schema_.type)
                if invalid_value is not None:
                    test_case_id = f"{operation.endpoint_id.replace(' ', '_').lower()}_invalid_{param.name}_type"
                    
                    # Generate parameters with invalid type
                    if param.location.value == "query":
                        query_params = self._generate_query_params(operation.query_parameters)
                        query_params[param.name] = invalid_value
                        path_params = self._generate_path_params(operation.path_parameters)
                    else:
                        query_params = self._generate_query_params(operation.query_parameters)
                        path_params = self._generate_path_params(operation.path_parameters)
                        if param.location.value == "path":
                            path_params[param.name] = invalid_value
                    
                    test_cases.append(TestCase(
                        id=test_case_id,
                        name=f"{operation.method.value.upper()} {operation.path} - Invalid {param.name} Type",
                        description=f"Test {operation.method.value.upper()} request with invalid type for '{param.name}'",
                        case_type=TestCaseType.INVALID_TYPE,
                        method=operation.method.value.upper(),
                        path=operation.path,
                        endpoint_id=operation.endpoint_id,
                        expected_status=400,
                        headers=self._generate_headers(operation),
                        path_params=path_params,
                        query_params=query_params,
                        request_body=self._generate_request_body(operation),
                        tags=operation.tags or [],
                        operation_id=operation.operation_id
                    ))
        
        return test_cases
    
    def _create_boundary_value_test_cases(self, operation: Operation) -> List[TestCase]:
        """Create test cases for boundary values."""
        test_cases = []
        
        for param in operation.all_parameters:
            if param.schema_:
                boundary_values = self._get_boundary_values(param.schema_)
                for boundary_type, value in boundary_values.items():
                    test_case_id = f"{operation.endpoint_id.replace(' ', '_').lower()}_{param.name}_{boundary_type}"
                    
                    # Generate parameters with boundary value
                    if param.location.value == "query":
                        query_params = self._generate_query_params(operation.query_parameters)
                        query_params[param.name] = value
                        path_params = self._generate_path_params(operation.path_parameters)
                    else:
                        query_params = self._generate_query_params(operation.query_parameters)
                        path_params = self._generate_path_params(operation.path_parameters)
                        if param.location.value == "path":
                            path_params[param.name] = value
                    
                    expected_status = 200 if boundary_type.startswith("valid") else 400
                    
                    test_cases.append(TestCase(
                        id=test_case_id,
                        name=f"{operation.method.value.upper()} {operation.path} - {param.name} {boundary_type}",
                        description=f"Test {operation.method.value.upper()} request with {boundary_type} value for '{param.name}'",
                        case_type=TestCaseType.BOUNDARY_VALUE,
                        method=operation.method.value.upper(),
                        path=operation.path,
                        endpoint_id=operation.endpoint_id,
                        expected_status=expected_status,
                        headers=self._generate_headers(operation),
                        path_params=path_params,
                        query_params=query_params,
                        request_body=self._generate_request_body(operation),
                        tags=operation.tags or [],
                        operation_id=operation.operation_id
                    ))
        
        return test_cases
    
    def _create_unauthorized_test_cases(self, operation: Operation) -> List[TestCase]:
        """Create test cases for unauthorized access."""
        test_case_id = f"{operation.endpoint_id.replace(' ', '_').lower()}_unauthorized"
        
        # Generate headers without authorization
        headers = self._generate_headers(operation, include_auth=False)
        
        return [TestCase(
            id=test_case_id,
            name=f"{operation.method.value.upper()} {operation.path} - Unauthorized",
            description=f"Test {operation.method.value.upper()} request without authentication",
            case_type=TestCaseType.UNAUTHORIZED,
            method=operation.method.value.upper(),
            path=operation.path,
            endpoint_id=operation.endpoint_id,
            expected_status=401,
            headers=headers,
            path_params=self._generate_path_params(operation.path_parameters),
            query_params=self._generate_query_params(operation.query_parameters),
            request_body=self._generate_request_body(operation),
            tags=operation.tags or [],
            operation_id=operation.operation_id
        )]
    
    def _generate_headers(self, operation: Operation, include_auth: bool = True) -> Dict[str, str]:
        """Generate headers for an operation."""
        headers = {"Content-Type": "application/json"}
        
        # Add headers from parameters
        for param in operation.header_parameters:
            headers[param.name] = self._generate_example_value(param.schema_)
        
        # Add authorization headers if needed
        if include_auth and self._has_security_requirements(operation):
            auth_headers = self._generate_auth_headers(operation)
            headers.update(auth_headers)
        
        return headers
    
    def _generate_auth_headers(self, operation: Operation) -> Dict[str, str]:
        """Generate authentication headers for an operation."""
        headers = {}
        security_schemes = self.spec.get_security_schemes()
        
        # Use the first security requirement if multiple exist
        if operation.security:
            for security_req in operation.security:
                for scheme_name in security_req.keys():
                    if scheme_name in security_schemes:
                        scheme = security_schemes[scheme_name]
                        if scheme.type == "apiKey" and scheme.location == "header":
                            headers[scheme.name] = "test_api_key"
                        elif scheme.type == "http" and scheme.scheme == "bearer":
                            headers["Authorization"] = "Bearer test_token"
                        elif scheme.type == "http" and scheme.scheme == "basic":
                            headers["Authorization"] = "Basic dGVzdDp0ZXN0"  # test:test
                        break
                break
        
        return headers
    
    def _generate_path_params(self, parameters: List[Parameter]) -> Dict[str, Any]:
        """Generate path parameters."""
        path_params = {}
        for param in parameters:
            path_params[param.name] = self._generate_example_value(param.schema_)
        return path_params
    
    def _generate_query_params(self, parameters: List[Parameter]) -> Dict[str, Any]:
        """Generate query parameters."""
        query_params = {}
        for param in parameters:
            if param.required or param.schema_.default is not None:
                query_params[param.name] = self._generate_example_value(param.schema_)
        return query_params
    
    def _generate_request_body(self, operation: Operation) -> Optional[Dict[str, Any]]:
        """Generate request body for an operation."""
        if not operation.request_body:
            return None
        
        # Use JSON content type if available
        if "application/json" in operation.request_body.content:
            media_type = operation.request_body.content["application/json"]
            if media_type.schema_:
                return self._generate_example_from_schema(media_type.schema_)
            elif media_type.example:
                return media_type.example
        
        # Use first available content type
        for media_type in operation.request_body.content.values():
            if media_type.schema_:
                return self._generate_example_from_schema(media_type.schema_)
            elif media_type.example:
                return media_type.example
        
        return {}
    
    def _generate_example_value(self, schema: Optional[Schema]) -> Any:
        """Generate an example value for a schema."""
        if not schema:
            return "test_value"
        
        if schema.example is not None:
            return schema.example
        
        if schema.default is not None:
            return schema.default
        
        if schema.enum:
            return schema.enum[0]
        
        if schema.type == "string":
            return "test_string"
        elif schema.type == "integer":
            return 123
        elif schema.type == "number":
            return 123.45
        elif schema.type == "boolean":
            return True
        elif schema.type == "array":
            if schema.items:
                return [self._generate_example_value(schema.items)]
            return ["test_item"]
        elif schema.type == "object":
            return self._generate_example_from_schema(schema)
        
        return "test_value"
    
    def _generate_example_from_schema(self, schema: Schema) -> Dict[str, Any]:
        """Generate an example object from a schema."""
        if schema.example is not None:
            return schema.example
        
        example = {}
        if schema.properties:
            for prop_name, prop_schema in schema.properties.items():
                if not schema.required or prop_name in schema.required:
                    example[prop_name] = self._generate_example_value(prop_schema)
        
        return example
    
    def _get_invalid_value_for_type(self, type_name: str) -> Any:
        """Get an invalid value for a given type."""
        type_invalid_map = {
            "string": 123,
            "integer": "not_an_integer",
            "number": "not_a_number",
            "boolean": "not_a_boolean",
            "array": "not_an_array",
            "object": "not_an_object"
        }
        return type_invalid_map.get(type_name)
    
    def _get_boundary_values(self, schema: Schema) -> Dict[str, Any]:
        """Get boundary values for a schema."""
        boundary_values = {}
        
        if schema.type == "integer" or schema.type == "number":
            if schema.minimum is not None:
                boundary_values["valid_minimum"] = schema.minimum
                boundary_values["invalid_below_minimum"] = schema.minimum - 1
            if schema.maximum is not None:
                boundary_values["valid_maximum"] = schema.maximum
                boundary_values["invalid_above_maximum"] = schema.maximum + 1
        
        elif schema.type == "string":
            if schema.min_length is not None:
                boundary_values["valid_min_length"] = "x" * schema.min_length
                if schema.min_length > 0:
                    boundary_values["invalid_below_min_length"] = "x" * (schema.min_length - 1)
            if schema.max_length is not None:
                boundary_values["valid_max_length"] = "x" * schema.max_length
                boundary_values["invalid_above_max_length"] = "x" * (schema.max_length + 1)
        
        return boundary_values
    
    def _has_security_requirements(self, operation: Operation) -> bool:
        """Check if operation has security requirements."""
        return bool(operation.security or self.spec.security)
    
    def _extract_security_schemes(self) -> Dict[str, Dict[str, Any]]:
        """Extract security schemes for the test plan."""
        schemes = {}
        security_schemes = self.spec.get_security_schemes()
        
        for name, scheme in security_schemes.items():
            schemes[name] = {
                "type": scheme.type,
                "description": scheme.description,
                "name": scheme.name if hasattr(scheme, 'name') else None,
                "in": scheme.location if hasattr(scheme, 'location') else None,
                "scheme": scheme.scheme if hasattr(scheme, 'scheme') else None
            }
        
        return schemes
    
    def _get_base_url(self) -> str:
        """Get the base URL for the API."""
        if self.spec.servers:
            return self.spec.servers[0].url
        return "http://localhost:8000"
    
    def _detect_framework(self) -> str:
        """Detect the framework based on spec metadata and file structure."""
        # Check for FastAPI indicators in the spec
        if hasattr(self.spec, 'info') and self.spec.info:
            title = (self.spec.info.title or "").lower()
            description = (self.spec.info.description or "").lower()
            
            if "fastapi" in title or "fastapi" in description:
                return "fastapi"
        
        # Check for Express.js indicators
        if hasattr(self.spec, 'info') and self.spec.info:
            title = (self.spec.info.title or "").lower()
            if "express" in title or "node" in title or "javascript" in title:
                return "express"
        
        # Check current working directory for framework files
        from pathlib import Path
        cwd = Path.cwd()
        
        # FastAPI indicators: main.py, app.py, requirements.txt with fastapi
        if (cwd / "main.py").exists() or (cwd / "app.py").exists():
            return "fastapi"
        
        # Check examples directory for FastAPI
        if (cwd / "examples" / "fastapi_buggy" / "main.py").exists():
            return "fastapi"
        
        # Express.js indicators: app.js, server.js, package.json
        if (cwd / "app.js").exists() or (cwd / "server.js").exists() or (cwd / "package.json").exists():
            return "express"
        
        # Check examples directory for Express
        if (cwd / "examples" / "express_buggy" / "app.js").exists():
            return "express"
        
        # Default to fastapi for Python environments with uvicorn
        return "fastapi"
    
    def _compute_spec_hash(self) -> str:
        """Compute a hash of the OpenAPI spec for caching."""
        # Use the normalized JSON representation for consistent hashing
        from ..spec.loader import normalize_spec_to_json
        spec_json = normalize_spec_to_json(self.spec)
        return hashlib.sha256(spec_json.encode('utf-8')).hexdigest()[:16]
    
    def _compute_plan_hash(self, test_plan: TestPlan) -> str:
        """Compute a hash of the test plan for caching."""
        # Create a representation without the plan_hash field
        plan_dict = test_plan.to_dict()
        plan_dict.pop('plan_hash', None)
        plan_json = json.dumps(plan_dict, sort_keys=True)
        return hashlib.sha256(plan_json.encode('utf-8')).hexdigest()[:16]


# Convenience functions
def generate_test_plan(spec: SpecModel, include_edge_cases: bool = True) -> TestPlan:
    """Generate a test plan from an OpenAPI spec."""
    generator = TestPlanGenerator(spec)
    return generator.generate_test_plan(include_edge_cases)


def build_test_plan(spec: SpecModel, include_edge_cases: bool = True) -> TestPlan:
    """Alias for generate_test_plan for backward compatibility."""
    return generate_test_plan(spec, include_edge_cases)
