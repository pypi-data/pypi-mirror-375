from __future__ import annotations
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional
import time, json, base64, hmac, hashlib

app = FastAPI(title="Buggy API", version="0.2.0")

# Planted misconfiguration: permissive CORS (to be flagged by fixit sec)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # BUG: wildcard
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory "DB"
USERS: Dict[int, Dict] = {}
EMAIL_INDEX: Dict[str, int] = {}
SEQ_ID = 0

SECRET_KEY = "devsecret"  # demo only
ALGORITHM = "HS256"

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _sign(msg: bytes, key: str) -> str:
    return _b64url(hmac.new(key.encode("utf-8"), msg, hashlib.sha256).digest())

def create_jwt(payload: dict, key: str, alg: str = "HS256") -> str:
    header = {"alg": alg, "typ": "JWT"}
    h = _b64url(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    p = _b64url(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    sig = _sign(f"{h}.{p}".encode("ascii"), key)
    return f"{h}.{p}.{sig}"

def decode_jwt(token: str, key: str) -> dict:
    try:
        h_b64, p_b64, sig = token.split(".")
    except ValueError:
        raise HTTPException(status_code=401, detail="Malformed token")
    expected = _sign(f"{h_b64}.{p_b64}".encode("ascii"), key)
    if not hmac.compare_digest(expected, sig):
        raise HTTPException(status_code=401, detail="Invalid signature")
    padded = p_b64 + "==="
    payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    exp = payload.get("exp")
    if exp is not None and time.time() > float(exp):
        raise HTTPException(status_code=401, detail="Token expired")
    return payload

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

@app.get("/")
def root():
    return {"ok": True}

# BUG #1: duplicate email -> raises 500 instead of 409 according to spec
@app.post("/users", status_code=201, response_model=UserOut)
def create_user(payload: UserCreate):
    global SEQ_ID
    if payload.email in EMAIL_INDEX:
        # Fixed: Return proper 409 Conflict instead of unhandled error
        raise HTTPException(status_code=409, detail="Email already exists")
    SEQ_ID += 1
    user = {"id": SEQ_ID, "email": str(payload.email), "password": payload.password, "name": payload.name}
    USERS[user["id"]] = user
    EMAIL_INDEX[user["email"]] = user["id"]
    return {"id": user["id"], "email": user["email"], "name": user["name"]}

@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginRequest):
    uid = EMAIL_INDEX.get(str(body.email))
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = USERS[uid]
    if user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    now = int(time.time())
    exp = now + 3600
    token = create_jwt({"sub": user["id"], "email": user["email"], "iat": now, "exp": exp}, SECRET_KEY)
    return {"access_token": token, "token_type": "bearer", "expires_in": 3600}

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_jwt(token, SECRET_KEY)
    uid = int(payload.get("sub", 0))
    user = USERS.get(uid)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# BUG #2 (M1): endpoint now requires auth but still lacks owner check (IDOR)
@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, authorization: Optional[str] = Header(None)):
    # Require a valid token (auth check) but DO NOT enforce owner check (bug)
    _ = get_current_user(authorization=authorization)  # validate token only
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user["id"], "email": user["email"], "name": user["name"]}