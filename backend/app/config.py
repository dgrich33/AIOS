from functools import lru_cache
import os
from pathlib import Path
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_ENV_FILE = PROJECT_ROOT / ".env.local.private"
PRIVATE_ENV_ALLOWED_MODES = {"local_developer", "presentation"}
PRIVATE_ENV_BLOCKED_MODES = {"production", "prod"}
PRIVATE_ENV_ALLOWED_PREFIXES = ("AIOS_", "OPENAI_", "AZURE_", "OLLAMA_")
_PRIVATE_ENV_STATUS = {
    "path": ".env.local.private",
    "loaded": False,
    "status": "not_checked",
    "keysLoaded": [],
    "keysSkipped": [],
    "secretsExposed": False,
}


def _strip_env_value(value: str) -> str:
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        return cleaned[1:-1]
    return cleaned


def _read_env_file(path: Path) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key.replace("_", "").isalnum():
            parsed[key] = _strip_env_value(value)
    return parsed


def load_private_env_file(path: str | Path | None = None, force: bool = False) -> dict:
    """Load local private developer config without exposing or persisting secrets."""
    global _PRIVATE_ENV_STATUS
    env_path = Path(path) if path else PRIVATE_ENV_FILE
    ambient_mode = (os.getenv("AIOS_ENV") or os.getenv("AIOS_ENVIRONMENT") or "").strip().lower()
    if ambient_mode in PRIVATE_ENV_BLOCKED_MODES and not force:
        _PRIVATE_ENV_STATUS = {
            "path": env_path.name,
            "loaded": False,
            "status": "blocked_in_production",
            "keysLoaded": [],
            "keysSkipped": [],
            "secretsExposed": False,
        }
        return dict(_PRIVATE_ENV_STATUS)
    if ambient_mode not in PRIVATE_ENV_ALLOWED_MODES and not force:
        _PRIVATE_ENV_STATUS = {
            "path": env_path.name,
            "loaded": False,
            "status": "blocked_until_process_mode_local_developer_or_presentation",
            "keysLoaded": [],
            "keysSkipped": [],
            "secretsExposed": False,
        }
        return dict(_PRIVATE_ENV_STATUS)
    if not env_path.exists():
        _PRIVATE_ENV_STATUS = {
            "path": env_path.name,
            "loaded": False,
            "status": "missing",
            "keysLoaded": [],
            "keysSkipped": [],
            "secretsExposed": False,
        }
        return dict(_PRIVATE_ENV_STATUS)

    values = _read_env_file(env_path)
    declared_mode = (values.get("AIOS_ENV") or ambient_mode or "local_developer").strip().lower()
    if declared_mode in PRIVATE_ENV_BLOCKED_MODES:
        _PRIVATE_ENV_STATUS = {
            "path": env_path.name,
            "loaded": False,
            "status": "blocked_by_file_mode",
            "keysLoaded": [],
            "keysSkipped": sorted(values.keys()),
            "secretsExposed": False,
        }
        return dict(_PRIVATE_ENV_STATUS)
    if declared_mode not in PRIVATE_ENV_ALLOWED_MODES and not force:
        _PRIVATE_ENV_STATUS = {
            "path": env_path.name,
            "loaded": False,
            "status": "blocked_until_local_developer_or_presentation",
            "keysLoaded": [],
            "keysSkipped": sorted(values.keys()),
            "secretsExposed": False,
        }
        return dict(_PRIVATE_ENV_STATUS)

    loaded: list[str] = []
    skipped: list[str] = []
    for key, value in values.items():
        if not key.startswith(PRIVATE_ENV_ALLOWED_PREFIXES):
            skipped.append(key)
            continue
        if key in os.environ and not force:
            skipped.append(key)
            continue
        os.environ[key] = value
        loaded.append(key)

    _PRIVATE_ENV_STATUS = {
        "path": env_path.name,
        "loaded": bool(loaded),
        "status": "loaded" if loaded else "present_no_new_keys",
        "keysLoaded": sorted(loaded),
        "keysSkipped": sorted(skipped),
        "mode": declared_mode,
        "secretsExposed": False,
    }
    return dict(_PRIVATE_ENV_STATUS)


def get_private_env_status() -> dict:
    return dict(_PRIVATE_ENV_STATUS)


def runtime_env_source() -> dict:
    return {
        "privateEnv": get_private_env_status(),
        "mode": os.getenv("AIOS_ENV") or os.getenv("AIOS_ENVIRONMENT") or "local",
        "secretsExposed": False,
    }


load_private_env_file()


class Settings(BaseModel):
    app_name: str = "AIOS Codex Unlimited"
    database_url: str = Field(default_factory=lambda: os.getenv("AIOS_DATABASE_URL", "sqlite:///./aios_dev.db"))
    redis_url: str = Field(default_factory=lambda: os.getenv("AIOS_REDIS_URL", ""))
    jwt_secret: str = Field(default_factory=lambda: os.getenv("AIOS_JWT_SECRET", "dev-only-change-me"))
    jwt_issuer: str = "aios-codex-unlimited"
    jwt_expires_minutes: int = Field(default_factory=lambda: int(os.getenv("AIOS_JWT_EXPIRES_MINUTES", "10080")))
    vault_url: str = Field(default_factory=lambda: os.getenv("AIOS_VAULT_URL", ""))
    vault_token: str = Field(default_factory=lambda: os.getenv("AIOS_VAULT_TOKEN", ""))
    policy_path: str = Field(default_factory=lambda: os.getenv("AIOS_POLICY_PATH", "../shared/policies/aios-policy.json"))
    demo_admin_email: str = Field(default_factory=lambda: os.getenv("AIOS_ADMIN_EMAIL", "admin@aios.local"))
    demo_admin_password: str = Field(default_factory=lambda: os.getenv("AIOS_ADMIN_PASSWORD", "AiosAdmin123!"))
    environment: str = Field(default_factory=lambda: os.getenv("AIOS_ENVIRONMENT", "local"))
    official_codex_runtime_endpoint: str = Field(default_factory=lambda: os.getenv("AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT", ""))
    official_codex_service_token: str = Field(default_factory=lambda: os.getenv("AIOS_OFFICIAL_CODEX_SERVICE_TOKEN", ""))
    official_codex_tenant_id: str = Field(default_factory=lambda: os.getenv("AIOS_OFFICIAL_CODEX_TENANT_ID", ""))
    official_sandbox_provider: str = Field(default_factory=lambda: os.getenv("AIOS_OFFICIAL_SANDBOX_PROVIDER", "openai_codex"))
    official_sandbox_live_enabled: bool = Field(default_factory=lambda: os.getenv("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"})
    official_sandbox_secret_store: str = Field(default_factory=lambda: os.getenv("AIOS_OFFICIAL_SANDBOX_SECRET_STORE", ""))
    official_sandbox_environment_id: str = Field(default_factory=lambda: os.getenv("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID", ""))
    azure_openai_endpoint: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_ENDPOINT", os.getenv("AIOS_AZURE_OPENAI_ENDPOINT", "")))
    azure_openai_api_key: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_API_KEY", os.getenv("AZURE_API_KEY", "")))
    azure_openai_deployment: str = Field(default_factory=lambda: os.getenv("AZURE_OPENAI_DEPLOYMENT", os.getenv("AIOS_AZURE_OPENAI_DEPLOYMENT", "")))
    azure_resource_name: str = Field(default_factory=lambda: os.getenv("AZURE_RESOURCE_NAME", ""))
    openai_base_url: str = Field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_project_id: str = Field(default_factory=lambda: os.getenv("OPENAI_PROJECT_ID", ""))
    openai_organization_id: str = Field(default_factory=lambda: os.getenv("OPENAI_ORG_ID", os.getenv("OPENAI_ORGANIZATION", "")))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-5.2-codex"))
    openai_max_output_tokens: int = Field(default_factory=lambda: int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "800")))
    openai_reasoning_effort: str = Field(default_factory=lambda: os.getenv("OPENAI_REASONING_EFFORT", "medium"))
    ollama_base_url: str = Field(default_factory=lambda: os.getenv("AIOS_OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")))
    ollama_model: str = Field(default_factory=lambda: os.getenv("AIOS_OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "deepseek-v4-pro:cloud")))
    runtime_broker_default_provider: str = Field(default_factory=lambda: os.getenv("AIOS_RUNTIME_BROKER_DEFAULT_PROVIDER", "auto"))
    aios_license_path: str = Field(default_factory=lambda: os.getenv("AIOS_LICENSE_PATH", r"C:\AIOS\aios-codex-unlimited-enterprise-v2\license.cert"))
    aios_license_authorized_hash: str = Field(default_factory=lambda: os.getenv("AIOS_LICENSE_AUTHORIZED_HASH", "2dab9a98164a84d5b596e1e1e2e51855467c5e79dccad42d370467ce6ce88b7f"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
