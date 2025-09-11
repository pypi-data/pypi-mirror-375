"""
Unified adapter interface for multiple LLM backends.
Supports LM Studio, Ollama, and llama.cpp.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    LM_STUDIO = "lm_studio"
    OLLAMA = "ollama"
    LLAMA_CPP = "llama_cpp"
    MOCK = "mock"  # For testing


def _provider_from_str(s: str) -> LLMProvider:
    """Convert string to LLMProvider enum."""
    s = (s or "").strip().lower().replace("-", "_")
    if s in ("lmstudio", "lm_studio"):
        return LLMProvider.LM_STUDIO
    if s in ("ollama",):
        return LLMProvider.OLLAMA
    if s in ("llama_cpp", "llamacpp", "llama.cpp"):
        return LLMProvider.LLAMA_CPP
    if s in ("mock",):
        return LLMProvider.MOCK
    raise ValueError(f"Unknown provider: {s}")


@dataclass
class LLMResponse:
    """Standard response from any LLM provider."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: LLMProvider
    model: str
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30
    extra_params: Optional[Dict[str, Any]] = None


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters."""
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the adapter with configuration.
        
        Args:
            config: LLM configuration
        """
        self.config = config
        self.provider = config.provider
        self.model = config.model
    
    @abstractmethod
    def query(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Send a query to the LLM and get a response.
        
        Args:
            prompt: The prompt to send
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM service is available.
        
        Returns:
            True if service is reachable
        """
        pass
    
    def format_for_json(self, prompt: str) -> str:
        """
        Format prompt to encourage JSON response.
        
        Args:
            prompt: Original prompt
            
        Returns:
            Formatted prompt
        """
        return f"{prompt}\n\nRespond with valid JSON only."


class MockLLMAdapter(LLMAdapter):
    """Mock adapter for testing without a real LLM."""
    
    def query(self, prompt: str, **kwargs) -> LLMResponse:
        """Return a mock response for testing."""
        import json
        from datetime import datetime
        
        # Simple mock response based on prompt content
        mock_response = {
            "test_id": "test_mock",
            "failure_type": "assertion_error",
            "root_cause": {
                "summary": "Mock test failure",
                "details": "This is a mock response for testing"
            },
            "fix_suggestions": [{
                "description": "Fix the mock issue",
                "code_changes": [{
                    "file": "mock.py",
                    "change_type": "modify"
                }],
                "priority": "high"
            }],
            "confidence_score": 0.95,
            "timestamp": datetime.now().isoformat()
        }
        
        return LLMResponse(
            content=json.dumps(mock_response),
            model="mock-model",
            provider="mock",
            tokens_used=100
        )
    
    def is_available(self) -> bool:
        """Mock adapter is always available."""
        return True


def create_adapter(config: LLMConfig) -> LLMAdapter:
    """
    Factory function to create the appropriate LLM adapter.
    
    Args:
        config: LLM configuration
        
    Returns:
        Configured LLM adapter instance
        
    Raises:
        ValueError: If provider is not supported
    """
    # Normalize provider (handle both strings and enums)
    if isinstance(config.provider, str):
        config.provider = _provider_from_str(config.provider)
    
    if config.provider == LLMProvider.MOCK:
        return MockLLMAdapter(config)
    
    # Import backend-specific adapters only when needed
    if config.provider == LLMProvider.LM_STUDIO:
        from .backends.lm_studio import LMStudioAdapter
        return LMStudioAdapter(config)
    
    elif config.provider == LLMProvider.OLLAMA:
        from .backends.ollama import OllamaAdapter
        return OllamaAdapter(config)
    
    elif config.provider == LLMProvider.LLAMA_CPP:
        from .backends.llama_cpp import LlamaCppAdapter
        return LlamaCppAdapter(config)
    
    else:
        raise ValueError(f"Unsupported LLM provider: {config.provider}")