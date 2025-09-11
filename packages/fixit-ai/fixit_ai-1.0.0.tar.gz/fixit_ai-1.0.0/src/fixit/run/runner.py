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
    
    # Enhanced parsing for all pytest output scenarios
    passed = 0
    failed = 0
    
    # Handle different pytest output formats more robustly
    patterns = [
        # Standard formats
        r"(\d+)\s+passed.*?(\d+)\s+failed",     # "X passed, Y failed"
        r"(\d+)\s+failed.*?(\d+)\s+passed",     # "X failed, Y passed"
        
        # With separators
        r"=+\s*(\d+)\s+passed.*?(\d+)\s+failed", # "==== X passed, Y failed ===="
        r"=+\s*(\d+)\s+failed.*?(\d+)\s+passed", # "==== X failed, Y passed ===="
        
        # Short formats
        r"(\d+)\s+passed,\s*(\d+)\s+failed",    # "X passed, Y failed"
        r"(\d+)\s+failed,\s*(\d+)\s+passed",    # "X failed, Y passed"
        
        # In summary lines
        r"=+.*?(\d+)\s+passed.*?(\d+)\s+failed.*?=+",  # "=== X passed, Y failed ==="
        r"=+.*?(\d+)\s+failed.*?(\d+)\s+passed.*?=+",  # "=== X failed, Y passed ==="
    ]
    
    # Try to match combined patterns first
    for pattern in patterns:
        m = re.search(pattern, out, re.DOTALL | re.IGNORECASE)
        if m:
            if "passed.*failed" in pattern:
                passed, failed = int(m.group(1)), int(m.group(2))
            else:
                failed, passed = int(m.group(1)), int(m.group(2))
            break
    
    # Enhanced fallback: parse individual counts with multiple patterns
    if passed == 0 and failed == 0:
        # Try to find passed count
        passed_patterns = [
            r"(\d+)\s+passed",           # "X passed"
            r"=+.*?(\d+)\s+passed",      # "=== X passed"
            r"(\d+)\s+test[s]?\s+passed" # "X tests passed"
        ]
        for pattern in passed_patterns:
            m = re.search(pattern, out, re.IGNORECASE)
            if m:
                passed = int(m.group(1))
                break
        
        # Try to find failed count
        failed_patterns = [
            r"(\d+)\s+failed",           # "X failed"
            r"=+.*?(\d+)\s+failed",      # "=== X failed"
            r"(\d+)\s+test[s]?\s+failed" # "X tests failed"
        ]
        for pattern in failed_patterns:
            m = re.search(pattern, out, re.IGNORECASE)
            if m:
                failed = int(m.group(1))
                break
    
    # Handle special cases
    if passed == 0 and failed == 0:
        # Check for "no tests ran" or "no tests collected"
        if re.search(r"no\s+tests?\s+(ran|collected)", out, re.IGNORECASE):
            passed = failed = 0
        # Check for specific patterns like "collected 0 items"
        elif re.search(r"collected\s+0\s+items", out, re.IGNORECASE):
            passed = failed = 0
        # Check for "0 passed"
        elif re.search(r"0\s+passed", out, re.IGNORECASE):
            passed = 0
        # If we see test execution but no counts, try to count from test names
        elif "PASSED" in out or "FAILED" in out:
            passed = len(re.findall(r"PASSED", out))
            failed = len(re.findall(r"FAILED", out))
    
    total = passed + failed
    
    # Final validation: ensure counts make sense
    if total == 0 and ("test" in out.lower() or "collected" in out.lower()):
        # If pytest output mentions tests but we found 0, there might be a parsing issue
        # Look for collected items as a backup
        collected_match = re.search(r"collected\s+(\d+)\s+items?", out, re.IGNORECASE)
        if collected_match:
            total = int(collected_match.group(1))
            # If we know total but not breakdown, assume all passed if exit_code == 0
            if passed == 0 and failed == 0:
                if proc.returncode == 0:
                    passed = total
                else:
                    failed = total
    
    return RunResult(proc.returncode, passed, failed, total, out)