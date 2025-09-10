# API Contracts Documentation

This document describes the key data structures and schemas used in the Dr. Fixit AI system for API testing and validation.

## Overview

The Dr. Fixit AI system provides automated API testing capabilities by:
1. Parsing OpenAPI specifications 
2. Generating comprehensive test plans
3. Executing tests with detailed failure context
4. Reporting security findings and vulnerabilities

## TestPlan v1 Schema

The TestPlan represents a complete test suite generated from an OpenAPI specification.

### Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.drfixit.ai/v1/test-plan.json",
  "title": "TestPlan v1",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "Human-readable title for the test plan"
    },
    "spec_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{16}$",
      "description": "SHA-256 hash of the source OpenAPI specification (truncated to 16 chars)"
    },
    "plan_hash": {
      "type": "string", 
      "pattern": "^[a-f0-9]{16}$",
      "description": "SHA-256 hash of the generated test plan content (truncated to 16 chars)"
    },
    "base_url": {
      "type": "string",
      "format": "uri",
      "description": "Base URL for API endpoints"
    },
    "security_schemes": {
      "type": "object",
      "description": "Security schemes from OpenAPI spec",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["apiKey", "http", "oauth2", "openIdConnect"]
          },
          "scheme": {
            "type": "string",
            "description": "HTTP auth scheme (for type: http)"
          },
          "location": {
            "type": "string", 
            "enum": ["query", "header", "cookie"],
            "description": "Location of API key (for type: apiKey)"
          },
          "name": {
            "type": "string",
            "description": "Name of header/query parameter (for type: apiKey)"
          }
        },
        "required": ["type"]
      }
    },
    "test_cases": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/TestCase"
      },
      "description": "Array of generated test cases"
    }
  },
  "required": ["title", "spec_hash", "plan_hash", "base_url", "test_cases"],
  "$defs": {
    "TestCase": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier for the test case"
        },
        "name": {
          "type": "string",
          "description": "Human-readable test case name"
        },
        "description": {
          "type": "string",
          "description": "Detailed description of what the test validates"
        },
        "case_type": {
          "type": "string",
          "enum": ["happy_path", "missing_required", "invalid_enum", "invalid_type", "unauthorized", "boundary_value"],
          "description": "Type of test case for categorization"
        },
        "method": {
          "type": "string",
          "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
          "description": "HTTP method"
        },
        "path": {
          "type": "string",
          "description": "API endpoint path with parameter placeholders"
        },
        "endpoint_id": {
          "type": "string",
          "description": "Identifier for the endpoint being tested"
        },
        "operation_id": {
          "type": ["string", "null"],
          "description": "OpenAPI operationId if specified"
        },
        "expected_status": {
          "type": "integer",
          "minimum": 100,
          "maximum": 599,
          "description": "Expected HTTP status code"
        },
        "headers": {
          "type": "object",
          "description": "HTTP headers to send with request",
          "additionalProperties": {
            "type": "string"
          }
        },
        "path_params": {
          "type": "object",
          "description": "Path parameter values",
          "additionalProperties": true
        },
        "query_params": {
          "type": "object", 
          "description": "Query parameter values",
          "additionalProperties": true
        },
        "request_body": {
          "description": "Request body data (any type)",
          "anyOf": [
            {"type": "object"},
            {"type": "array"},
            {"type": "string"},
            {"type": "number"},
            {"type": "boolean"},
            {"type": "null"}
          ]
        },
        "tags": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Tags for organizing and filtering test cases"
        }
      },
      "required": ["id", "name", "description", "case_type", "method", "path", "endpoint_id", "expected_status"]
    }
  }
}
```

### Usage Example

```python
from fixit.gen.cases import TestPlanGenerator
from fixit.spec.loader import SpecLoader

# Load OpenAPI specification
loader = SpecLoader()
spec = loader.load_from_file("api-spec.yaml")

# Generate test plan
generator = TestPlanGenerator()
test_plan = generator.generate_test_plan(spec, base_url="https://api.example.com")

# Access test plan properties
print(f"Test Plan: {test_plan.title}")
print(f"Spec Hash: {test_plan.spec_hash}")
print(f"Total Test Cases: {len(test_plan.test_cases)}")

# Filter by test case type
happy_path_tests = [tc for tc in test_plan.test_cases if tc.case_type == "happy_path"]
```

## FailureContext Schema

The FailureContext captures detailed information when API tests fail, enabling effective debugging and analysis.

### Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.drfixit.ai/v1/failure-context.json",
  "title": "FailureContext v1",
  "type": "object",
  "properties": {
    "test_case_id": {
      "type": "string",
      "description": "ID of the failing test case"
    },
    "endpoint_id": {
      "type": "string",
      "description": "ID of the API endpoint being tested"
    },
    "method": {
      "type": "string",
      "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
      "description": "HTTP method used"
    },
    "path": {
      "type": "string",
      "description": "API endpoint path"
    },
    "expected_status": {
      "type": "integer",
      "minimum": 100,
      "maximum": 599,
      "description": "Expected HTTP status code"
    },
    "actual_status": {
      "type": "integer", 
      "minimum": 100,
      "maximum": 599,
      "description": "Actual HTTP status code received"
    },
    "request_data": {
      "type": "object",
      "properties": {
        "method": {"type": "string"},
        "path": {"type": "string"},
        "headers": {
          "type": "object",
          "additionalProperties": {"type": "string"}
        },
        "path_params": {
          "type": "object",
          "additionalProperties": true
        },
        "query_params": {
          "type": "object", 
          "additionalProperties": true
        },
        "request_body": {
          "description": "Request body sent",
          "anyOf": [
            {"type": "object"},
            {"type": "array"},
            {"type": "string"},
            {"type": "null"}
          ]
        }
      },
      "required": ["method", "path", "headers"],
      "description": "Complete request data that was sent"
    },
    "response_data": {
      "type": "object",
      "properties": {
        "status_code": {"type": "integer"},
        "headers": {
          "type": "object",
          "additionalProperties": {"type": "string"}
        },
        "body": {
          "description": "Response body received",
          "anyOf": [
            {"type": "object"},
            {"type": "array"}, 
            {"type": "string"},
            {"type": "null"}
          ]
        }
      },
      "required": ["status_code", "headers"],
      "description": "Complete response data that was received"
    },
    "error_message": {
      "type": "string",
      "description": "Human-readable error description"
    },
    "spec_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{16}$",
      "description": "Hash of the OpenAPI spec used for testing (truncated to 16 chars)"
    },
    "plan_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{16}$",
      "description": "Hash of the test plan used (truncated to 16 chars)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the failure occurred"
    }
  },
  "required": [
    "test_case_id",
    "endpoint_id", 
    "method",
    "path",
    "expected_status",
    "actual_status",
    "request_data",
    "response_data", 
    "error_message",
    "spec_hash",
    "plan_hash"
  ]
}
```

### Usage Example

```python
from fixit.gen.templates.pytest_endpoint import TestFailureContext

# Create failure context (typically done automatically in tests)
failure_context = TestFailureContext(
    test_case_id="test_001",
    endpoint_id="GET /api/users/{id}",
    method="GET",
    path="/api/users/123",
    expected_status=200,
    actual_status=404,
    request_data={
        "method": "GET",
        "path": "/api/users/123",
        "headers": {"Accept": "application/json"},
        "path_params": {"id": "123"},
        "query_params": {},
        "request_body": None
    },
    response_data={
        "status_code": 404,
        "headers": {"Content-Type": "application/json"},
        "body": {"error": "User not found"}
    },
    error_message="Expected status 200, got 404"
)

# Convert to dictionary for logging
failure_dict = failure_context.to_dict()
```

## SecurityFindings v1 Schema

The SecurityFindings schema captures security vulnerabilities and issues discovered during API testing and analysis.

### Schema Definition

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.drfixit.ai/v1/security-findings.json",
  "title": "SecurityFindings v1",
  "type": "object",
  "properties": {
    "scan_id": {
      "type": "string",
      "description": "Unique identifier for the security scan"
    },
    "spec_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "Hash of the analyzed OpenAPI specification"
    },
    "scan_timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the security scan was performed"
    },
    "findings": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/SecurityFinding"
      },
      "description": "List of security findings discovered"
    },
    "summary": {
      "type": "object",
      "properties": {
        "total_findings": {"type": "integer", "minimum": 0},
        "critical_count": {"type": "integer", "minimum": 0},
        "high_count": {"type": "integer", "minimum": 0},
        "medium_count": {"type": "integer", "minimum": 0},
        "low_count": {"type": "integer", "minimum": 0},
        "info_count": {"type": "integer", "minimum": 0}
      },
      "required": ["total_findings", "critical_count", "high_count", "medium_count", "low_count", "info_count"],
      "description": "Summary statistics of findings by severity"
    }
  },
  "required": ["scan_id", "spec_hash", "scan_timestamp", "findings", "summary"],
  "$defs": {
    "SecurityFinding": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier for this finding"
        },
        "severity": {
          "type": "string",
          "enum": ["critical", "high", "medium", "low", "info"],
          "description": "Severity level of the security finding"
        },
        "category": {
          "type": "string",
          "enum": [
            "authentication",
            "authorization", 
            "input_validation",
            "data_exposure",
            "injection",
            "cryptography",
            "configuration",
            "rate_limiting",
            "cors",
            "other"
          ],
          "description": "Category of security issue"
        },
        "title": {
          "type": "string",
          "description": "Short title describing the finding"
        },
        "description": {
          "type": "string", 
          "description": "Detailed description of the security issue"
        },
        "endpoint": {
          "type": "object",
          "properties": {
            "method": {"type": "string"},
            "path": {"type": "string"},
            "operation_id": {"type": ["string", "null"]}
          },
          "description": "Affected API endpoint (if applicable)"
        },
        "cwe_id": {
          "type": ["integer", "null"],
          "description": "Common Weakness Enumeration ID"
        },
        "owasp_category": {
          "type": ["string", "null"],
          "description": "OWASP API Security Top 10 category"
        },
        "remediation": {
          "type": "string",
          "description": "Recommended steps to fix the issue"
        },
        "evidence": {
          "type": "object",
          "description": "Evidence supporting the finding",
          "properties": {
            "location": {"type": "string"},
            "details": {"type": "object"},
            "proof_of_concept": {"type": ["string", "null"]}
          }
        },
        "confidence": {
          "type": "string",
          "enum": ["high", "medium", "low"],
          "description": "Confidence level in the finding"
        }
      },
      "required": [
        "id",
        "severity", 
        "category",
        "title",
        "description",
        "remediation",
        "confidence"
      ]
    }
  }
}
```

### Usage Example

```python
from fixit.sec.checks import SecurityAnalyzer

# Analyze OpenAPI specification for security issues
analyzer = SecurityAnalyzer()
spec = loader.load_from_file("api-spec.yaml")
findings = analyzer.analyze(spec)

# Access findings
print(f"Total findings: {findings.summary.total_findings}")
print(f"Critical issues: {findings.summary.critical_count}")

# Filter high-severity findings
critical_findings = [f for f in findings.findings if f.severity == "critical"]

# Generate security report
for finding in critical_findings:
    print(f"[{finding.severity.upper()}] {finding.title}")
    print(f"Category: {finding.category}")
    print(f"Description: {finding.description}")
    print(f"Remediation: {finding.remediation}")
```

## Integration Examples

### Complete Testing Workflow

```python
from fixit.spec.loader import SpecLoader
from fixit.spec.validator import SpecValidator
from fixit.gen.cases import TestPlanGenerator
from fixit.gen.writer import TestFileWriter
from fixit.sec.checks import SecurityAnalyzer

# 1. Load and validate OpenAPI specification
loader = SpecLoader()
spec = loader.load_from_file("api-spec.yaml")

validator = SpecValidator()
validation_issues = validator.validate(spec)
if validation_issues:
    print("Validation issues found:")
    for issue in validation_issues:
        print(f"  {issue.path}: {issue.message}")

# 2. Generate test plan
generator = TestPlanGenerator()
test_plan = generator.generate_test_plan(spec, base_url="https://api.example.com")

# 3. Write test files
writer = TestFileWriter()
result = writer.write_test_files(
    test_plan=test_plan,
    output_dir=Path("./tests/generated"),
    split_by_tags=True
)

print(f"Generated {len(result.files)} test files")
print(f"Total test cases: {result.total_test_cases}")

# 4. Perform security analysis
analyzer = SecurityAnalyzer()
security_findings = analyzer.analyze(spec)

print(f"Security findings: {security_findings.summary.total_findings}")
if security_findings.summary.critical_count > 0:
    print(f"CRITICAL: {security_findings.summary.critical_count} critical security issues found!")
```

### Custom Test Generation

```python
# Generate tests with custom configuration
test_plan = generator.generate_test_plan(
    spec=spec,
    base_url="https://staging-api.example.com",
    include_edge_cases=True,
    auth_test_mode="comprehensive"  # Test all auth scenarios
)

# Filter test cases by type
security_tests = [tc for tc in test_plan.test_cases if "security" in tc.tags]
performance_tests = [tc for tc in test_plan.test_cases if tc.case_type == "boundary_value"]

# Generate separate test files for different concerns
writer.write_test_files(
    test_plan=TestPlan(
        title="Security Tests",
        spec_hash=test_plan.spec_hash,
        plan_hash=test_plan.plan_hash,
        base_url=test_plan.base_url,
        security_schemes=test_plan.security_schemes,
        test_cases=security_tests
    ),
    output_dir=Path("./tests/security"),
    file_prefix="test_security_"
)
```

## JSON Schema Validation

All schemas are available for validation and IDE support:

- **TestPlan v1**: `https://schemas.drfixit.ai/v1/test-plan.json`
- **FailureContext v1**: `https://schemas.drfixit.ai/v1/failure-context.json`  
- **SecurityFindings v1**: `https://schemas.drfixit.ai/v1/security-findings.json`

Use these URLs in your JSON Schema validators or IDE configurations for automatic validation and completion.

