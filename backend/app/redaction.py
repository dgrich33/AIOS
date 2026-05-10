import re
from typing import Any


SENSITIVE_KEYS = {
    "password",
    "token",
    "secret",
    "api_key",
    "authorization",
    "jwt",
    "private_key",
}

PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"pplx-[A-Za-z0-9_-]{12,}"),
    re.compile(r"AIza[A-Za-z0-9_-]{12,}"),
    re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
]


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(sensitive in lowered for sensitive in SENSITIVE_KEYS)


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if _is_sensitive_key(str(key)) else redact(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        redacted = value
        for pattern in PATTERNS:
            redacted = pattern.sub("[REDACTED]", redacted)
        return redacted
    return value
