"""JWT authentication utilities for OrcaFit API."""

import hashlib
import hmac
import json
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass

# Simple secret — in production, use env var
SECRET_KEY = "orcafit-dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 3600  # 1 hour
REFRESH_TOKEN_EXPIRE_SECONDS = 86400 * 30  # 30 days


def _b64encode(data: bytes) -> str:
    return urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(data: str) -> bytes:
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return urlsafe_b64decode(data)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt. Simple but functional."""
    import secrets
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, hash_value = hashed.split(":", 1)
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hash_value
    except (ValueError, AttributeError):
        return False


def create_token(user_id: int, expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS) -> str:
    """Create a simple JWT-like token."""
    header = _b64encode(json.dumps({"alg": ALGORITHM, "typ": "JWT"}).encode())
    payload = _b64encode(json.dumps({
        "sub": str(user_id),
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time()),
    }).encode())
    
    signature = hmac.new(
        SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256
    ).digest()
    sig_b64 = _b64encode(signature)
    
    return f"{header}.{payload}.{sig_b64}"


def decode_token(token: str) -> dict | None:
    """Decode and verify a token. Returns payload dict or None if invalid."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, sig_b64 = parts
        
        # Verify signature
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256,
        ).digest()
        
        actual_sig = _b64decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        # Decode payload
        payload = json.loads(_b64decode(payload_b64))
        
        # Check expiration
        if payload.get("exp", 0) < time.time():
            return None
        
        return payload
    except Exception:
        return None


def create_token_pair(user_id: int) -> dict:
    """Create access + refresh token pair."""
    return {
        "access_token": create_token(user_id, ACCESS_TOKEN_EXPIRE_SECONDS),
        "refresh_token": create_token(user_id, REFRESH_TOKEN_EXPIRE_SECONDS),
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
    }
