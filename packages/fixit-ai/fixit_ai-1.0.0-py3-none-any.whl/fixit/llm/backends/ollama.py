"""
Ollama backend adapter implementation.
Ollama runs models locally and provides a REST API.
"""

import json
import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry  # ← Correct import

from ..adapter import LLMAdapter, LLMResponse, LLMConfig

logger = logging.getLogger(__name__)


class OllamaAdapter(LLMAdapter):
    """
    Adapter for Ollama local LLM server.
    Ollama provides a simple API for running LLMs locally.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize Ollama adapter.
        
        Args:
            config: LLM configuration
        """
        super().__init__(config)
        
        # Default Ollama URL if not provided
        self.base_url = config.api_url or "http://localhost:11434"
        self.generate_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.timeout = config.timeout
    
    def query(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Send a query to Ollama.
        
        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse object
            
        Raises:
            Exception: If the query fails
        """
        # Use chat endpoint for better structured responses
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes code and test failures. Always respond with valid JSON when requested."
                },
                {
                    "role": "user",
                    "content": self.format_for_json(prompt)
                }
            ],
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.config.temperature),
                "num_predict": kwargs.get("max_tokens", self.config.max_tokens),
            }
        }
        
        # Add any extra parameters
        if self.config.extra_params:
            payload["options"].update(self.config.extra_params)
        
        try:
            logger.debug(f"Sending request to Ollama at {self.chat_endpoint}")
            
            response = self.session.post(
                self.chat_endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract response from Ollama format
            content = data["message"]["content"]
            
            # Ollama provides different metrics
            total_duration = data.get("total_duration", 0)
            eval_count = data.get("eval_count", 0)
            
            logger.debug(f"Received response from Ollama (eval_count: {eval_count})")
            
            return LLMResponse(
                content=content,
                model=data.get("model", self.config.model),
                provider="ollama",
                tokens_used=eval_count,
                finish_reason="stop" if data.get("done") else "length",
                metadata={
                    "total_duration": total_duration,
                    "load_duration": data.get("load_duration"),
                    "prompt_eval_count": data.get("prompt_eval_count"),
                    "prompt_eval_duration": data.get("prompt_eval_duration"),
                    "eval_count": eval_count,
                    "eval_duration": data.get("eval_duration")
                }
            )
            
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            raise TimeoutError(f"Ollama request timed out after {self.timeout}s")
            
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Ollama at {self.base_url}: {e}")
            raise ConnectionError(f"Failed to connect to Ollama. Is it running? Try: ollama serve")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ValueError(f"Model '{self.config.model}' not found. Try: ollama pull {self.config.model}")
            logger.error(f"Ollama HTTP error: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Ollama query failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """
        Check if Ollama is running and the model is available.
        
        Returns:
            True if Ollama is reachable and model is available
        """
        try:
            # Check if Ollama is running
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if the specific model is available
            data = response.json()
            available_models = [model["name"] for model in data.get("models", [])]
            
            # Handle model names with/without tags (e.g., "llama2" vs "llama2:latest")
            model_name = self.config.model.split(":")[0]
            return any(model_name in available for available in available_models)
            
        except:
            return False
    
    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """
        Pull a model from Ollama registry.
        
        Args:
            model_name: Model to pull (defaults to configured model)
            
        Returns:
            True if successful
        """
        model = model_name or self.config.model
        try:
            logger.info(f"Pulling model {model} from Ollama...")
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True,
                timeout=None  # Pulling can take a while
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "status" in data:
                        logger.debug(data["status"])
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to pull model {model}: {e}")
            return False