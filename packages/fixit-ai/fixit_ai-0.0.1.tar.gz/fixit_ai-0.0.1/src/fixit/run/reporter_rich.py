from __future__ import annotations
from rich.console import Console
from rich.panel import Panel
from .runner import RunResult

def print_summary(res: RunResult) -> None:
    console = Console()
    status = "green" if res.exit_code == 0 else "red"
    msg = f"Tests: passed={res.passed} failed={res.failed} total={res.total}"
    console.print(Panel.fit(msg, title=f"[{status}]fixit test[/]", border_style=status))