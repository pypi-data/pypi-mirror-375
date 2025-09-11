from __future__ import annotations
import typer
from . import init as init_cmd, gen as gen_cmd, test as test_cmd, sec as sec_cmd, fix as fix_cmd
from .sec import cli_auth  # Typer sub-app for auth commands

app = typer.Typer(help="Fixit: Offline API Test Agent (OpenAPI-first)")

@app.command("init")
def init(
    spec: str = typer.Option(None, "--spec", help="Path to openapi.yaml/json (traditional mode)"),
    base: str = typer.Option("http://localhost:8000", "--base", help="Base URL of API server"),
    fastapi: str = typer.Option(None, "--fastapi", help="FastAPI app module path (e.g., 'main:app')"),
    express: str = typer.Option(None, "--express", help="Express.js project directory path"),
    autodiscover: bool = typer.Option(False, "--autodiscover", help="Auto-discover OpenAPI spec from server"),
    llm_provider: str = typer.Option("lmstudio", "--llm-provider", help="LLM provider (lmstudio, ollama, llama_cpp)"),
    llm_url: str = typer.Option("http://localhost:1234/v1", "--llm-url", help="LLM API URL"),
    llm_model: str = typer.Option("gpt-oss 20B", "--llm-model", help="LLM model name"),
):
    """
    Initialize Fixit with OpenAPI spec using zero-YAML onboarding.
    
    Examples:
        fixit init --spec openapi.yaml --base http://localhost:8000
        fixit init --fastapi main:app --base http://localhost:8000  
        fixit init --express ./my-express-app --base http://localhost:3000
        fixit init --autodiscover --base http://localhost:8000
        fixit init --fastapi main:app --base http://localhost:8000 --llm-provider ollama --llm-model phi3:mini
    """
    init_cmd.run(
        spec=spec, 
        base=base, 
        fastapi=fastapi, 
        express=express, 
        autodiscover=autodiscover,
        llm_provider=llm_provider,
        llm_url=llm_url,
        llm_model=llm_model
    )

@app.command("gen")
def gen():
    gen_cmd.run()

@app.command("test")
def test(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed LLM analysis"),
    show_cached: bool = typer.Option(False, "--show-cached", help="Show both new and cached analysis"),
):
    """
    Run tests and analyze failures with AI.
    
    Examples:
        fixit test                    # Show only new analysis  
        fixit test --show-cached      # Show all analysis (new + cached)
        fixit test --verbose          # Detailed LLM output
    """
    test_cmd.run(verbose, show_cached)

@app.command("sec")
def sec():
    # Runs your security checks (sec.py: run())
    sec_cmd.run()

@app.command("fix")
def fix(
    apply: bool = typer.Option(False, "--apply", help="DANGEROUS: Auto-apply patches (requires confirmation)"),
):
    """
    Show AI-generated code suggestions (safe by default).
    
    By default, this shows suggestions only. Use --apply for dangerous auto-patching.
    
    Examples:
        fixit fix                    # Show suggestions (safe)
        fixit fix --apply           # Auto-apply patches (dangerous)
    """
    fix_cmd.run(apply)

# Mount auth subcommands (set/show/clear) under 'auth' only
app.add_typer(cli_auth, name="auth")

def main():
    app()