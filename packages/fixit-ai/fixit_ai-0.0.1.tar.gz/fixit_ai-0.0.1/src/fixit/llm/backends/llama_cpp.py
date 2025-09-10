"""
llama.cpp backend adapter implementation.
This is a lightweight stub for direct llama.cpp integration.
"""

import json
import logging
from typing import Optional, Dict, Any
import subprocess
import tempfile
from pathlib import Path

from ..adapter import LLMAdapter, LLMResponse, LLMConfig

logger = logging.getLogger(__name__)


class LlamaCppAdapter(LLMAdapter):
    """
    Adapter for llama.cpp direct integration.
    This is a demonstration stub - full implementation would require
    llama-cpp-python or direct subprocess calls to llama.cpp binary.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize llama.cpp adapter.
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        
        # Path to llama.cpp executable
        self.executable_path = config.extra_params.get("executable_path") if config.extra_params else None
        if not self.executable_path:
            # Try to find in PATH
            self.executable_path = "llama-cli"  # or "main" for older versions
        
        # Path to model file (GGUF format)
        self.model_path = config.extra_params.get("model_path") if config.extra_params else None
        if not self.model_path:
            raise ValueError("model_path must be provided in extra_params for llama.cpp")
        
        # Additional llama.cpp parameters
        self.n_ctx = config.extra_params.get("n_ctx", 2048) if config.extra_params else 2048
        self.n_predict = config.max_tokens
        self.temperature = config.temperature
        self.n_threads = config.extra_params.get("n_threads", 4) if config.extra_params else 4
        
        # Check if using llama-cpp-python instead
        self.use_python_binding = config.extra_params.get("use_python_binding", False) if config.extra_params else False
        
        if self.use_python_binding:
            try:
                from llama_cpp import Llama
                self.llama = Llama(
                    model_path=self.model_path,
                    n_ctx=self.n_ctx,
                    n_threads=self.n_threads
                )
                logger.info("Using llama-cpp-python binding")
            except ImportError:
                logger.warning("llama-cpp-python not installed, falling back to subprocess")
                self.use_python_binding = False
                self.llama = None
    
    def query(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Send a query to llama.cpp.
        
        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
            
        Raises:
            Exception: If the query fails
        """
        formatted_prompt = self.format_for_json(prompt)
        
        if self.use_python_binding and self.llama:
            return self._query_python_binding(formatted_prompt, **kwargs)
        else:
            return self._query_subprocess(formatted_prompt, **kwargs)
    
    def _query_python_binding(self, prompt: str, **kwargs) -> LLMResponse:
        """Query using llama-cpp-python binding."""
        try:
            logger.debug("Querying llama.cpp via Python binding")
            
            # Generate response
            response = self.llama(
                prompt,
                max_tokens=kwargs.get("max_tokens", self.n_predict),
                temperature=kwargs.get("temperature", self.temperature),
                echo=False
            )
            
            content = response["choices"][0]["text"]
            tokens_used = response.get("usage", {}).get("total_tokens")
            
            return LLMResponse(
                content=content,
                model=self.config.model,
                provider="llama_cpp",
                tokens_used=tokens_used,
                finish_reason=response["choices"][0].get("finish_reason", "stop"),
                metadata=response.get("usage")
            )
            
        except Exception as e:
            logger.error(f"llama-cpp-python query failed: {e}")
            raise
    
    def _query_subprocess(self, prompt: str, **kwargs) -> LLMResponse:
        """Query using subprocess call to llama.cpp executable."""
        try:
            logger.debug("Querying llama.cpp via subprocess")
            
            # Write prompt to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            # Build command
            cmd = [
                self.executable_path,
                "-m", self.model_path,
                "-p", prompt,  # or "-f", prompt_file for file input
                "-n", str(kwargs.get("max_tokens", self.n_predict)),
                "-c", str(self.n_ctx),
                "-t", str(self.n_threads),
                "--temp", str(kwargs.get("temperature", self.temperature)),
                "--json-schema", "{}",  # Request JSON output
                "--no-display-prompt"  # Don't echo the prompt
            ]
            
            # Run llama.cpp
            logger.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout
            )
            
            # Clean up temp file
            Path(prompt_file).unlink(missing_ok=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"llama.cpp failed: {result.stderr}")
            
            content = result.stdout.strip()
            
            return LLMResponse(
                content=content,
                model=self.config.model,
                provider="llama_cpp",
                tokens_used=None,  # llama.cpp doesn't report this in stdout
                finish_reason="stop",
                metadata={"command": " ".join(cmd)}
            )
            
        except subprocess.TimeoutExpired:
            logger.error(f"llama.cpp timed out after {self.config.timeout}s")
            raise TimeoutError(f"llama.cpp timed out after {self.config.timeout}s")
            
        except FileNotFoundError:
            logger.error(f"llama.cpp executable not found: {self.executable_path}")
            raise FileNotFoundError(
                f"llama.cpp executable not found. "
                f"Please install llama.cpp and ensure '{self.executable_path}' is in PATH"
            )
            
        except Exception as e:
            logger.error(f"llama.cpp subprocess query failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """
        Check if llama.cpp is available and model file exists.
        
        Returns:
            True if llama.cpp and model are available
        """
        # Check if model file exists
        if not self.model_path or not Path(self.model_path).exists():
            return False
        
        if self.use_python_binding:
            return self.llama is not None
        
        # Check if executable exists
        try:
            result = subprocess.run(
                [self.executable_path, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class LlamaCppStubAdapter(LLMAdapter):
    """
    Simplified stub adapter for testing without actual llama.cpp.
    Returns mock responses for demonstration purposes.
    """
    
    def query(self, prompt: str, **kwargs) -> LLMResponse:
        """Return a mock response for testing."""
        import json
        from datetime import datetime
        
        # Generate a mock response based on prompt keywords
        if "security" in prompt.lower():
            response_type = "security"
        elif "test" in prompt.lower() or "failure" in prompt.lower():
            response_type = "test_failure"
        else:
            response_type = "generic"
        
        responses = {
            "test_failure": {
                "test_id": "test_llama_cpp_stub",
                "failure_type": "assertion_error",
                "root_cause": {
                    "summary": "Mock failure from llama.cpp stub",
                    "details": "This is a demonstration response from the llama.cpp stub adapter"
                },
                "fix_suggestions": [{
                    "description": "Review the implementation",
                    "code_changes": [{
                        "file": "stub.py",
                        "change_type": "modify"
                    }],
                    "priority": "medium"
                }],
                "confidence_score": 0.75,
                "timestamp": datetime.now().isoformat()
            },
            "security": {
                "scan_id": "llama_cpp_stub_scan",
                "findings": [{
                    "severity": "medium",
                    "type": "information_disclosure",
                    "description": "Potential information disclosure (stub)",
                    "recommendation": "Review security configurations"
                }],
                "summary": {
                    "total_issues": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 1,
                    "low": 0,
                    "info": 0
                },
                "timestamp": datetime.now().isoformat()
            },
            "generic": {
                "response": "This is a stub response from llama.cpp adapter",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        content = json.dumps(responses.get(response_type, responses["generic"]))
        
        return LLMResponse(
            content=content,
            model="llama-cpp-stub",
            provider="llama_cpp_stub",
            tokens_used=100,
            finish_reason="stop",
            metadata={"stub": True}
        )
    
    def is_available(self) -> bool:
        """Stub is always available."""
        return True