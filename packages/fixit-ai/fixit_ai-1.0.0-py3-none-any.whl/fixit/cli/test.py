from __future__ import annotations
import json
import os
from pathlib import Path
from rich import print
from fixit.core.paths import tests_dir, reports_dir
from fixit.run.runner import run_pytest
from fixit.run.reporter_rich import print_summary
from fixit.run.reporter_html import write_html_report
from fixit.llm.adapter import create_adapter
from fixit.core.config import build_llm_config
from fixit.explain.advisor import Advisor
from fixit.llm.cache import LLMCache
import hashlib

def _load_failures() -> list[dict]:
    p = reports_dir() / "failures.jsonl"
    if not p.exists():
        return []
    
    # Get unique failures only (deduplicate by test_id/endpoint_id)
    seen_ids = set()
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            failure = json.loads(line)
            test_id = failure.get("test_id") or failure.get("endpoint_id")
            if test_id not in seen_ids:
                seen_ids.add(test_id)
                out.append(failure)
        except Exception:
            continue
    return out

def _get_project_context() -> str:
    """Get project context for test isolation."""
    try:
        from fixit.core.config import get_config
        cfg = get_config()
        
        # Build project context
        base_url = getattr(cfg, 'base_url', 'http://localhost:8000')
        spec_path = getattr(cfg, 'spec_path', '')
        
        # Create project identifier 
        project_context = f"{base_url}|{spec_path}"
        return hashlib.sha256(project_context.encode()).hexdigest()[:8]
    except Exception:
        return "default"

def _get_current_spec_hash() -> str:
    """Get the spec hash for the current project."""
    try:
        from fixit.core.config import get_config
        from fixit.spec.loader import load_model
        
        cfg = get_config()
        if not cfg or not cfg.spec_path:
            return ""
        
        # Load the spec and compute its hash (same as TestPlanGenerator)
        spec_model, _ = load_model(cfg.spec_path)
        from fixit.spec.loader import normalize_spec_to_json
        spec_json = normalize_spec_to_json(spec_model)
        return hashlib.sha256(spec_json.encode('utf-8')).hexdigest()[:8]
    except Exception:
        return ""

def _get_project_test_file() -> Path | None:
    """Get the test file specific to current project."""
    tests_root = tests_dir()
    if not tests_root.exists():
        return None
    
    current_spec_hash = _get_current_spec_hash()
    if not current_spec_hash:
        # Fallback: return the most recent test file
        test_files = list(tests_root.glob("test_*.py"))
        if test_files:
            return max(test_files, key=lambda f: f.stat().st_mtime)
        return None
    
    # Look for test file with our current spec hash
    for test_file in tests_root.glob("test_*.py"):
        if current_spec_hash in test_file.name:
            return test_file
    
    # If no exact match, try fallback
    test_files = list(tests_root.glob("test_*.py"))
    if test_files:
        return max(test_files, key=lambda f: f.stat().st_mtime)
    
    return None

def _display_single_advice(adv_dict: dict, prefix: str) -> None:
    """Display a single advice entry immediately."""
    test_id = adv_dict.get("test_id", "unknown")
    
    # Extract root cause information
    root_cause = adv_dict.get("root_cause") or {}
    summary = root_cause.get("summary", "")
    details = root_cause.get("details", "")
    
    failure_type = adv_dict.get("failure_type", "unknown")
    conf = adv_dict.get("confidence_score", "-")

    # Clean, structured output
    print(f"\n{prefix} {test_id}")
    print(f"    Type: {failure_type.replace('_', ' ').title()}")
    print(f"    Confidence: {conf}")
    print(f"    Issue: {summary}")
    if details and details != summary:
        print(f"    Details: {details}")


def run(verbose: bool = False, show_cached: bool = False) -> None:
    # Set environment variable for LLM debug output
    if verbose:
        os.environ["FIXIT_LLM_VERBOSE"] = "1"
    else:
        os.environ.pop("FIXIT_LLM_VERBOSE", None)
    
    # Clear previous failures to only analyze current test run
    failures_file = reports_dir() / "failures.jsonl"
    if failures_file.exists():
        failures_file.unlink()
    
    # Project-specific test execution
    project_test_file = _get_project_test_file()
    if project_test_file and project_test_file.exists():
        res = run_pytest(project_test_file)
    else:
        res = run_pytest(tests_dir())
    
    print_summary(res)
    write_html_report(res)

    # LLM advice with enhanced display logic
    failures = _load_failures()
    if failures:
        llm_cfg = build_llm_config()
        if llm_cfg:
            adapter = create_adapter(llm_cfg)
            advisor = Advisor(llm_adapter=adapter, cache=LLMCache())
            
            # Real-time LLM analysis with immediate display
            fresh_count = 0
            cached_count = 0
            all_advices = []

            print("\n" + "="*50)
            print("🔍 LLM Analysis")
            print("="*50)

            # Process failures one by one with real-time display
            for i, f in enumerate(failures, 1):
                test_id = f.get("test_id", "unknown")
                print(f"\n[{i}/{len(failures)}] Analyzing {test_id}...", end=" ", flush=True)
                
                advice = advisor.explain_failure(f)

                # Serialize Pydantic → JSON dict
                adv_dict = json.loads(
                    advice.model_dump_json(by_alias=True, exclude_none=True)
                )
                all_advices.append(adv_dict)
                
                # Immediate display based on cache status
                if getattr(advice, 'is_cached', False):
                    cached_count += 1
                    if show_cached:
                        print("💾 (cached)")
                        _display_single_advice(adv_dict, f"💾 [{i}]")
                    else:
                        print("💾 (cached)")
                else:
                    fresh_count += 1
                    print("🆕 (fresh)")
                    _display_single_advice(adv_dict, f"🆕 [{i}]")

            # Summary and next steps
            if fresh_count > 0 or show_cached:
                print(f"\n💡 Run 'fixit fix' to see suggested solutions")
                print("📊 Full analysis saved to .fixit/reports/advice.json")
                print("🌐 HTML report: .fixit/reports/index.html")

            # Cache status summary
            if not show_cached and cached_count > 0:
                print(f"\n💾 {cached_count} cached analysis available")
                print("💡 Run 'fixit test --show-cached' to see all results")
            
            if fresh_count == 0 and cached_count > 0 and not show_cached:
                print("💡 No new failures detected.")

        else:
            # No LLM configured
            print("\n[yellow]No LLM configured. Run with --verbose to see test details.[/yellow]")

        # Save advice to JSON for fix command
        if failures and 'all_advices' in locals():
            advice_path = reports_dir() / "advice.json"
            advice_path.parent.mkdir(parents=True, exist_ok=True)
            advice_path.write_text(json.dumps(all_advices, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            print("\n⚠️  LLM config not found; skipping explanations.")
    else:
        print("\n✅ No test failures found!")

    raise SystemExit(res.exit_code)