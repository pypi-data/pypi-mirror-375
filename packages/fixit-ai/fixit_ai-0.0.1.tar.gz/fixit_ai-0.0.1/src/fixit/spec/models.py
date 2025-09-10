"""Pydantic models for OpenAPI specification parsing and validation."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from enum import Enum


class HttpMethod(str, Enum):
    """HTTP methods supported in OpenAPI."""
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"
    HEAD = "head"
    OPTIONS = "options"
    TRACE = "trace"


class ParameterLocation(str, Enum):
    """Parameter locations in OpenAPI."""
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"


class SecuritySchemeType(str, Enum):
    """Security scheme types in OpenAPI."""
    API_KEY = "apiKey"
    HTTP = "http"
    OAUTH2 = "oauth2"
    OPEN_ID_CONNECT = "openIdConnect"


class Schema(BaseModel):
    """OpenAPI Schema object."""
    type: Optional[str] = None
    format: Optional[str] = None
    items: Optional['Schema'] = None
    properties: Optional[Dict[str, 'Schema']] = None
    required: Optional[List[str]] = None
    enum: Optional[List[Any]] = None
    example: Optional[Any] = None
    default: Optional[Any] = None
    minimum: Optional[Union[int, float]] = None
    maximum: Optional[Union[int, float]] = None
    min_length: Optional[int] = Field(None, alias="minLength")
    max_length: Optional[int] = Field(None, alias="maxLength")
    pattern: Optional[str] = None
    additional_properties: Optional[Union[bool, 'Schema']] = Field(None, alias="additionalProperties")
    
    model_config = ConfigDict(populate_by_name=True)


class Parameter(BaseModel):
    """OpenAPI Parameter object."""
    name: str
    location: ParameterLocation = Field(alias="in")
    description: Optional[str] = None
    required: Optional[bool] = False
    deprecated: Optional[bool] = False
    schema_: Optional[Schema] = Field(None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(populate_by_name=True)
    
    @field_validator('required', mode='before')
    @classmethod
    def set_required_for_path_params(cls, v, info):
        """Path parameters are always required."""
        if info.data.get('location') == ParameterLocation.PATH:
            return True
        return v if v is not None else False


class MediaType(BaseModel):
    """OpenAPI Media Type object."""
    schema_: Optional[Schema] = Field(None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Any]] = None
    encoding: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(populate_by_name=True)


class RequestBody(BaseModel):
    """OpenAPI Request Body object."""
    description: Optional[str] = None
    content: Dict[str, MediaType] = {}
    required: Optional[bool] = False


class Header(BaseModel):
    """OpenAPI Header object."""
    description: Optional[str] = None
    required: Optional[bool] = False
    deprecated: Optional[bool] = False
    schema_: Optional[Schema] = Field(None, alias="schema")
    
    model_config = ConfigDict(populate_by_name=True)


class Response(BaseModel):
    """OpenAPI Response object."""
    description: str
    headers: Optional[Dict[str, Header]] = None
    content: Optional[Dict[str, MediaType]] = None
    links: Optional[Dict[str, Any]] = None


class OAuthFlow(BaseModel):
    """OpenAPI OAuth Flow object."""
    authorization_url: Optional[str] = Field(None, alias="authorizationUrl")
    token_url: Optional[str] = Field(None, alias="tokenUrl")
    refresh_url: Optional[str] = Field(None, alias="refreshUrl")
    scopes: Dict[str, str] = {}

    model_config = ConfigDict(populate_by_name=True)


class OAuthFlows(BaseModel):
    """OpenAPI OAuth Flows object."""
    implicit: Optional[OAuthFlow] = None
    password: Optional[OAuthFlow] = None
    client_credentials: Optional[OAuthFlow] = Field(None, alias="clientCredentials")
    authorization_code: Optional[OAuthFlow] = Field(None, alias="authorizationCode")

    model_config = ConfigDict(populate_by_name=True)


class SecurityScheme(BaseModel):
    """OpenAPI Security Scheme object."""
    type: SecuritySchemeType
    description: Optional[str] = None
    name: Optional[str] = None  # For apiKey
    location: Optional[str] = Field(None, alias="in")  # For apiKey
    scheme: Optional[str] = None  # For http
    bearer_format: Optional[str] = Field(None, alias="bearerFormat")  # For http bearer
    flows: Optional[OAuthFlows] = None  # For oauth2
    open_id_connect_url: Optional[str] = Field(None, alias="openIdConnectUrl")  # For openIdConnect

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode='after')
    def check_required_fields(self) -> 'SecurityScheme':
        """Validate conditionally required fields."""
        if self.type == SecuritySchemeType.API_KEY:
            if not self.name:
                raise ValueError("'name' is required for apiKey security scheme")
            if not self.location:
                raise ValueError("'in' is required for apiKey security scheme")

        elif self.type == SecuritySchemeType.HTTP:
            if not self.scheme:
                raise ValueError("'scheme' is required for http security scheme")

        elif self.type == SecuritySchemeType.OAUTH2:
            if not self.flows:
                raise ValueError("'flows' is required for oauth2 security scheme")

        elif self.type == SecuritySchemeType.OPEN_ID_CONNECT:
            if not self.open_id_connect_url:
                raise ValueError("'openIdConnectUrl' is required for openIdConnect security scheme")

        return self


class Operation(BaseModel):
    """OpenAPI Operation object."""
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    external_docs: Optional[Dict[str, Any]] = Field(None, alias="externalDocs")
    operation_id: Optional[str] = Field(None, alias="operationId")
    parameters: Optional[List[Parameter]] = None
    request_body: Optional[RequestBody] = Field(None, alias="requestBody")
    responses: Dict[str, Response] = {}
    callbacks: Optional[Dict[str, Any]] = None
    deprecated: Optional[bool] = False
    security: Optional[List[Dict[str, List[str]]]] = None
    servers: Optional[List[Dict[str, Any]]] = None
    
    # Custom fields for our use
    method: Optional[HttpMethod] = None
    path: Optional[str] = None
    endpoint_id: str = ""  # Will be computed as method + path
    
    model_config = ConfigDict(populate_by_name=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.endpoint_id and self.method and self.path:
            self.endpoint_id = f"{self.method.value.upper()} {self.path}"
    
    @property
    def success_responses(self) -> Dict[str, Response]:
        """Get successful response codes (2xx)."""
        return {
            code: response for code, response in self.responses.items()
            if code.startswith('2') and code != 'default'
        }
    
    @property
    def primary_success_status(self) -> str:
        """Get the primary success status code (first 2xx or 200)."""
        success_codes = list(self.success_responses.keys())
        if not success_codes:
            return "200"  # Default assumption
        return success_codes[0]
    
    @property
    def all_parameters(self) -> List[Parameter]:
        """Get all parameters including path, query, header, and cookie."""
        return self.parameters or []
    
    @property
    def path_parameters(self) -> List[Parameter]:
        """Get only path parameters."""
        return [p for p in self.all_parameters if p.location == ParameterLocation.PATH]
    
    @property
    def query_parameters(self) -> List[Parameter]:
        """Get only query parameters."""
        return [p for p in self.all_parameters if p.location == ParameterLocation.QUERY]
    
    @property
    def header_parameters(self) -> List[Parameter]:
        """Get only header parameters."""
        return [p for p in self.all_parameters if p.location == ParameterLocation.HEADER]


class PathItem(BaseModel):
    """OpenAPI Path Item object."""
    ref: Optional[str] = Field(None, alias="$ref")
    summary: Optional[str] = None
    description: Optional[str] = None
    get: Optional[Operation] = None
    put: Optional[Operation] = None
    post: Optional[Operation] = None
    delete: Optional[Operation] = None
    options: Optional[Operation] = None
    head: Optional[Operation] = None
    patch: Optional[Operation] = None
    trace: Optional[Operation] = None
    servers: Optional[List[Dict[str, Any]]] = None
    parameters: Optional[List[Parameter]] = None
    
    model_config = ConfigDict(populate_by_name=True)


class Info(BaseModel):
    """OpenAPI Info object."""
    title: str
    description: Optional[str] = None
    terms_of_service: Optional[str] = Field(None, alias="termsOfService")
    contact: Optional[Dict[str, Any]] = None
    license: Optional[Dict[str, Any]] = None
    version: str
    
    model_config = ConfigDict(populate_by_name=True)


class Server(BaseModel):
    """OpenAPI Server object."""
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class Components(BaseModel):
    """OpenAPI Components object."""
    schemas: Optional[Dict[str, Schema]] = None
    responses: Optional[Dict[str, Response]] = None
    parameters: Optional[Dict[str, Parameter]] = None
    examples: Optional[Dict[str, Any]] = None
    request_bodies: Optional[Dict[str, RequestBody]] = Field(None, alias="requestBodies")
    headers: Optional[Dict[str, Header]] = None
    security_schemes: Optional[Dict[str, SecurityScheme]] = Field(None, alias="securitySchemes")
    links: Optional[Dict[str, Any]] = None
    callbacks: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(populate_by_name=True)


class SpecModel(BaseModel):
    """Root OpenAPI Specification model."""
    openapi: str
    info: Info
    servers: Optional[List[Server]] = None
    paths: Dict[str, PathItem] = {}
    components: Optional[Components] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    tags: Optional[List[Dict[str, Any]]] = None
    external_docs: Optional[Dict[str, Any]] = Field(None, alias="externalDocs")
    
    model_config = ConfigDict(populate_by_name=True)
    
    def get_all_operations(self) -> List[Operation]:
        """Extract all operations from all paths."""
        operations = []
        
        for path, path_item in self.paths.items():
            if path_item.ref:
                # Skip $ref items for now
                continue
                
            for method in HttpMethod:
                operation = getattr(path_item, method.value, None)
                if operation:
                    # Set the method and path on the operation
                    operation.method = method
                    operation.path = path
                    operation.endpoint_id = f"{method.value.upper()} {path}"
                    operations.append(operation)
        
        return operations
    
    def get_security_schemes(self) -> Dict[str, SecurityScheme]:
        """Get all security schemes defined in components."""
        if not self.components or not self.components.security_schemes:
            return {}
        return self.components.security_schemes
    
    def get_operation_by_id(self, operation_id: str) -> Optional[Operation]:
        """Find operation by operationId."""
        for operation in self.get_all_operations():
            if operation.operation_id == operation_id:
                return operation
        return None
    
    def get_operation_by_endpoint_id(self, endpoint_id: str) -> Optional[Operation]:
        """Find operation by endpoint_id (method + path)."""
        for operation in self.get_all_operations():
            if operation.endpoint_id == endpoint_id:
                return operation
        return None


# Update forward references
Schema.model_rebuild()
Components.model_rebuild()
