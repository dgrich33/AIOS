from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import json
import secrets
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import ServiceToken, User


ROLE_ORDER = {"viewer": 1, "developer": 2, "manager": 3, "admin": 4}


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def hash_service_token(token: str) -> str:
    settings = get_settings()
    digest = hmac.new(settings.jwt_secret.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"service_sha256${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, digest = stored_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return hmac.compare_digest(candidate.hex(), digest)


def create_access_token(subject: str, role: str, expires_minutes: int = 480) -> str:
    settings = get_settings()
    header = {"alg": "HS256", "typ": "JWT"}
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "role": role,
        "iss": settings.jwt_issuer,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    signing_input = f"{_b64url(json.dumps(header, separators=(',', ':')).encode())}.{_b64url(json.dumps(payload, separators=(',', ':')).encode())}"
    signature = hmac.new(settings.jwt_secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
    return f"{signing_input}.{_b64url(signature)}"


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        signing_input = f"{header_b64}.{payload_b64}"
        expected = hmac.new(settings.jwt_secret.encode("utf-8"), signing_input.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url(expected), signature_b64):
            raise ValueError("invalid signature")
        payload = json.loads(_b64url_decode(payload_b64))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("iss") != settings.jwt_issuer or int(payload.get("exp", 0)) < int(datetime.utcnow().timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token")
    return payload


def _service_token_user(raw_token: str, db: Session) -> User | None:
    if not raw_token.startswith("aios_st_"):
        return None
    fast_hash = hash_service_token(raw_token)
    fast_match = db.query(ServiceToken).filter(ServiceToken.token_hash == fast_hash).first()
    if fast_match:
        creator = db.query(User).filter(User.id == fast_match.created_by_user_id, User.is_active.is_(True)).first()
        if not creator:
            return None
        return User(
            id=creator.id,
            email=f"service-token:{fast_match.name}",
            password_hash="",
            display_name=f"Service token: {fast_match.name}",
            role=fast_match.role,
            is_active=True,
        )
    tokens = db.query(ServiceToken).all()
    for item in tokens:
        if verify_password(raw_token, item.token_hash):
            creator = db.query(User).filter(User.id == item.created_by_user_id, User.is_active.is_(True)).first()
            if not creator:
                return None
            return User(
                id=creator.id,
                email=f"service-token:{item.name}",
                password_hash="",
                display_name=f"Service token: {item.name}",
                role=item.role,
                is_active=True,
            )
    return None


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    bearer = authorization.removeprefix("Bearer ").strip()
    service_user = _service_token_user(bearer, db)
    if service_user:
        return service_user
    payload = decode_access_token(bearer)
    user = db.query(User).filter(User.id == payload["sub"], User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(required_role: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if ROLE_ORDER.get(user.role, 0) < ROLE_ORDER[required_role]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return user

    return dependency
