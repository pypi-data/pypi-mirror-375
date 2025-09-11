from __future__ import annotations
import json
import tempfile
from pathlib import Path
from typing import Optional
from rich import print
from fixit.core.config import Config, write_config
from fixit.core.paths import ensure_workspace
from fixit.spec.loader import load as load_spec, normalize_spec_dict
from fixit.spec.validator import validate_spec_model as validate_openapi, validate_spec_dict
from fixit.spec.autodiscover import try_fetch_known_spec
from fixit.spec.from_fastapi import extract_openapi as extract_fastapi_openapi
from fixit.spec.from_express import extract_express_routes


def run(
    spec: Optional[str] = None, 
    base: str = "http://localhost:8000",
    fastapi: Optional[str] = None,
    express: Optional[str] = None,
    autodiscover: bool = False,
    llm_provider: str = "lmstudio",
    llm_url: str = "http://localhost:1234/v1", 
    llm_model: str = "gpt-oss 20B"
) -> None:
    """
    Initialize Fixit with OpenAPI spec.
    
    Args:
        spec: Path to OpenAPI YAML/JSON file (traditional mode)
        base: Base URL for the API
        fastapi: Python module path to FastAPI app (e.g., 'main:app')
        express: Path to Express.js project directory
        autodiscover: Try to fetch OpenAPI spec from common endpoints
        llm_provider: LLM provider to use (lmstudio, ollama, llama_cpp)
        llm_url: LLM API URL
        llm_model: LLM model name
    """
    ensure_workspace()
    
    # Validate mutually exclusive options
    options_count = sum(bool(x) for x in [spec, fastapi, express, autodiscover])
    if options_count > 1:
        raise SystemExit(
            "[red]❌ Error: Only one of --spec, --fastapi, --express, or --autodiscover can be used at a time[/red]"
        )
    
    # Zero-YAML modes
    if autodiscover:
        print(f"[blue]🔍 Auto-discovering OpenAPI spec from {base}...[/blue]")
        spec_dict = try_fetch_known_spec(base)
        if spec_dict:
            print(f"[green]✅ Found OpenAPI spec at {base}[/green]")
            workspace = Path.cwd() / '.fixit'
            workspace.mkdir(exist_ok=True)
            
            # Write generated spec
            generated_path = workspace / 'openapi.generated.json'
            with open(generated_path, 'w', encoding='utf-8') as f:
                json.dump(spec_dict, f, indent=2)
            print(f"[dim]📄 Created {generated_path}[/dim]")
            
            # Normalize spec
            normalized_path = normalize_spec_dict(spec_dict, workspace / 'openapi.normalized.json')
            print(f"[dim]📋 Created {normalized_path}[/dim]")
            
            temp_spec_path = str(normalized_path)
        else:
            raise SystemExit(f"[red]❌ No OpenAPI spec found at {base}[/red]\nTried common endpoints like /openapi.json, /docs/openapi.json")
    
    elif fastapi:
        print(f"[blue]🐍 Extracting OpenAPI spec from FastAPI app: {fastapi}...[/blue]")
        try:
            spec_dict = extract_fastapi_openapi(fastapi)
            if spec_dict:
                print(f"[green]✅ Extracted OpenAPI spec from FastAPI app[/green]")
                workspace = Path.cwd() / '.fixit'
                workspace.mkdir(exist_ok=True)
                
                # Write generated spec
                generated_path = workspace / 'openapi.generated.json'
                with open(generated_path, 'w', encoding='utf-8') as f:
                    json.dump(spec_dict, f, indent=2)
                print(f"[dim]📄 Created {generated_path}[/dim]")
                
                # Normalize spec  
                normalized_path = normalize_spec_dict(spec_dict, workspace / 'openapi.normalized.json')
                print(f"[dim]📋 Created {normalized_path}[/dim]")
                
                temp_spec_path = str(normalized_path)
            else:
                raise SystemExit(f"[red]❌ Failed to extract OpenAPI spec from FastAPI app: {fastapi}[/red]")
        except Exception as e:
            raise SystemExit(f"[red]❌ Error extracting FastAPI spec: {e}[/red]")
    
    elif express:
        print(f"[blue]🟨 Extracting routes from Express.js app: {express}...[/blue]")
        try:
            spec_dict = extract_express_routes(express)
            if spec_dict:
                print(f"[green]✅ Generated OpenAPI spec from Express.js routes[/green]")
                workspace = Path.cwd() / '.fixit'
                workspace.mkdir(exist_ok=True)
                
                # Write generated spec
                generated_path = workspace / 'openapi.generated.json'
                with open(generated_path, 'w', encoding='utf-8') as f:
                    json.dump(spec_dict, f, indent=2)
                print(f"[dim]📄 Created {generated_path}[/dim]")
                
                # Normalize spec
                normalized_path = normalize_spec_dict(spec_dict, workspace / 'openapi.normalized.json')
                print(f"[dim]📋 Created {normalized_path}[/dim]")
                
                temp_spec_path = str(normalized_path)
            else:
                raise SystemExit(f"[red]❌ Failed to extract routes from Express.js app: {express}[/red]")
        except Exception as e:
            raise SystemExit(f"[red]❌ Error extracting Express.js routes: {e}[/red]")
    
    elif spec:
        # Traditional mode - OpenAPI YAML/JSON file
        print(f"[blue]📄 Loading OpenAPI spec from file: {spec}...[/blue]")
        spec_path = Path(spec).resolve()
        if not spec_path.exists():
            raise SystemExit(f"[red]Spec not found:[/red] {spec_path}")
        temp_spec_path = str(spec_path)
    
    else:
        raise SystemExit(
            "[red]❌ No spec source provided[/red]\n\n"
            "Choose one of:\n"
            "• [yellow]--spec[/yellow] path/to/openapi.yaml  [dim](traditional mode)[/dim]\n"
            "• [yellow]--fastapi[/yellow] main:app  [dim](extract from FastAPI)[/dim]\n"
            "• [yellow]--express[/yellow] ./my-app  [dim](extract from Express.js)[/dim]\n"
            "• [yellow]--autodiscover[/yellow]  [dim](fetch from running server)[/dim]"
        )
    
    # Load and validate the spec (for traditional mode only)
    if spec:
        raw, normalized_path = load_spec(temp_spec_path)
        # Validate the spec - raw is always a SpecModel from load_spec
        validate_openapi(raw)
    else:
        # For code-first modes, we already normalized above
        raw, normalized_path = load_spec(temp_spec_path)
        validate_openapi(raw)
    
    # Auto-create fixit.toml if missing
    _ensure_fixit_toml_if_missing(base, llm_provider, llm_url, llm_model)
    
    # Write config
    write_config(Config(base_url=base, spec_path=temp_spec_path))
    
    print(f"[green]✅ Initialized Fixit[/green] • base={base}")
    print(f"📋 Normalized spec: {normalized_path}")
    
    # Show what we found - access SpecModel attributes directly
    title = raw.info.title if raw.info else 'API'
    version = raw.info.version if raw.info else 'unknown'
    paths_count = len(raw.paths) if raw.paths else 0
    
    print(f"[dim]API: {title} v{version} ({paths_count} paths)[/dim]")


def _ensure_fixit_toml_if_missing(base_url: str, provider: str, llm_url: str, llm_model: str) -> None:
    """
    If fixit.toml is missing at project root, create it with defaults.
    """
    toml_path = Path.cwd() / "fixit.toml"
    if toml_path.exists():
        print(f"[dim]📄 fixit.toml already exists, skipping creation[/dim]")
        return
    
    # Create default fixit.toml content
    toml_content = f'''llm_active = "llm"
openapi = "openapi.yaml"

[llm]
provider = "{provider}"
# base_url = "http://localhost:11434/v1" # Ollama
base_url = "{llm_url}"    # LM Studio
model = "{llm_model}"
temperature = 0.0
max_tokens = 2048
timeout_seconds = 180
offline = true
api_key_env = "FIXIT_API_KEY"

[llm.demo]
provider = "llama.cpp-stub"

[test]
include = []
exclude = []
max_tests = 0
concurrency = 8
'''
    
    toml_path.write_text(toml_content, encoding='utf-8')
    print(f"[green]📄 Created fixit.toml[/green] with provider={provider}, model={llm_model}")


def _save_temp_spec(spec_dict: dict) -> str:
    """Save OpenAPI spec dict to a temporary JSON file."""
    
    # Create a temp file in the workspace
    workspace = Path.cwd() / '.fixit'
    workspace.mkdir(exist_ok=True)
    
    temp_path = workspace / 'extracted_openapi.json'
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(spec_dict, f, indent=2)
    
    return str(temp_path)