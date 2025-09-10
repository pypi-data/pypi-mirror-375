from __future__ import annotations
import base64, json, hmac, hashlib
from typing import Dict, Optional
import httpx

def make_client(base_url: str, headers: Optional[Dict[str, str]] = None) -> httpx.Client:
    return httpx.Client(base_url=base_url.rstrip("/"), headers=headers or {}, timeout=10.0, follow_redirects=True)

def inject_bearer(headers: Dict[str, str], token: str) -> Dict[str, str]:
    h = dict(headers or {})
    h["Authorization"] = f"Bearer {token}"
    return h

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def make_hs256_jwt(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    p = _b64url(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    sig = _b64url(hmac.new(secret.encode("utf-8"), f"{h}.{p}".encode("ascii"), hashlib.sha256).digest())
    return f"{h}.{p}.{sig}"