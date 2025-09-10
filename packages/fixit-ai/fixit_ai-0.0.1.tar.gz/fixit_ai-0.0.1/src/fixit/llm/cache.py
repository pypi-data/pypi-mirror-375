from __future__ import annotations
import hashlib
import pickle
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class LLMCache:
    """
    Simple disk-based cache for LLM responses.
    - Root: <cwd>/.fixit/llm_cache
    - Filenames: SHA256(key).pkl (OS-safe)
    """
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_hours: int = 24,
        max_size_mb: int = 100
    ):
        self.cache_dir = cache_dir or (Path.cwd() / ".fixit" / "llm_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.memory_cache: Dict[str, Any] = {}

    def generate_key(self, key_str: str) -> str:
        """Return a hex digest for any raw key string."""
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def _path_for(self, hashed_key: str) -> Path:
        return self.cache_dir / f"{hashed_key}.pkl"

    def get(self, hashed_key: str) -> Optional[Dict[str, Any]]:
        if hashed_key in self.memory_cache:
            return self.memory_cache[hashed_key]
        p = self._path_for(hashed_key)
        if not p.exists():
            return None
        try:
            with p.open("rb") as f:
                obj = pickle.load(f)
            ts = datetime.fromisoformat(obj.get("timestamp"))
            if datetime.now() - ts > self.ttl:
                p.unlink(missing_ok=True)
                return None
            data = obj.get("response")
            self.memory_cache[hashed_key] = data
            return data
        except Exception as e:
            logger.warning(f"Failed to read cache file {p}: {e}")
            return None

    def set(self, hashed_key: str, response: Dict[str, Any]) -> None:
        """Store response under hashed key."""
        self.memory_cache[hashed_key] = response
        p = self._path_for(hashed_key)
        try:
            payload = {"timestamp": datetime.now().isoformat(), "response": response}
            with p.open("wb") as f:
                pickle.dump(payload, f)
            self._cleanup_if_needed()
        except Exception as e:
            logger.warning(f"Failed to cache response to {p}: {e}")

    def _cleanup_if_needed(self) -> None:
        total = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
        if total <= self.max_size_bytes:
            return
        files = sorted(self.cache_dir.glob("*.pkl"), key=lambda f: f.stat().st_mtime)
        while total > self.max_size_bytes and files:
            old = files.pop(0)
            size = old.stat().st_size
            old.unlink(missing_ok=True)
            total -= size

    def clear(self) -> None:
        self.memory_cache.clear()
        for f in self.cache_dir.glob("*.pkl"):
            f.unlink(missing_ok=True)