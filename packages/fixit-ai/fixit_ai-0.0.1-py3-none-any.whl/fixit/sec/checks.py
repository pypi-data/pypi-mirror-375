from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import time
import re
import httpx
from fixit.core.config import Config  # duck-typed for tests too
from fixit.utils.http import make_client, make_hs256_jwt, inject_bearer

Finding = Dict[str, Any]

def _paths(spec: dict) -> Dict[str, dict]:
    return spec.get("paths", {}) or {}

def _operations(spec: dict):
    for path, ops in _paths(spec).items():
        for method, op in (ops or {}).items():
            if method.lower() in {"get", "post", "put", "patch", "delete"}:
                yield method.upper(), path, op

def _op_security(op: dict, spec: dict) -> list:
    if "security" in op:
        return op.get("security") or []
    return spec.get("security") or []

def _has_bearer_jwt_scheme(spec: dict) -> Tuple[bool, Optional[str]]:
    comps = (spec.get("components") or {}).get("securitySchemes") or {}
    for name, sch in comps.items():
        if (sch.get("type") == "http") and (sch.get("scheme", "").lower() == "bearer"):
            return True, name
    return False, None

def _find_login_path(spec: dict) -> Optional[Tuple[str, str]]:
    # Heuristic: prefer /auth/login, else any path with "login" or "/token"
    candidates = []
    for method, path, op in _operations(spec):
        p = path.lower()
        if method == "POST" and ("/auth/login" in p or p.endswith("/login")):
            candidates.append((method, path))
    if candidates:
        return candidates[0]
    for method, path, op in _operations(spec):
        p = path.lower()
        if method == "POST" and ("/token" in p or "login" in p):
            return (method, path)
    return None

def _first_get(spec: dict) -> Tuple[str, str]:
    for method, path, op in _operations(spec):
        if method == "GET":
            return method, path
    return "GET", "/"

def _sub_path_params(path: str, example_id: int = 1) -> str:
    return re.sub(r"\{[^}]+\}", str(example_id), path)

def _check_cors(base_url: str) -> Optional[Finding]:
    headers = {"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"}
    try:
        resp = httpx.options(base_url.rstrip("/") + "/", headers=headers, timeout=5.0)
    except Exception:
        return None
    acao = resp.headers.get("Access-Control-Allow-Origin")
    if acao == "*":
        return {
            "id": "CORS_WILDCARD",
            "severity": "medium",
            "message": "Access-Control-Allow-Origin is '*'",
            "evidence": {"Access-Control-Allow-Origin": acao},
            "recommendation": "Restrict allow_origins to known domains (no wildcard in production).",
        }
    return None

def _check_jwt_negative(cfg: Config, spec: dict) -> Optional[Finding]:
    has_bearer, _name = _has_bearer_jwt_scheme(spec)
    if not has_bearer:
        return None
    protected: Optional[Tuple[str, str, dict]] = None
    for method, path, op in _operations(spec):
        if _op_security(op, spec):
            protected = (method, path, op)
            break
    if not protected:
        return None
    method, path, op = protected
    url_path = _sub_path_params(path, 1)
    with make_client(cfg.base_url) as client:
        r_no = client.request(method, url_path)
        if r_no.status_code not in (401, 403):
            return {
                "id": "MISSING_AUTH",
                "severity": "high",
                "message": f"{method} {path} appears accessible without Authorization",
                "evidence": {"status": r_no.status_code, "body": (r_no.text or "")[:200]},
                "recommendation": "Enforce authentication on protected endpoints (verify bearer token).",
                "endpoint": {"method": method, "path": path},
            }
        now = int(time.time())
        bad_token = make_hs256_jwt({"sub": "9999", "iat": now, "exp": now + 3600}, secret="fixitsec")
        r_bad = client.request(method, url_path, headers=inject_bearer({}, bad_token))
        if 200 <= r_bad.status_code < 300:
            return {
                "id": "JWT_INVALID_SIGNATURE_ACCEPTED",
                "severity": "high",
                "message": f"{method} {path} accepted a JWT with an invalid signature",
                "evidence": {"status": r_bad.status_code, "token_prefix": bad_token[:20]},
                "recommendation": "Verify JWT signature and reject tokens signed with unknown keys.",
                "endpoint": {"method": method, "path": path},
            }
    return None

def _find_user_ops(spec: dict):
    post_users = None
    get_user = None
    for method, path, op in _operations(spec):
        pl = path.lower()
        if method == "POST" and pl.rstrip("/") == "/users":
            post_users = (method, path, op)
        if method == "GET" and re.match(r"^/users/\{[^}]+\}$", pl):
            get_user = (method, path, op)
    return post_users, get_user

def _check_idor(cfg: Config, spec: dict) -> Optional[Finding]:
    post_users, get_user = _find_user_ops(spec)
    if not get_user:
        return None
    created_ids: List[int] = []
    creds: List[Dict[str, str]] = []
    with make_client(cfg.base_url) as client:
        if post_users:
            for i in range(2):
                body = {
                    "email": f"fixit_user_{int(time.time())}_{i}@example.com",
                    "password": "p@ss",
                    "name": f"Fixit{i}",
                }
                r = client.post("/users", json=body)
                if r.status_code in (201, 200):
                    created_ids.append(r.json()["id"])
                    creds.append({"email": body["email"], "password": body["password"]})
                elif r.status_code == 409:
                    body["email"] = f"fixit_user_{int(time.time())}_{i}_b@example.com"
                    r = client.post("/users", json=body)
                    if r.status_code in (201, 200):
                        created_ids.append(r.json()["id"])
                        creds.append({"email": body["email"], "password": body["password"]})
        if len(created_ids) < 2:
            # fallback unauth probe
            method, path, op = get_user
            url = _sub_path_params(path, 1)
            r = client.request(method, url)
            if r.status_code not in (401, 403):
                return {
                    "id": "IDOR_OR_MISSING_AUTH",
                    "severity": "high",
                    "message": f"{method} {path} accessible without auth; potential IDOR/missing auth",
                    "evidence": {"status": r.status_code},
                    "endpoint": {"method": method, "path": path},
                    "recommendation": "Require authentication and enforce ownership checks.",
                }
            return None

        # login both users (heuristic)
        login = _find_login_path(spec) or ("POST", "/auth/login")
        _, login_path = login

        def do_login(email, password) -> Optional[str]:
            rr = client.post(login_path, json={"email": email, "password": password})
            if rr.status_code == 200 and "access_token" in rr.json():
                return rr.json()["access_token"]
            return None

        tA = do_login(creds[0]["email"], creds[0]["password"])
        tB = do_login(creds[1]["email"], creds[1]["password"])
        if not tA or not tB:
            return None

        method, path, op = get_user
        victim_id = created_ids[1]
        url = path.replace("{id}", str(victim_id)).replace("{user_id}", str(victim_id))
        r = client.request(method, url, headers=inject_bearer({}, tA))
        if r.status_code == 200:
            body = {}
            try:
                body = r.json()
            except Exception:
                pass
            return {
                "id": "IDOR_MISSING_OWNER_CHECK",
                "severity": "high",
                "message": f"{method} {path}: user A can read user B's resource (IDOR)",
                "evidence": {"status": r.status_code, "body": body},
                "endpoint": {"method": method, "path": path},
                "recommendation": "Authorize by enforcing owner check (sub == path id).",
            }
    return None

def _check_rate_limit(cfg: Config, spec: dict) -> Optional[Finding]:
    method, path = _first_get(spec)
    url = path if path.startswith("/") else "/" + path
    # configurable burst via cfg.flags.sec.{count,window_ms} (defaults)
    sec_flags = (cfg.flags or {}).get("sec", {}) if hasattr(cfg, "flags") else {}
    count = int(sec_flags.get("rate_limit_count", 15))
    codes: List[int] = []
    with make_client(cfg.base_url) as client:
        for _ in range(count):
            try:
                r = client.request(method, url)
                codes.append(r.status_code)
            except Exception:
                break
    if 429 in codes:
        return None
    return {
        "id": "NO_RATE_LIMIT",
        "severity": "low",
        "message": f"No 429 responses observed under a small burst ({count} requests).",
        "evidence": {"sample_statuses": codes[:10]},
        "recommendation": "Add a basic rate limiter (e.g., SlowAPI) for public endpoints.",
        "endpoint": {"method": method, "path": path},
    }

def run_checks(cfg: Config, spec: dict) -> List[Finding]:
    findings: List[Finding] = []
    c = _check_cors(cfg.base_url)
    if c:
        findings.append(c)
    j = _check_jwt_negative(cfg, spec)
    if j:
        findings.append(j)
    i = _check_idor(cfg, spec)
    if i:
        findings.append(i)
    r = _check_rate_limit(cfg, spec)
    if r:
        findings.append(r)
    return findings