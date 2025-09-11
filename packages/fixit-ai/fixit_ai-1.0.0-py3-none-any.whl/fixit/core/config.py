from __future__ import annotations
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import tomllib

from .paths import ensure_workspace, config_path
from fixit.llm.adapter import LLMConfig, _provider_from_str

class Config(BaseModel):
    base_url: str
    spec_path: str
    llm_provider: str = "mock"  # mock | lmstudio | ollama | llama.cpp
    llm_url: str | None = None
    llm_model: str | None = None
    offline: bool = True

def read_config() -> Config | None:
    p = config_path()
    if not p.exists():
        return None
    return Config.model_validate_json(p.read_text())

def write_config(cfg: Config) -> None:
    ensure_workspace()
    p = config_path()
    p.write_text(cfg.model_dump_json(indent=2), encoding="utf-8")

def read_fixit_toml(project_root: Path | None = None) -> dict:
    pr = project_root or Path.cwd()
    p = pr / "fixit.toml"
    if not p.exists():
        return {}
    content = p.read_text(encoding="utf-8")
    # Remove BOM if present
    if content.startswith("\ufeff"):
        content = content[1:]
    return tomllib.loads(content)

def build_llm_config(project_root: Path | None = None) -> Optional[LLMConfig]:
    cfg = read_fixit_toml(project_root)
    if not cfg:
        # Return sensible defaults when fixit.toml is missing
        from fixit.llm.adapter import LLMProvider
        return LLMConfig(
            provider=LLMProvider.LM_STUDIO,
            model="gpt-oss 20B",
            api_url="http://localhost:1234/v1",
            api_key=None,
            temperature=0.0,
            max_tokens=2048,
            timeout=180,
            extra_params={},
        )

    active = cfg.get("llm_active", "llm")

    # Handle [llm] and nested [llm.<profile>]
    llm_root = cfg.get("llm", {}) or {}
    if active == "llm":
        section = llm_root
    else:
        section = llm_root.get(active, {}) or cfg.get(f"llm.{active}", {}) or llm_root

    provider_str = section.get("provider", "lmstudio")
    provider_enum = _provider_from_str(provider_str)

    model = str(section.get("model", "gpt-oss 20B"))
    api_url = str(section.get("base_url", "http://localhost:1234/v1"))
    try:
        temperature = float(section.get("temperature", 0.0))
    except Exception:
        temperature = 0.0
    try:
        max_tokens = int(section.get("max_tokens", 2048))
    except Exception:
        max_tokens = 2048
    # Accept either timeout_seconds or timeout
    try:
        timeout = int(section.get("timeout_seconds", section.get("timeout", 180)))
    except Exception:
        timeout = 180

    api_key_env = section.get("api_key_env")
    api_key = None
    if api_key_env:
        import os
        api_key = os.getenv(api_key_env)

    return LLMConfig(
        provider=provider_enum,
        model=model,
        api_url=api_url,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        extra_params={},
    )