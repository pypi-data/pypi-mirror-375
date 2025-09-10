from __future__ import annotations
from rich import print
from fixit.core.config import read_config
from fixit.spec.loader import load_as_dict  # use dict-returning loader
from fixit.sec.checks import run_checks

# --- Auth additions ---
import json
from pathlib import Path
import typer

def run() -> None:
    cfg = read_config()
    if not cfg:
        raise SystemExit("Run 'fixit init' first.")
    spec_dict, _ = load_as_dict(cfg.spec_path)  # always pass a dict to checks
    findings = run_checks(cfg, spec_dict)
    if not findings:
        print("[green]Security quick pass: no findings[/green]")
        return
    print("[yellow]Security findings:[/yellow]")
    for f in findings:
        sev = f.get("severity", "info").upper()
        eid = f.get("id", "FINDING")
        msg = f.get("message", "")
        print(f" - [{sev}] {eid}: {msg}")

# Typer sub-app for auth management (so main.py can mount it as `fixit auth`)
cli_auth = typer.Typer(help="Auth management")

def _repo_root(start: Path | None = None) -> Path:
    start = start or Path.cwd()
    for d in [start, *start.parents]:
        if (d / "pyproject.toml").exists() or (d / "fixit.toml").exists() or (d / ".git").exists():
            return d
    return start

def _auth_file() -> Path:
    d = _repo_root() / ".fixit"
    d.mkdir(parents=True, exist_ok=True)
    return d / "auth.json"

@cli_auth.command("set")
def set_credentials(
    jwt: str | None = typer.Option(None, "--jwt", help="Bearer JWT token for protected endpoints"),
    api_key: str | None = typer.Option(None, "--api-key", help="API key for your LLM server"),
):
    auth_path = _auth_file()
    current = {}
    if auth_path.exists():
        try:
            current = json.loads(auth_path.read_text())
        except Exception:
            current = {}
    if jwt is not None:
        current["jwt"] = jwt
    if api_key is not None:
        current["api_key"] = api_key
    auth_path.write_text(json.dumps(current, indent=2))
    print(f"[green]Saved credentials to {auth_path}[/green]")

@cli_auth.command("show")
def show_credentials():
    auth_path = _auth_file()
    if not auth_path.exists():
        print("[yellow]No credentials saved yet.[/yellow]")
        raise typer.Exit(0)
    try:
        data = json.loads(auth_path.read_text())
    except Exception:
        print("[red]Could not read credentials file.[/red]")
        raise typer.Exit(1)
    masked = dict(data)
    if "api_key" in masked and masked["api_key"]:
        masked["api_key"] = masked["api_key"][:6] + "..." + masked["api_key"][-4:]
    if "jwt" in masked and masked["jwt"]:
        masked["jwt"] = masked["jwt"][:12] + "...(hidden)"
    print(masked)

@cli_auth.command("clear")
def clear_credentials():
    auth_path = _auth_file()
    if auth_path.exists():
        auth_path.unlink()
        print("[green]Cleared credentials.[/green]")
    else:
        print("[yellow]No credentials to clear.[/yellow]")

if __name__ == "__main__":
    run()