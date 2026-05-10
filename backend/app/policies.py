import json
from pathlib import Path

from .config import get_settings


DEFAULT_POLICY = {
    "productUnit": "codex_sessions",
    "forbiddenProductUnits": ["tokens", "weekly_token_quota", "token_balance"],
    "sensitiveFiles": [".env", "*.pem", "*.key", "secrets.json"],
    "allowedCommands": ["npm", "python", "pytest", "git", "docker", "node", "powershell"],
    "snapshotRequired": True,
    "auditMcpToolCalls": True,
}


def load_policy() -> dict:
    path = Path(get_settings().policy_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return DEFAULT_POLICY
