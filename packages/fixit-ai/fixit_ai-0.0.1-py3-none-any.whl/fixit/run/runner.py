from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import subprocess, sys, re
from typing import Union

@dataclass
class RunResult:
    exit_code: int
    passed: int
    failed: int
    total: int
    raw_output: str

def run_pytest(target: Union[Path, str]) -> RunResult:
    """Run pytest on a directory or specific file."""
    cmd = [sys.executable, "-m", "pytest", str(target), "-q", "--maxfail=0", "--disable-warnings"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stdout + "\n" + proc.stderr
    
    # More robust parsing for different pytest output formats
    passed = 0
    failed = 0
    
    # Try multiple patterns to handle different pytest output formats
    patterns = [
        r"(\d+)\s+passed.*?(\d+)\s+failed",  # "X passed, Y failed"
        r"(\d+)\s+failed.*?(\d+)\s+passed",  # "X failed, Y passed" 
        r"=+\s*(\d+)\s+passed.*?(\d+)\s+failed",  # With separators
        r"=+\s*(\d+)\s+failed.*?(\d+)\s+passed",  # With separators
    ]
    
    for pattern in patterns:
        m = re.search(pattern, out, re.DOTALL | re.IGNORECASE)
        if m:
            if "passed.*failed" in pattern:
                passed, failed = int(m.group(1)), int(m.group(2))
            else:
                failed, passed = int(m.group(1)), int(m.group(2))
            break
    
    # Fallback: parse individually if combined patterns fail
    if passed == 0 and failed == 0:
        passed_match = re.search(r"(\d+)\s+passed", out, re.IGNORECASE)
        failed_match = re.search(r"(\d+)\s+failed", out, re.IGNORECASE)
        
        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
    
    total = passed + failed
    return RunResult(proc.returncode, passed, failed, total, out)