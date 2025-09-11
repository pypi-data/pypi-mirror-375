"""
Advisor: strict JSON, trimmed prompt, hashed cache keys with API fingerprinting.
"""
from __future__ import annotations
import json
import logging
import re
import os 
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from tenacity import retry, stop_after_attempt, wait_exponential
from jsonschema import validate, ValidationError

from .models import FailureAdvice
from ..llm.adapter import LLMAdapter
from ..llm.cache import LLMCache
from ..core.config import read_config

logger = logging.getLogger(__name__)

STRICT_SYSTEM_MESSAGE = (
    "Return ONLY a valid JSON object matching the requested structure. "
    "No markdown, no code fences, no comments, no extra fields. End with '}'."
)

class AdvisorError(Exception): ...
class SchemaValidationError(AdvisorError): ...

class Advisor:
    def __init__(self, llm_adapter: Optional[LLMAdapter] = None, cache: Optional[LLMCache] = None):
        self.llm = llm_adapter
        self.cache = cache or LLMCache()
        self.schemas_dir = Path(__file__).parent / "schemas" / "v1"
        self.failure_schema = self._load_schema("failure_advice.schema.json")
        self.logger = logger
        # Enhanced cache system with API fingerprinting
        self._project_context = self._get_project_context()
        self._api_fingerprint = self._generate_api_fingerprint()
        self._session_id = self._generate_session_id()
        
        # Debug: Log cache initialization
        self.logger.debug(f"Cache init: project={self._project_context}, api={self._api_fingerprint}, session={self._session_id}")

    def _get_project_context(self) -> str:
        """
        Generate a unique project identifier for cache isolation.
        
        This prevents cache contamination between different APIs/projects.
        Uses base_url + spec_path for uniqueness.
        """
        try:
            config = read_config()
            if config:
                # Create unique identifier from base_url and spec_path
                context_parts = [
                    config.base_url.rstrip('/'),
                    str(config.spec_path)
                ]
                context_string = '|'.join(context_parts)
                # Hash for consistent length and avoid special characters
                return hashlib.md5(context_string.encode()).hexdigest()[:8]
            else:
                # Fallback: use current working directory
                return hashlib.md5(str(Path.cwd()).encode()).hexdigest()[:8]
        except Exception:
            # Ultimate fallback
            return "default"

    def _generate_api_fingerprint(self) -> str:
        """
        Generate fingerprint of current API structure.
        
        When API structure changes (new endpoints, modified spec),
        this fingerprint changes, forcing fresh analysis.
        """
        try:
            config = read_config()
            if config and Path(config.spec_path).exists():
                spec_content = Path(config.spec_path).read_text()
                # Hash spec content + base URL for API structure fingerprint
                fingerprint_data = f"{config.base_url}|{spec_content}"
                return hashlib.md5(fingerprint_data.encode()).hexdigest()[:12]
            return "unknown"
        except Exception:
            return "unknown"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID for current test run."""
        return hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]

    def _load_schema(self, name: str) -> Dict[str, Any]:
        p = self.schemas_dir / name
        if not p.exists():
            raise FileNotFoundError(f"Schema not found: {p}")
        return json.loads(p.read_text(encoding="utf-8"))

    def _validate(self, data: Dict[str, Any]) -> None:
        try:
            validate(instance=data, schema=self.failure_schema)
        except ValidationError as e:
            raise SchemaValidationError(f"Schema mismatch: {e.message}")

    def _raw_cache_key(self, failure: Dict[str, Any]) -> str:
        """
        Generate cache key with project isolation and API fingerprinting.
        
        Now includes:
        - Project context (prevents cross-contamination between APIs)
        - API fingerprint (invalidates cache when API structure changes)
        - Test-specific data (method, path, status codes)
        """
        parts = [
            # Project context ensures cache isolation between different APIs
            self._project_context,
            # API fingerprint detects structural changes (new endpoints, etc.)
            self._api_fingerprint,
            str(failure.get("test_id","")),
            str(failure.get("method","")),
            str(failure.get("path","")),
            str(failure.get("expected_status","")),
            str(failure.get("actual_status","")),
        ]
        cache_key = "|".join(parts)
        # Debug: Log cache key generation
        self.logger.debug(f"Generated cache key: {cache_key}")
        return cache_key

    def _extract_json_region(self, text: str) -> str:
        s = text.strip()
        if s.startswith("```json"):
            s = s[7:]
            if "```" in s:
                s = s[:s.index("```")]
        elif s.startswith("```"):
            s = s[3:]
            if "```" in s:
                s = s[:s.index("```")]
        start = s.find("{")
        if start == -1:
            return s
        s = s[start:]
        last = s.rfind("}")
        if last != -1:
            return s[:last+1]
        return s

    def _coerce_json_if_needed(self, raw: str) -> str:
        s = raw.strip()
        if re.search(r'"timestamp"\s*:\s*"[^"]*$', s):
            s += '"'
        # balance braces & brackets
        def bal(t: str, o: str, c: str) -> str:
            diff = t.count(o) - t.count(c)
            return t + (c * diff) if diff > 0 else t
        s = bal(s, "{", "}")
        s = bal(s, "[", "]")
        return s

    def _get_project_file_context(self, framework: str) -> str:
        """Get project structure context to help AI suggest correct file paths."""
        from pathlib import Path
        import os
        
        project_root = Path.cwd()
        context_lines = []
        
        # Scan for actual files in the project
        if framework == "fastapi":
            python_files = []
            for pattern in ["*.py", "**/*.py"]:
                for file in project_root.glob(pattern):
                    if file.is_file() and not file.name.startswith('.') and 'site-packages' not in str(file):
                        rel_path = file.relative_to(project_root)
                        if len(str(rel_path)) < 50:  # Keep paths reasonable
                            python_files.append(str(rel_path))
            
            if python_files:
                context_lines.append(f"Project has Python files: {', '.join(python_files[:10])}")
        
        elif framework == "express":
            js_files = []
            for pattern in ["*.js", "**/*.js"]:
                for file in project_root.glob(pattern):
                    if file.is_file() and not file.name.startswith('.') and 'node_modules' not in str(file):
                        rel_path = file.relative_to(project_root)
                        if len(str(rel_path)) < 50:  # Keep paths reasonable
                            js_files.append(str(rel_path))
            
            if js_files:
                context_lines.append(f"Project has JavaScript files: {', '.join(js_files[:10])}")
        
        if context_lines:
            return "Project context:\n" + "\n".join(f"- {line}" for line in context_lines) + "\n"
        
        return ""

    def _build_failure_prompt(self, failure: Dict[str, Any]) -> str:
        trimmed = {
        "test_id": failure.get("test_id"),
        "method": failure.get("method"),
        "path": failure.get("path"),
        "expected_status": failure.get("expected_status"),
        "actual_status": failure.get("actual_status"),
        "response_excerpt": (failure.get("response", {}).get("body_text", "")[:300] if failure.get("response") else "")
    }
    
        # Detect framework from failure data
        framework = failure.get("framework", "unknown")
        response_body = failure.get("response", {}).get("body_text", "")
        
        # Auto-detect framework if not explicitly set
        if framework == "unknown":
            if '"detail":[{' in response_body or 'HTTPException' in response_body:
                framework = "fastapi"
            elif '"error":' in response_body or 'res.status' in response_body:
                framework = "express"
        
        # Add project context for better file detection
        project_context = self._get_project_file_context(framework)
    
        # Completely generic example - no framework bias
        schema_example = (
        '{"test_id":"post_/users_validation_error","failure_type":"assertion_error",'
        '"root_cause":{"summary":"Validation error","details":"Invalid input format"},'
        '"fix_suggestions":[{"description":"Add input validation","code_changes":[{"file":"server_file","change_type":"modify"}],"priority":"high"}],'
        '"confidence_score":0.9,"timestamp":"2025-01-01T00:00:00Z",'
        '"code_patches":[{"file":"server_file","diff":"--- server_file\\n+++ server_file\\n@@ -10,7 +10,9 @@\\n def create_user(data):\\n+    if not data:\\n+        raise ValidationError(\\"Missing data\\")\\n     return user"}]}'
        )
        
        framework_hint = ""
        if framework == "fastapi":
            framework_hint = "- This is a FastAPI project. Use Python syntax, HTTPException, Pydantic models, @app.get() decorators, etc. Check for actual file names like main.py, app.py, src/main.py, app/main.py, api/main.py, backend/main.py. "
        elif framework == "express":
            framework_hint = "- This is an Express.js project. Use JavaScript syntax, res.status(), app.get(), middleware, etc. Check for actual file names like app.js, server.js, src/app.js, routes/index.js, lib/app.js. "
        
        return (
        "Analyze this API test failure and return ONLY valid JSON per the example. "
        "No extra fields. Keep it short; one line; end with '}'.\n\n"
        f"Failure (trimmed):\n{json.dumps(trimmed, ensure_ascii=False)}\n\n"
        f"JSON example (shape, optional code_patches shown):\n{schema_example}\n"
        f"{project_context}"
        f"{framework_hint}"
        "Constraints:\n- fix_suggestions: exactly 1 item\n- code_changes: exactly 1 item\n"
        "- Include code_patches with a unified diff (---/+++/@@) whenever you can identify a specific code fix. "
        "- Determine the correct file and framework from the test context and API response format. "
        "- For FastAPI: use Python syntax with HTTPException, Pydantic models, etc. "
        "- For Express.js: use JavaScript syntax with res.status(), middleware, etc. "
        "- Use the most likely actual file name based on the project structure and framework conventions. "
        "Try to provide a code patch for common issues like validation errors, missing fields, auth issues, etc. "
        "Only omit code_patches if the fix requires external dependencies or major architectural changes.\n"
        "Return ONLY the JSON object."
    )

    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
    def _query_with_retry(self, prompt: str) -> Dict[str, Any]:
        if not self.llm:
            raise AdvisorError("No LLM adapter configured")
        response = self.llm.query(prompt, system_message=STRICT_SYSTEM_MESSAGE)
        raw = response.content or ""
        
        # Only show debug output if explicitly requested
        if os.getenv("FIXIT_LLM_VERBOSE") == "1":
            # Extract test_id for cleaner debug output
            test_id = "unknown"
            if '"test_id":"' in raw:
                start = raw.find('"test_id":"') + 11
                end = raw.find('"', start)
                if end != -1:
                    test_id = raw[start:end]
            
            # Show concise analysis info
            print(f"🔍 [LLM] Analyzing {test_id}... ", end="")
            
            # Extract confidence if available
            confidence = "?"
            if '"confidence_score":' in raw:
                start = raw.find('"confidence_score":') + 19
                end = raw.find(',', start)
                if end == -1:
                    end = raw.find('}', start)
                if end != -1:
                    confidence = raw[start:end].strip()
            
            print(f"(confidence: {confidence}) ✓")
            
        region = self._extract_json_region(raw)
        try:
            return json.loads(region)
        except json.JSONDecodeError:
            repaired = self._coerce_json_if_needed(region)
            return json.loads(repaired)

    def explain_failure(self, test_id_or_failure: Any, *args, **kwargs) -> FailureAdvice:
        # Support dict signature directly
        if isinstance(test_id_or_failure, dict):
            failure = test_id_or_failure
        else:
            # legacy signature: (test_id, error_message, stack_trace, ...)
            failure = (kwargs.get("additional_context") or {}).copy()
            failure.update({"test_id": test_id_or_failure})

        # Enhanced cache key with project isolation and API fingerprinting
        raw_key = self._raw_cache_key(failure)
        hashed_key = self.cache.generate_key(raw_key)
        
        # Debug: Log cache lookup
        self.logger.debug(f"Looking for cache key: {hashed_key[:16]}...")
        
        cached = self.cache.get(hashed_key)
        if cached:
            self.logger.info(f"✅ Cache HIT: {failure.get('test_id', 'unknown')} (key: {hashed_key[:8]})")
            # Create FailureAdvice from cached data and mark as cached
            advice = FailureAdvice.model_validate(cached)
            # Set cache tracking fields (these are excluded from serialization)
            advice.is_cached = True
            advice.session_id = self._session_id
            return advice
        
        # No cache hit - generate fresh analysis
        self.logger.info(f"❌ Cache MISS: {failure.get('test_id', 'unknown')} - generating fresh analysis")

        prompt = self._build_failure_prompt(failure)
        data = self._query_with_retry(prompt)
        self._validate(data)
        data.setdefault("timestamp", datetime.now().isoformat())
        advice = FailureAdvice.model_validate(data)
        
        # Mark as fresh analysis
        advice.is_cached = False
        advice.session_id = self._session_id

        # Store as pure JSON dict with enhanced key
        cache_data = advice.model_dump(by_alias=True, exclude_none=True)
        self.cache.set(hashed_key, cache_data)
        self.logger.info(f"💾 Cache SET: {failure.get('test_id', 'unknown')} (key: {hashed_key[:8]})")
        return advice

    def is_available(self) -> bool:
        return bool(self.llm and self.llm.is_available())