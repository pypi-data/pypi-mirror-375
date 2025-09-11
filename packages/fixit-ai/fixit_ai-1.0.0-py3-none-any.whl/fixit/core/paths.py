from __future__ import annotations
from pathlib import Path

WORKSPACE_NAME = ".fixit"

def workspace_dir() -> Path:
    return Path.cwd() / WORKSPACE_NAME

def ensure_workspace() -> Path:
    ws = workspace_dir()
    (ws / "tests").mkdir(parents=True, exist_ok=True)
    (ws / "reports").mkdir(parents=True, exist_ok=True)
    (ws / "cache").mkdir(parents=True, exist_ok=True)
    return ws

def config_path() -> Path:
    return workspace_dir() / "config.json"

def normalized_spec_path() -> Path:
    return workspace_dir() / "openapi.normalized.json"

def tests_dir() -> Path:
    return workspace_dir() / "tests"

def reports_dir() -> Path:
    return workspace_dir() / "reports"

def cache_dir() -> Path:
    return workspace_dir() / "cache"