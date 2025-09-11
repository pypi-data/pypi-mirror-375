from __future__ import annotations
import httpx
from typing import Optional, Dict, Any
from ..adapter import LLMAdapter, LLMResponse, LLMConfig, LLMProvider

_MIN_FAILURE_ADVICE_SCHEMA = {
    "name": "FailureAdvice",
    "schema": {
        "type": "object",
        "required": ["test_id","failure_type","root_cause","fix_suggestions","confidence_score","timestamp"],
        "properties": {
            "test_id": {"type": "string"},
            "failure_type": {"type": "string","enum":["assertion_error","type_error","value_error","http_error","connection_error","timeout","permission_error","unknown"]},
            "root_cause": {"type": "object","required": ["summary","details"],"properties":{"summary":{"type":"string"},"details":{"type":"string"}}},
            "fix_suggestions": {
                "type": "array","minItems": 1,"maxItems": 1,
                "items": {
                    "type": "object",
                    "required": ["description","code_changes","priority"],
                    "properties": {
                        "description":{"type":"string"},
                        "code_changes":{
                            "type":"array","minItems":1,"maxItems":1,
                            "items":{"type":"object","required":["file","change_type"],"properties":{"file":{"type":"string"},"change_type":{"type":"string","enum":["add","modify","delete"]}}}
                        },
                        "priority":{"type":"string","enum":["high","medium","low"]}
                    }
                }
            },
            "confidence_score":{"type":"number","minimum":0,"maximum":1},
            "timestamp":{"type":"string","format":"date-time"},
            "code_patches": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["file","diff"],
                    "properties": {
                        "file": {"type": "string"},
                        "diff": {"type": "string"}
                    }
                }
            }
        }
    }
}

class LMStudioAdapter(LLMAdapter):
    def _timeout(self) -> httpx.Timeout:
        return httpx.Timeout(connect=10, read=self.config.timeout, write=self.config.timeout, pool=self.config.timeout)

    def is_available(self) -> bool:
        base = (self.config.api_url or "").rstrip("/")
        try:
            with httpx.Client(timeout=self._timeout()) as client:
                r = client.get(f"{base}/models")
                return r.status_code == 200
        except Exception:
            return False

    def _chat(self, prompt: str, system_message: Optional[str]) -> Dict[str, Any]:
        base = (self.config.api_url or "").rstrip("/")
        url = f"{base}/chat/completions"
        payload = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens if self.config.max_tokens is not None else 256,
            "messages": [
                {"role": "system", "content": system_message or "Return ONLY a JSON object that matches the schema."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "response_format": {
                "type": "json_schema",
                "json_schema": _MIN_FAILURE_ADVICE_SCHEMA
            }
        }
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        with httpx.Client(timeout=self._timeout()) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()

    def _completions(self, prompt: str) -> Dict[str, Any]:
        base = (self.config.api_url or "").rstrip("/")
        url = f"{base}/completions"
        prompt2 = "Return ONLY a valid JSON object. No markdown, no comments, end with '}'.\n\n" + prompt
        payload = {
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens if self.config.max_tokens is not None else 256,
            "prompt": prompt2,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        with httpx.Client(timeout=self._timeout()) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()

    def query(self, prompt: str, **kwargs) -> LLMResponse:
        sys_msg = kwargs.get("system_message") or "Return ONLY a valid JSON object that matches the schema."
        try:
            data = self._chat(prompt, sys_msg)
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            data = self._completions(prompt)
        except Exception:
            data = self._completions(prompt)

        content = ""
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception:
            content = data.get("choices", [{}])[0].get("text", "") or ""

        finish_reason = data.get("choices", [{}])[0].get("finish_reason")
        usage = data.get("usage", {})
        tokens_used = usage.get("total_tokens")

        return LLMResponse(
            content=content or "",
            model=self.config.model,
            provider=LLMProvider.LM_STUDIO.value,
            tokens_used=tokens_used,
            finish_reason=finish_reason,
            metadata={"raw": data},
        )