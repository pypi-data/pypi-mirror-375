from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import re
import difflib
import shutil
from rich import print
from rich.prompt import Prompt
from rich.table import Table
from rich.console import Console
from fixit.explain.patches import compose_fastapi_patches_for_example

console = Console()

def _clear_stale_cache_and_advice():
    """Clear potentially stale LLM cache and advice when applying patches."""
    from fixit.core.paths import reports_dir
    
    cache_dir = Path.cwd() / ".fixit" / "llm_cache"
    advice_file = reports_dir() / "advice.json"
    
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print("[yellow]🧹 Cleared LLM cache to ensure fresh analysis[/yellow]")
    
    if advice_file.exists():
        advice_file.unlink()
        print("[yellow]🧹 Cleared stale advice.json[/yellow]")

def _normalize_line(line: str) -> str:
    """Normalize line for fuzzy matching - remove extra whitespace."""
    return line.strip().replace('\t', '    ')

def _apply_unified_diff_to_text_fuzzy(orig: str, diff_text: str) -> Tuple[Optional[str], str]:
    """Apply unified diff with ULTRA CONSERVATIVE fuzzy matching. Returns (result, error_msg)."""
    try:
        lines = diff_text.splitlines(keepends=True)
        i = 0
        while i < len(lines) and not lines[i].startswith("@@"):
            i += 1
        if i >= len(lines):
            return None, "No @@ header found in diff"
        
        hunks = []
        header_re = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
        
        while i < len(lines):
            m = header_re.match(lines[i])
            if not m:
                i += 1
                continue
            
            old_start = int(m.group(1))
            old_len = int(m.group(2) or "1")
            new_start = int(m.group(3))
            new_len = int(m.group(4) or "1")
            i += 1
            
            hunk = []
            while i < len(lines) and not lines[i].startswith("@@"):
                if lines[i].startswith(("---", "+++")):
                    i += 1
                    continue
                if lines[i].strip() == "":
                    i += 1
                    continue
                    
                tag = lines[i][0]
                content = lines[i][1:]
                if tag in (" ", "+", "-"):
                    hunk.append((tag, content))
                i += 1
            
            hunks.append((old_start, old_len, new_start, new_len, hunk))
        
        src = orig.splitlines(keepends=True)
        out: List[str] = []
        ptr = 1
        
        for hunk_idx, (old_start, old_len, new_start, new_len, hunk) in enumerate(hunks):
            # Copy lines before this hunk
            while ptr < old_start and (ptr - 1) < len(src):
                out.append(src[ptr - 1])
                ptr += 1
            
            # ULTRA CONSERVATIVE: Try exact match first
            exact_match = True
            for i, (tag, content) in enumerate(hunk):
                if tag == " " or tag == "-":
                    expected_line_idx = old_start - 1 + i
                    if (expected_line_idx >= len(src) or 
                        src[expected_line_idx].rstrip() != content.rstrip()):
                        exact_match = False
                        break
            
            if not exact_match:
                # Try ULTRA conservative fuzzy matching (99% similarity required)
                fuzzy_match = False
                search_window = 2  # Only look 2 lines up/down
                
                for offset in range(-search_window, search_window + 1):
                    adjusted_start = old_start + offset
                    if adjusted_start < 1:
                        continue
                    
                    temp_match = True
                    similarity_sum = 0
                    similarity_count = 0
                    
                    for i, (tag, content) in enumerate(hunk):
                        if tag == " " or tag == "-":
                            test_line_idx = adjusted_start - 1 + i
                            if test_line_idx >= len(src):
                                temp_match = False
                                break
                            
                            similarity = difflib.SequenceMatcher(None, 
                                src[test_line_idx].strip(), 
                                content.strip()).ratio()
                            similarity_sum += similarity
                            similarity_count += 1
                            
                            if similarity < 0.99:  # 99% similarity required per line
                                temp_match = False
                                break
                    
                    # Require overall 99% similarity
                    if temp_match and similarity_count > 0:
                        avg_similarity = similarity_sum / similarity_count
                        if avg_similarity >= 0.99:
                            ptr = adjusted_start
                            fuzzy_match = True
                            print(f"[dim]   Fuzzy match found with {avg_similarity:.1%} similarity[/dim]")
                            break
                
                if not fuzzy_match:
                    return None, f"Hunk {hunk_idx + 1}: Cannot find context match (requires 99% similarity)"
            
            # Apply changes ultra conservatively
            try:
                for tag, content in hunk:
                    if tag == " ":
                        # Context line - should match
                        if ptr <= len(src):
                            out.append(content)
                            ptr += 1
                    elif tag == "-":
                        # Remove line - skip it
                        if ptr <= len(src):
                            ptr += 1
                    elif tag == "+":
                        # Add line
                        out.append(content)
                        
            except Exception as e:
                return None, f"Hunk {hunk_idx + 1} failed: {str(e)}"
        
        # Copy remaining lines
        while (ptr - 1) < len(src):
            out.append(src[ptr - 1])
            ptr += 1
        
        return "".join(out), ""
        
    except Exception as e:
        return None, f"Diff parsing failed: {str(e)}"

def _apply_unified_diff_file(file_path: Path, diff_text: str, patch_title: str) -> bool:
    if not file_path.exists():
        print(f"[red]File not found:[/red] {file_path}")
        return False
    
    orig = file_path.read_text(encoding="utf-8")
    result, error_msg = _apply_unified_diff_to_text_fuzzy(orig, diff_text)
    
    if result is None:
        print(f"[red]✗ Failed to apply patch:[/red] {error_msg}")
        print(f"[dim]  Patch: {patch_title}[/dim]")
        print(f"[dim]  File: {file_path}[/dim]")
        print(f"[yellow]💡 This may indicate the patch was generated for different code[/yellow]")
        return False
    
    # Backup original file  
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    backup_path.write_text(orig, encoding="utf-8")
    
    # Write patched content
    file_path.write_text(result, encoding="utf-8")
    print(f"[green]✓ Applied patch:[/green] {patch_title}")
    print(f"[dim]  File: {file_path} (backup: {backup_path.name})[/dim]")
    return True

def _load_advice() -> list[dict]:
    from fixit.core.paths import reports_dir
    p = reports_dir() / "advice.json"
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []

def _analyze_patch_quality(patches: List[dict]) -> None:
    """Analyze and report on patch quality and potential issues."""
    if not patches:
        return
        
    print("\n[bold]🔍 Patch Analysis:[/bold]")

def run(apply: bool = False, suggestions_only: bool = None) -> None:
    """
    Show code patches from LLM analysis.
    
    Args:
        apply: REMOVED - No longer supported
        suggestions_only: Show suggestions only (always True now)
    """
    if apply:
        print("[yellow]⚠️  --apply has been removed. fixit fix now shows suggestions only.[/yellow]")
    
    project_root = Path.cwd()

    # Always show suggestions only for safety
    suggestions_only = True
    
    # 1) LLM patches (from advice.json)
    advice_list = _load_advice()
    llm_patches: list[dict] = []
    if advice_list:
        for a in advice_list:
            cps = a.get("code_patches") or []
            for cp in cps:
                file = cp.get("file", "?")
                diff = cp.get("diff", "")
                llm_patches.append({
                    "file": file, 
                    "diff": diff, 
                    "title": f"Fix: {a.get('root_cause', {}).get('summary', 'Unknown issue')}"
                })

    # 2) Deterministic FastAPI patches (only for FastAPI projects)
    det_patches = []
    
    # More flexible FastAPI detection
    fastapi_indicators = [
        project_root / "main.py",
        project_root / "app.py",
        project_root / "src" / "main.py", 
        project_root / "src" / "app.py",
        project_root / "app" / "main.py",
        project_root / "api" / "main.py",
        project_root / "backend" / "main.py"
    ]
    
    # Check if any FastAPI indicator files exist
    fastapi_detected = any(f.exists() for f in fastapi_indicators)
    
    if not fastapi_detected:
        # Scan for FastAPI imports as fallback
        for py_file in project_root.rglob("*.py"):
            try:
                if py_file.is_file() and "fastapi" in py_file.read_text(encoding="utf-8", errors="ignore").lower():
                    fastapi_detected = True
                    break
            except (OSError, PermissionError):
                continue
    
    if fastapi_detected:
        # Only apply FastAPI patches if we detect FastAPI files
        det_patches = compose_fastapi_patches_for_example(project_root)
        det_patches = [p for p in det_patches if "note" not in p]

    if not llm_patches and not det_patches:
        print("[green]No patches available. Run 'fixit test --verbose' first to identify issues.[/green]")
        return

    if suggestions_only or not apply:
        # SUGGESTIONS MODE - Show patches with clear visibility (DEFAULT)
        _analyze_patch_quality(llm_patches)
        
        if llm_patches:
            print(f"\n[bold cyan]💡 {len(llm_patches)} AI-generated suggestions:[/bold cyan]")
            for i, patch in enumerate(llm_patches, 1):
                print(f"\n{'='*80}")
                print(f"[bold cyan]SUGGESTION {i}:[/bold cyan] [bold white]{patch['title']}[/bold white]")
                print(f"[yellow]📁 File:[/yellow] {patch['file']}")
                print(f"{'='*80}")
                
                # Show diff with enhanced formatting and contrast
                diff_lines = patch["diff"].split('\n')
                for line in diff_lines[:25]:  # Show more lines
                    if line.startswith('+++') or line.startswith('---'):
                        print(f"[bold magenta]{line}[/bold magenta]")
                    elif line.startswith('+'):
                        print(f"[black on green]+ {line[1:]}[/black on green]")
                    elif line.startswith('-'):
                        print(f"[white on red]- {line[1:]}[/white on red]")
                    elif line.startswith('@@'):
                        print(f"[black on yellow]{line}[/black on yellow]")
                    elif line.strip():
                        print(f"  {line}")
                    else:
                        print()  # Empty line for spacing
                
                if len(diff_lines) > 25:
                    print(f"[dim italic]... ({len(diff_lines) - 25} more lines)[/dim italic]")
                print(f"{'='*80}\n")
        
        if det_patches:
            print(f"\n[bold cyan]⚙️  {len(det_patches)} deterministic suggestions:[/bold cyan]")
            for i, patch in enumerate(det_patches, 1):
                print(f"\n{'='*80}")
                print(f"[bold cyan]DETERMINISTIC {i}:[/bold cyan] [bold white]{patch['title']}[/bold white]")
                print(f"[yellow]📁 File:[/yellow] {patch['file']}")
                print(f"{'='*80}")
                
                # Enhanced diff display for deterministic patches too
                diff_lines = patch['diff'].split('\n')
                for line in diff_lines[:25]:  
                    if line.startswith('+++') or line.startswith('---'):
                        print(f"[bold magenta]{line}[/bold magenta]")
                    elif line.startswith('+'):
                        print(f"[black on green]+ {line[1:]}[/black on green]")
                    elif line.startswith('-'):
                        print(f"[white on red]- {line[1:]}[/white on red]")
                    elif line.startswith('@@'):
                        print(f"[black on yellow]{line}[/black on yellow]")
                    elif line.strip():
                        print(f"  {line}")
                    else:
                        print()
                
                if len(diff_lines) > 25:
                    print(f"[dim italic]... ({len(diff_lines) - 25} more lines)[/dim italic]")
                print(f"{'='*80}\n")
        
        print(f"\n[bold green]💡 Suggestions mode (safe).[/bold green] Review and apply changes manually.")
        print(f"[dim]Found {len(llm_patches)} AI + {len(det_patches)} deterministic suggestions[/dim]")
        return

    # APPLY MODE - Actually apply the patches (DANGEROUS)
    print("[bold red]⚠️  DANGEROUS MODE: Auto-applying patches![/bold red]")
    print("[yellow]� This can corrupt your code. Ensure git backup first![/yellow]")
    
    confirm_danger = Prompt.ask("Are you sure you want to auto-apply patches?", choices=["yes", "no"], default="no")
    if confirm_danger != "yes":
        print("[green]Smart choice! Use suggestions mode instead.[/green]")
        return
    
    # Check for stale patches and warn user
    _analyze_patch_quality(llm_patches)
    
    if llm_patches:
        outdated_patterns = ["async def create_user(request: Request)", "data = await request.json()", "db.add", "User(**data)"]
        stale_count = sum(1 for patch in llm_patches if any(pattern in patch.get("diff", "") for pattern in outdated_patterns))
        
        if stale_count > 0:
            print(f"[yellow]⚠️  {stale_count} patches appear stale. Clear cache?[/yellow]")
            clear_cache = Prompt.ask("Clear cache and regenerate patches?", choices=["y", "n"], default="y")
            
            if clear_cache == "y":
                _clear_stale_cache_and_advice()
                print("[yellow]💡 Run 'fixit test --verbose' then 'fixit fix --apply' again[/yellow]")
                return
    
    applied_total = 0
    
    # Apply LLM patches ONE AT A TIME with confirmation
    if llm_patches:
        print(f"\n[bold]LLM patches - applying ONE AT A TIME:[/bold]")
        for i, patch in enumerate(llm_patches, 1):
            print(f"\n[yellow]Patch {i}/{len(llm_patches)}:[/yellow] [bold]{patch['title']}[/bold]")
            
            # Show preview
            preview_lines = patch["diff"].split('\n')[:10]
            for line in preview_lines:
                if line.startswith('+') and not line.startswith('+++'):
                    print(f"[green]{line}[/green]")
                elif line.startswith('-') and not line.startswith('---'):
                    print(f"[red]{line}[/red]")
                else:
                    print(f"[dim]{line}[/dim]")
            
            if len(patch["diff"].split('\n')) > 10:
                print("[dim]... (truncated)[/dim]")
            
            confirm = Prompt.ask(f"Apply this patch?", choices=["y", "n", "skip-all"], default="n")
            
            if confirm == "skip-all":
                break
            elif confirm == "y":
                if _apply_unified_diff_file(Path(patch["file"]), patch["diff"], patch["title"]):
                    applied_total += 1
                    print("[green]✓ Applied successfully[/green]")
                else:
                    print("[red]✗ Failed to apply - skipping[/red]")
    
    # Apply deterministic patches
    if det_patches and applied_total >= 0:  # Continue if user didn't skip all
        print(f"\n[bold]Deterministic patches - applying ONE AT A TIME:[/bold]")
        for i, patch in enumerate(det_patches, 1):
            print(f"\n[yellow]Patch {i}/{len(det_patches)}:[/yellow] [bold]{patch['title']}[/bold]")
            
            confirm = Prompt.ask(f"Apply this patch?", choices=["y", "n", "skip-all"], default="n")
            
            if confirm == "skip-all":
                break
            elif confirm == "y":
                if _apply_unified_diff_file(Path(patch["file"]), patch["diff"], patch["title"]):
                    applied_total += 1
    
    if applied_total > 0:
        print(f"\n[green]✅ {applied_total} patch(es) applied safely![/green]")
        print("[dim]💡 Run 'fixit test' to verify each fix[/dim]")
    else:
        print("[yellow]No patches were applied.[/yellow]")