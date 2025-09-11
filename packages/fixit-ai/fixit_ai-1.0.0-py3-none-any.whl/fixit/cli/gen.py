from __future__ import annotations
from rich import print
from fixit.core.config import read_config
from fixit.spec.loader import load_model
from fixit.gen.cases import build_test_plan
from fixit.gen.writer import write_tests
from fixit.core.paths import tests_dir

def run() -> None:
    cfg = read_config()
    if not cfg:
        raise SystemExit("Run 'fixit init' first.")
    spec_model, _ = load_model(cfg.spec_path)
    plan = build_test_plan(spec_model)
    out = tests_dir()
    count = write_tests(plan, out)
    print(f"[green]Generated[/green] {count} test(s) → {out}")