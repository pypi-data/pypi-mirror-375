"""Pydantic models aligned with JSON schemas for type safety and validation."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class FailureType(str, Enum):
    """Types of test failures."""
    ASSERTION_ERROR = "assertion_error"
    TYPE_ERROR = "type_error"
    VALUE_ERROR = "value_error"
    HTTP_ERROR = "http_error"
    CONNECTION_ERROR = "connection_error"
    TIMEOUT = "timeout"
    PERMISSION_ERROR = "permission_error"
    UNKNOWN = "unknown"


class Priority(str, Enum):
    """Fix priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ChangeType(str, Enum):
    """Types of code changes."""
    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"


class Severity(str, Enum):
    """Security severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorLocation(BaseModel):
    """Location of an error in code."""
    file: str
    line: int
    function: Optional[str] = None


class LineRange(BaseModel):
    """Range of lines in a file."""
    start: int
    end: int


class CodeChange(BaseModel):
    """Represents a suggested code change."""
    file: str
    change_type: ChangeType
    line_range: Optional[LineRange] = None
    suggested_code: Optional[str] = None
    explanation: Optional[str] = None


class RootCause(BaseModel):
    """Root cause analysis of a failure."""
    summary: str
    details: str
    error_location: Optional[ErrorLocation] = None


class FixSuggestion(BaseModel):
    """A suggested fix for a test failure."""
    description: str
    code_changes: List[CodeChange]
    priority: Priority
    estimated_impact: Optional[str] = None


class SecurityImplication(BaseModel):
    """Security implications of a code issue."""
    severity: Severity
    description: str
    cwe_id: Optional[str] = None


class LLMMetadata(BaseModel):
    """Metadata about the LLM response."""
    model: str
    provider: str
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None


class CodePatch(BaseModel):
    """Unified diff patch from the LLM."""
    file: str
    diff: str


class FailureAdvice(BaseModel):
    """Complete advice for fixing a test failure."""
    test_id: str
    failure_type: FailureType
    root_cause: RootCause
    fix_suggestions: List[FixSuggestion] = Field(..., min_items=1, max_items=5)
    confidence_score: float = Field(..., ge=0, le=1)
    timestamp: datetime
    related_files: Optional[List[str]] = None
    security_implications: Optional[List[SecurityImplication]] = None
    llm_metadata: Optional[LLMMetadata] = None

    # OPTIONAL LLM patches (unified diffs)
    code_patches: Optional[List[CodePatch]] = None
    
    # Cache tracking fields (not serialized to JSON schema)
    is_cached: bool = Field(default=False, exclude=True)
    session_id: Optional[str] = Field(default=None, exclude=True)

    @validator('confidence_score')
    def validate_confidence(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Confidence score must be between 0 and 1')
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.dict(exclude_none=True, by_alias=True)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.json(exclude_none=True, by_alias=True)


class SecurityFinding(BaseModel):
    """Individual security finding."""
    severity: Severity
    type: str
    description: str
    recommendation: str
    affected_code: Optional[Dict[str, Any]] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None
    fix_example: Optional[str] = None


class SecurityScanSummary(BaseModel):
    """Summary of security scan results."""
    total_issues: int
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class SecurityFindings(BaseModel):
    """Complete security scan results."""
    scan_id: str
    findings: List[SecurityFinding]
    summary: SecurityScanSummary
    timestamp: datetime
    target: Optional[Dict[str, Any]] = None