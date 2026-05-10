from functools import lru_cache
import os
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "AIOS Codex Unlimited"
    database_url: str = Field(default_factory=lambda: os.getenv("AIOS_DATABASE_URL", "sqlite:///./aios_dev.db"))
    redis_url: str = Field(default_factory=lambda: os.getenv("AIOS_REDIS_URL", ""))
    jwt_secret: str = Field(default_factory=lambda: os.getenv("AIOS_JWT_SECRET", "dev-only-change-me"))
    jwt_issuer: str = "aios-codex-unlimited"
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
