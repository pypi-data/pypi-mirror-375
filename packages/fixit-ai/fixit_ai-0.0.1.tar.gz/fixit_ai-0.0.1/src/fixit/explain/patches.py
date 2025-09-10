from __future__ import annotations
from pathlib import Path
import re
import difflib
from typing import List, Dict

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def _unified_diff(a_text: str, b_text: str, a_path: str, b_path: str) -> str:
    return "".join(difflib.unified_diff(
        a_text.splitlines(keepends=True),
        b_text.splitlines(keepends=True),
        fromfile=a_path,
        tofile=b_path,
    ))

def patch_duplicate_email(main_py: Path) -> str | None:
    """
    Fix example bug: raise HTTPException(409) instead of RuntimeError("duplicate email")
    """
    src = _read(main_py)
    # Match the duplicate email branch and RuntimeError
    pattern = (
        r'if\s+payload\.email\s+in\s+EMAIL_INDEX:\s*\n'
        r'(?:\s*#.*\n)*'
        r'\s*raise\s+RuntimeErrorKATEX_INLINE_OPEN[\'"]duplicate email[\'"]KATEX_INLINE_CLOSE'
    )
    if not re.search(pattern, src, flags=re.S):
        return None
    patched = re.sub(
        pattern,
        'if payload.email in EMAIL_INDEX:\n'
        '        # Return 409 Conflict on duplicate email\n'
        '        from fastapi import HTTPException\n'
        '        raise HTTPException(status_code=409, detail="Email already exists")',
        src,
        count=1,
        flags=re.S,
    )
    if patched == src:
        return None
    return _unified_diff(src, patched, str(main_py), str(main_py))

def patch_require_owner_on_get_user(main_py: Path) -> str | None:
    """
    Add owner check to GET /users/{user_id} handler.
    Assumes the function has authorization: Optional[str] = Header(None) and calls get_current_user(...).
    """
    src = _read(main_py)
    # Find the function header for GET /users/{user_id}
    func_def_re = re.compile(
        r'@app\.getKATEX_INLINE_OPEN"/users/\{user_id\}".*?KATEX_INLINE_CLOSE\s*def\s+get_user\s*KATEX_INLINE_OPEN\s*user_id:\s*int\s*,\s*authorization:.*?KATEX_INLINE_CLOSE:\s*\n',
        re.S,
    )
    m = func_def_re.search(src)
    if not m:
        return None

    # Insert owner check immediately after validation of token
    # We'll look for a line calling get_current_user(authorization=authorization)
    token_call_re = re.compile(r'get_current_user\s*KATEX_INLINE_OPEN\s*authorization\s*=\s*authorization\s*KATEX_INLINE_CLOSE\s*', re.S)
    pos = token_call_re.search(src[m.end():])
    if not pos:
        # if no explicit call, we still can add at the start of function body
        insert_at = m.end()
    else:
        insert_at = m.end() + pos.end()

    insert_snippet = (
        '\n    # Enforce owner check: requesting user must match path user_id\n'
        '    user = get_current_user(authorization=authorization)\n'
        '    if int(user_id) != int(user["id"]):\n'
        '        from fastapi import HTTPException\n'
        '        raise HTTPException(status_code=403, detail="Forbidden")\n'
    )

    patched = src[:insert_at] + insert_snippet + src[insert_at:]
    if patched == src:
        return None
    return _unified_diff(src, patched, str(main_py), str(main_py))

def patch_cors_restrict(main_py: Path) -> str | None:
    """
    Replace allow_origins=["*"] with a safer localhost origin example.
    """
    src = _read(main_py)
    # Matches allow_origins = ["*"] with arbitrary whitespace and quotes
    pattern = r'allow_origins\s*=\s*\[\s*["\'][\*]["\']?\s*\]'
    if not re.search(pattern, src):
        return None
    patched = re.sub(pattern, 'allow_origins=["http://localhost:3000"]', src, count=1)
    if patched == src:
        return None
    return _unified_diff(src, patched, str(main_py), str(main_py))

def suggest_rate_limiter_snippet() -> str:
    return """# Add rate limiting (SlowAPI)
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Example: limit endpoint
# @limiter.limit("5/minute")
# @app.get("/some-endpoint")
# def some_handler(): ...
"""

def compose_fastapi_patches_for_example(project_root: Path) -> list[dict]:
    """Compose deterministic patches for FastAPI projects with flexible file discovery."""
    patches: list[dict] = []
    
    # Try multiple common FastAPI file locations
    possible_main_files = [
        project_root / "main.py",
        project_root / "src" / "main.py",
        project_root / "app" / "main.py",
        project_root / "api" / "main.py",
        project_root / "backend" / "main.py",
        # Include original examples path for backward compatibility
        project_root / "examples" / "fastapi_buggy" / "main.py"
    ]
    
    # Also check for app.py as alternative
    possible_app_files = [
        project_root / "app.py",
        project_root / "src" / "app.py",
        project_root / "app" / "app.py",
        project_root / "api" / "app.py"
    ]
    
    # Find the first existing file
    main_py = None
    for candidate in possible_main_files + possible_app_files:
        if candidate.exists():
            main_py = candidate
            break
    
    if not main_py:
        # No FastAPI file found, return empty patches
        return patches

    for builder, title in [
        (patch_duplicate_email, "Fix duplicate email (409 Conflict)"),
        (patch_require_owner_on_get_user, "Add owner check to GET /users/{id}"),
        (patch_cors_restrict, "Restrict CORS allow_origins"),
    ]:
        try:
            diff = builder(main_py)
            if diff:
                patches.append({"title": title, "file": str(main_py), "diff": diff})
        except (FileNotFoundError, UnicodeDecodeError, PermissionError):
            # Skip patches that fail due to file issues
            continue
    
    try:
        patches.append({
            "title": "Add rate limiter middleware (snippet)",
            "file": str(main_py),
            "diff": suggest_rate_limiter_snippet(),
            "note": "Requires SlowAPI dependency; apply manually.",
        })
    except Exception:
        # Skip rate limiter patch if it fails
        pass
    
    return patches

def preview_patches(patches: List[Dict]) -> str:
    lines: List[str] = []
    for i, p in enumerate(patches, 1):
        lines.append("=" * 80)
        lines.append(f"{i}. {p.get('title')}")
        lines.append(f"- file: {p.get('file')}")
        note = p.get("note")
        if note:
            lines.append(f"Note: {note}")
        lines.append(p.get("diff") or "")
    return "\n".join(lines)