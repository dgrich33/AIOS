from datetime import datetime
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def new_id() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255), default="AIOS User")
    role: Mapped[str] = mapped_column(String(32), default="developer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entitlement: Mapped["Entitlement"] = relationship(back_populates="user", uselist=False)


class Entitlement(Base):
    __tablename__ = "entitlements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    plan: Mapped[str] = mapped_column(String(64), default="aios_codex_unlimited")
    status: Mapped[str] = mapped_column(String(32), default="active")
    priority_class: Mapped[str] = mapped_column(String(64), default="premium_unlimited")
    product_unit: Mapped[str] = mapped_column(String(64), default="codex_sessions")
    access_model: Mapped[str] = mapped_column(String(64), default="unlimited_codex_access")
    has_token_limit: Mapped[bool] = mapped_column(Boolean, default=False)
    shows_token_counter: Mapped[bool] = mapped_column(Boolean, default=False)
    uses_token_balance: Mapped[bool] = mapped_column(Boolean, default=False)
    has_weekly_token_quota: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="entitlement")


class CodexModel(Base):
    __tablename__ = "codex_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    model_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(64), default="premium")
    purpose: Mapped[str] = mapped_column(Text, default="")
    runtime_provider: Mapped[str] = mapped_column(String(128), default="official_codex_adapter")
    available_in_unlimited: Mapped[bool] = mapped_column(Boolean, default=True)
    default_for: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(64), default="ready_for_adapter")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CodexPlan(Base):
    __tablename__ = "codex_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    plan_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    price_label: Mapped[str] = mapped_column(String(128), default="Premium highest tier")
    product_unit: Mapped[str] = mapped_column(String(64), default="codex_sessions")
    has_token_limit: Mapped[bool] = mapped_column(Boolean, default=False)
    shows_token_counter: Mapped[bool] = mapped_column(Boolean, default=False)
    uses_token_balance: Mapped[bool] = mapped_column(Boolean, default=False)
    has_weekly_token_quota: Mapped[bool] = mapped_column(Boolean, default=False)
    priority_class: Mapped[str] = mapped_column(String(64), default="premium_unlimited")
    status: Mapped[str] = mapped_column(String(32), default="active")
    features: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    plan_id: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    license_key: Mapped[str] = mapped_column(String(255), index=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LanguagePolicyRule(Base):
    __tablename__ = "language_policy_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    rule_type: Mapped[str] = mapped_column(String(32), index=True)
    term: Mapped[str] = mapped_column(String(255), index=True)
    severity: Mapped[str] = mapped_column(String(32), default="medium")
    replacement: Mapped[str] = mapped_column(String(255), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IdentityProfile(Base):
    __tablename__ = "identity_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    profile_type: Mapped[str] = mapped_column(String(64), default="licensed_user")
    runtime_access_mode: Mapped[str] = mapped_column(String(128), default="official_adapter_only")
    codex_auth_mode: Mapped[str] = mapped_column(String(128), default="external_account_not_managed")
    allowed_workspace: Mapped[str] = mapped_column(String(1024), default=r"C:\AIOS\aios-codex-unlimited-enterprise-v2")
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SecureRuntimeBridge(Base):
    __tablename__ = "secure_runtime_bridges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    bridge_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    mode: Mapped[str] = mapped_column(String(128), default="secure_official_adapter_boundary")
    allowed_operations: Mapped[str] = mapped_column(Text, default="[]")
    blocked_operations: Mapped[str] = mapped_column(Text, default="[]")
    requires_signed_artifact_authorization: Mapped[bool] = mapped_column(Boolean, default=True)
    stores_private_artifacts: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ContextIndex(Base):
    __tablename__ = "context_indexes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(128), default="workspace")
    status: Mapped[str] = mapped_column(String(32), default="indexed")
    file_count: Mapped[int] = mapped_column(Integer, default=0)
    graph_nodes: Mapped[int] = mapped_column(Integer, default=0)
    graph_edges: Mapped[int] = mapped_column(Integer, default=0)
    index_path: Mapped[str] = mapped_column(String(1024), default=".aios/context/index.db")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SkillStoreItem(Base):
    __tablename__ = "skill_store_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    skill_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(64), default="codex")
    tier: Mapped[str] = mapped_column(String(64), default="unlimited")
    description: Mapped[str] = mapped_column(Text, default="")
    activation_triggers: Mapped[str] = mapped_column(Text, default="[]")
    permissions_required: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(32), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WindowsReleaseArtifact(Base):
    __tablename__ = "windows_release_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    release_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    channel: Mapped[str] = mapped_column(String(64), default="rc")
    version: Mapped[str] = mapped_column(String(64), default="RC3")
    includes_private_codex_artifacts: Mapped[bool] = mapped_column(Boolean, default=False)
    launcher_type: Mapped[str] = mapped_column(String(64), default="windows_cmd_launcher")
    install_mode: Mapped[str] = mapped_column(String(64), default="portable_local")
    status: Mapped[str] = mapped_column(String(32), default="ready")
    files: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OfficialIntegrationConfig(Base):
    __tablename__ = "official_integration_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    integration_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    runtime_endpoint_label: Mapped[str] = mapped_column(String(255), default="Official Codex Runtime API")
    adapter_class: Mapped[str] = mapped_column(String(128), default="OfficialCodexRuntimeAdapter")
    sandbox_status: Mapped[str] = mapped_column(String(32), default="approved")
    staging_status: Mapped[str] = mapped_column(String(32), default="approved")
    production_status: Mapped[str] = mapped_column(String(32), default="conditional")
    streaming_supported: Mapped[bool] = mapped_column(Boolean, default=True)
    tool_calling_supported: Mapped[bool] = mapped_column(Boolean, default=True)
    session_lifecycle_supported: Mapped[bool] = mapped_column(Boolean, default=True)
    snapshot_handoff_hooks_supported: Mapped[bool] = mapped_column(Boolean, default=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=120)
    retry_max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    retry_policy: Mapped[str] = mapped_column(String(255), default="exponential_backoff_no_destructive_tool_duplication")
    status: Mapped[str] = mapped_column(String(32), default="ready_for_credentials")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SandboxDataProfile(Base):
    __tablename__ = "sandbox_data_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    profile_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    data_classification: Mapped[str] = mapped_column(String(128), default="real_sandbox_approved")
    approval_reference: Mapped[str] = mapped_column(String(255), default="")
    redaction_required: Mapped[bool] = mapped_column(Boolean, default=True)
    public_export_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    retention_days: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RestrictedAccessRequest(Base):
    __tablename__ = "restricted_access_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    operation: Mapped[str] = mapped_column(String(128), index=True)
    environment: Mapped[str] = mapped_column(String(128), default="sandbox_approved_machine")
    justification: Mapped[str] = mapped_column(Text, default="")
    artifact_name: Mapped[str] = mapped_column(String(255), default="")
    artifact_hash: Mapped[str] = mapped_column(String(255), default="")
    path_scope: Mapped[str] = mapped_column(String(1024), default=r"C:\AIOS\aios-codex-unlimited-enterprise-v2")
    status: Mapped[str] = mapped_column(String(32), default="requested", index=True)
    requested_by_user_id: Mapped[str] = mapped_column(String(36), index=True)
    approved_by: Mapped[str] = mapped_column(String(255), default="")
    decision_notes: Mapped[str] = mapped_column(Text, default="")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApprovalGateRequest(Base):
    __tablename__ = "approval_gate_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    requested_by_user_id: Mapped[str] = mapped_column(String(36), index=True)
    operation: Mapped[str] = mapped_column(String(128), index=True)
    target: Mapped[str] = mapped_column(String(1024), default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    preview: Mapped[str] = mapped_column(Text, default="{}")
    risk_level: Mapped[str] = mapped_column(String(32), default="medium", index=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=50)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    decision_reason: Mapped[str] = mapped_column(Text, default="")
    decided_by_user_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TenantMembership(Base):
    __tablename__ = "tenant_memberships"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(32), default="developer")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CodexSession(Base):
    __tablename__ = "codex_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    tenant_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    objective: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    priority_class: Mapped[str] = mapped_column(String(64), default="premium_unlimited")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("codex_sessions.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    files_changed: Mapped[str] = mapped_column(Text, default="[]")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Handoff(Base):
    __tablename__ = "handoffs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("codex_sessions.id"), index=True)
    from_adapter: Mapped[str] = mapped_column(String(128), default="local_queue")
    to_adapter: Mapped[str] = mapped_column(String(128), default="official_codex_runtime_future")
    reason: Mapped[str] = mapped_column(Text, default="")
    context: Mapped[str] = mapped_column(Text, default="")
    next_steps: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SessionEvent(Base):
    __tablename__ = "session_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("codex_sessions.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    source: Mapped[str] = mapped_column(String(128), default="api")
    title: Mapped[str] = mapped_column(String(255), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    payload: Mapped[str] = mapped_column(Text, default="{}")
    actor: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SessionFileChanged(Base):
    __tablename__ = "session_files_changed"
    __table_args__ = (UniqueConstraint("session_id", "path", name="uq_session_file_changed"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    session_id: Mapped[str] = mapped_column(ForeignKey("codex_sessions.id"), index=True)
    path: Mapped[str] = mapped_column(String(1024), index=True)
    source: Mapped[str] = mapped_column(String(128), default="api")
    last_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QosJob(Base):
    __tablename__ = "qos_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    job_type: Mapped[str] = mapped_column(String(64), default="codex_run")
    priority_class: Mapped[str] = mapped_column(String(64), default="premium_unlimited", index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    payload: Mapped[str] = mapped_column(Text, default="{}")
    result: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(128), index=True)
    resource: Mapped[str] = mapped_column(String(255), default="")
    details: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class McpToolCall(Base):
    __tablename__ = "mcp_tool_calls"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tool_name: Mapped[str] = mapped_column(String(128), index=True)
    actor: Mapped[str] = mapped_column(String(255), default="local")
    status: Mapped[str] = mapped_column(String(32), default="completed")
    details: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ServiceToken(Base):
    __tablename__ = "service_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255), index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[str] = mapped_column(String(32), default="developer")
    created_by_user_id: Mapped[str] = mapped_column(String(36), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
