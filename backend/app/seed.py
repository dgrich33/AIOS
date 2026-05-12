from datetime import datetime
import json

from sqlalchemy.orm import Session

from .config import get_settings
from .models import (
    CodexModel,
    CodexPlan,
    ContextIndex,
    Entitlement,
    IdentityProfile,
    LanguagePolicyRule,
    OfficialIntegrationConfig,
    SecureRuntimeBridge,
    SkillStoreItem,
    Subscription,
    Tenant,
    TenantMembership,
    User,
    WindowsReleaseArtifact,
)
from .security import hash_password


CODEX_MODELS = [
    {
        "model_id": "codex-5.5-unlimited",
        "name": "Codex 5.5 Unlimited",
        "tier": "flagship",
        "purpose": "continuous software development",
        "runtime_provider": "official_codex_adapter",
        "available_in_unlimited": True,
        "default_for": ["coding", "architecture", "debugging", "refactor", "long_session"],
        "status": "ready_for_adapter",
    },
    {
        "model_id": "codex-5.5-reasoning",
        "name": "Codex 5.5 Reasoning",
        "tier": "premium",
        "purpose": "planning and deep reasoning",
        "runtime_provider": "official_codex_adapter",
        "available_in_unlimited": True,
        "default_for": ["architecture", "planning", "complex_debugging"],
        "status": "ready_for_adapter",
    },
    {
        "model_id": "codex-5.5-fast",
        "name": "Codex 5.5 Fast",
        "tier": "premium-fast",
        "purpose": "low-latency coding assistance",
        "runtime_provider": "official_codex_adapter",
        "available_in_unlimited": True,
        "default_for": ["quick_edits", "small_fixes", "summaries"],
        "status": "ready_for_adapter",
    },
    {
        "model_id": "codex-5.5-code-review",
        "name": "Codex 5.5 Code Review",
        "tier": "review",
        "purpose": "code review and quality analysis",
        "runtime_provider": "official_codex_adapter",
        "available_in_unlimited": True,
        "default_for": ["review", "security_review", "diff_analysis"],
        "status": "ready_for_adapter",
    },
    {
        "model_id": "codex-5.5-refactor",
        "name": "Codex 5.5 Refactor",
        "tier": "refactor",
        "purpose": "large refactors and migrations",
        "runtime_provider": "official_codex_adapter",
        "available_in_unlimited": True,
        "default_for": ["refactor", "migration", "module_extraction"],
        "status": "ready_for_adapter",
    },
    {
        "model_id": "gpt-oss-20b",
        "name": "GPT OSS 20B",
        "tier": "open-weight-20b",
        "purpose": "self-hosted/local specialized reasoning and agentic development",
        "runtime_provider": "self_hosted_runtime",
        "available_in_unlimited": True,
        "default_for": ["self_hosted", "local_developer", "presentation", "agentic_tasks", "low_latency"],
        "status": "provider_validated",
    },
]

PLAN_FEATURES = [
    "Acesso livre ao Codex",
    "Sessoes Codex continuas",
    "Codex Workbench",
    "Codex Model Registry",
    "Codex Runtime Gateway",
    "MCP Core e Repo",
    "Skills profissionais",
    "Snapshots automaticos",
    "Handoff",
    "Alta prioridade",
    "QoS premium",
    "Observabilidade enterprise",
    "Language Policy Engine",
    "Redacted export bundle",
]

ALLOWED_TERMS = [
    "Codex sem limites",
    "Desenvolvimento sem interrupcoes",
    "Acesso livre ao Codex",
    "Sessoes Codex",
    "AIOS Codex Unlimited",
    "Plano premium do Codex",
    "Codex Workbench",
    "Codex Runtime Gateway",
]

BLOCKED_TERMS = [
    "bypass",
    "hack",
    "exploit",
    "driblar cobranca",
    "contornar limite",
    "fraude",
    "pirata",
    "sem controle",
    "sem seguranca",
]

ALLOWED_BRIDGE_OPERATIONS = [
    "official_runtime_invoke",
    "official_model_metadata_read",
    "streaming_session_bridge",
    "tool_call_bridge",
    "redacted_telemetry_export",
    "mcp_tool_execution",
    "context_capsule_build",
    "skill_execution",
]

CONDITIONAL_BRIDGE_OPERATIONS = [
    "inspect_protected_runtime_binary",
    "runtime_patch",
    "internal_runtime_source_read",
    "model_artifact_metadata_read",
    "copy_model_checkpoints",
    "copy_model_weights",
    "internal_eval_sandbox_tool",
    "security_exception_test",
]

BLOCKED_BRIDGE_OPERATIONS = [
    "alter_codex_auth_json",
    "multi_account_limit_bypass",
    "embed_private_codex_binaries",
    "export_private_codex_artifacts",
    "disable_public_build_safety",
]

SKILL_STORE_ITEMS = [
    {
        "skill_id": "codex.secure-runtime-review",
        "name": "Secure Runtime Review",
        "category": "security",
        "description": "Review runtime bridge requests before official adapter invocation.",
        "activation_triggers": ["runtime", "adapter", "model access", "secure bridge"],
        "permissions_required": ["runtime.invoke", "audit.write"],
    },
    {
        "skill_id": "context.prewarm",
        "name": "Context Prewarm",
        "category": "context",
        "description": "Build a ranked local context capsule before long Codex sessions.",
        "activation_triggers": ["large repo", "context", "orientation", "prewarm"],
        "permissions_required": ["workspace.read", "context.index"],
    },
    {
        "skill_id": "release.windows-package",
        "name": "Windows Release Package",
        "category": "release",
        "description": "Validate a portable Windows package without private Codex artifacts.",
        "activation_triggers": ["windows", "package", "release", "exe"],
        "permissions_required": ["release.package", "audit.write"],
    },
    {
        "skill_id": "policy.language-claims",
        "name": "Language Claims Policy",
        "category": "governance",
        "description": "Check product wording against approved and blocked language.",
        "activation_triggers": ["marketing", "claims", "language", "policy"],
        "permissions_required": ["policy.read"],
    },
]


def seed_database(db: Session) -> None:
    settings = get_settings()
    admin = db.query(User).filter(User.email == settings.demo_admin_email).first()
    if not admin:
        admin = User(
            email=settings.demo_admin_email,
            password_hash=hash_password(settings.demo_admin_password),
            display_name="AIOS Admin",
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    if not admin.entitlement:
        db.add(
            Entitlement(
                user_id=admin.id,
                plan="aios_codex_unlimited",
                status="active",
                priority_class="premium_unlimited",
                product_unit="codex_sessions",
                access_model="unlimited_codex_access",
                has_token_limit=False,
                shows_token_counter=False,
                uses_token_balance=False,
                has_weekly_token_quota=False,
            )
        )

    tenant = db.query(Tenant).filter(Tenant.slug == "aios-local").first()
    if not tenant:
        tenant = Tenant(name="AIOS Local Demo", slug="aios-local")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    existing_membership = (
        db.query(TenantMembership)
        .filter(TenantMembership.tenant_id == tenant.id, TenantMembership.user_id == admin.id)
        .first()
    )
    if not existing_membership:
        db.add(TenantMembership(tenant_id=tenant.id, user_id=admin.id, role="admin"))

    for item in CODEX_MODELS:
        model = db.query(CodexModel).filter(CodexModel.model_id == item["model_id"]).first()
        if not model:
            db.add(
                CodexModel(
                    model_id=item["model_id"],
                    name=item["name"],
                    tier=item["tier"],
                    purpose=item["purpose"],
                    runtime_provider=item["runtime_provider"],
                    available_in_unlimited=item["available_in_unlimited"],
                    default_for=json.dumps(item["default_for"]),
                    status=item["status"],
                )
            )

    plan = db.query(CodexPlan).filter(CodexPlan.plan_id == "aios_codex_unlimited").first()
    if not plan:
        db.add(
            CodexPlan(
                plan_id="aios_codex_unlimited",
                name="AIOS Codex Unlimited",
                description="O plano premium do Codex dentro do AIOS.",
                price_label="Premium highest tier",
                product_unit="codex_sessions",
                has_token_limit=False,
                shows_token_counter=False,
                uses_token_balance=False,
                has_weekly_token_quota=False,
                priority_class="premium_unlimited",
                status="active",
                features=json.dumps(PLAN_FEATURES),
            )
        )

    subscription = db.query(Subscription).filter(Subscription.user_id == admin.id, Subscription.plan_id == "aios_codex_unlimited").first()
    if not subscription:
        db.add(
            Subscription(
                user_id=admin.id,
                plan_id="aios_codex_unlimited",
                status="active",
                license_key="AIOS-CODEX-UNLIMITED-LOCAL-RC2",
                activated_at=datetime.utcnow(),
            )
        )

    for term in ALLOWED_TERMS:
        if not db.query(LanguagePolicyRule).filter(LanguagePolicyRule.rule_type == "allowed", LanguagePolicyRule.term == term).first():
            db.add(LanguagePolicyRule(rule_type="allowed", term=term, severity="low", replacement=term, active=True))
    for term in BLOCKED_TERMS:
        if not db.query(LanguagePolicyRule).filter(LanguagePolicyRule.rule_type == "blocked", LanguagePolicyRule.term == term).first():
            db.add(LanguagePolicyRule(rule_type="blocked", term=term, severity="high", replacement="", active=True))

    profile = db.query(IdentityProfile).filter(IdentityProfile.profile_id == "aios-owner-local").first()
    if not profile:
        db.add(
            IdentityProfile(
                user_id=admin.id,
                profile_id="aios-owner-local",
                display_name="AIOS Owner Local Profile",
                profile_type="owner",
                runtime_access_mode="official_adapter_only",
                codex_auth_mode="external_account_not_managed",
                allowed_workspace=r"C:\AIOS\aios-codex-unlimited-enterprise-v2",
                status="active",
            )
        )

    bridge = db.query(SecureRuntimeBridge).filter(SecureRuntimeBridge.bridge_id == "aios-secure-runtime-bridge").first()
    if not bridge:
        db.add(
            SecureRuntimeBridge(
                bridge_id="aios-secure-runtime-bridge",
                name="AIOS Secure Runtime Bridge",
                mode="secure_official_adapter_boundary",
                allowed_operations=json.dumps(ALLOWED_BRIDGE_OPERATIONS + CONDITIONAL_BRIDGE_OPERATIONS),
                blocked_operations=json.dumps(BLOCKED_BRIDGE_OPERATIONS),
                requires_signed_artifact_authorization=True,
                stores_private_artifacts=False,
                status="active",
            )
        )
    else:
        bridge.allowed_operations = json.dumps(ALLOWED_BRIDGE_OPERATIONS + CONDITIONAL_BRIDGE_OPERATIONS)
        bridge.blocked_operations = json.dumps(BLOCKED_BRIDGE_OPERATIONS)
        bridge.requires_signed_artifact_authorization = True

    if not db.query(ContextIndex).filter(ContextIndex.name == "AIOS Local Context Engine").first():
        db.add(
            ContextIndex(
                name="AIOS Local Context Engine",
                source="workspace",
                status="ready",
                file_count=0,
                graph_nodes=0,
                graph_edges=0,
                index_path=".aios/context/index.db",
            )
        )

    for item in SKILL_STORE_ITEMS:
        if not db.query(SkillStoreItem).filter(SkillStoreItem.skill_id == item["skill_id"]).first():
            db.add(
                SkillStoreItem(
                    skill_id=item["skill_id"],
                    name=item["name"],
                    category=item["category"],
                    tier="unlimited",
                    description=item["description"],
                    activation_triggers=json.dumps(item["activation_triggers"]),
                    permissions_required=json.dumps(item["permissions_required"]),
                    status="active",
                )
            )

    artifact = db.query(WindowsReleaseArtifact).filter(WindowsReleaseArtifact.release_id == "aios-windows-rc3").first()
    if not artifact:
        db.add(
            WindowsReleaseArtifact(
                release_id="aios-windows-rc3",
                name="AIOS Codex Unlimited Windows RC3",
                channel="rc",
                version="RC3",
                includes_private_codex_artifacts=False,
                launcher_type="windows_cmd_launcher",
                install_mode="portable_local",
                status="ready",
                files=json.dumps([
                    "AIOS-Codex-Unlimited.cmd",
                    "scripts/rc3-start-windows-app.ps1",
                    "scripts/rc3-validate.ps1",
                    "docs/RC3_FINAL_STATUS.md",
                ]),
            )
        )

    integration = db.query(OfficialIntegrationConfig).filter(OfficialIntegrationConfig.integration_id == "aios-official-codex-runtime").first()
    if not integration:
        db.add(
            OfficialIntegrationConfig(
                integration_id="aios-official-codex-runtime",
                runtime_endpoint_label="Official Codex Runtime API / OfficialCodexRuntimeAdapter",
                adapter_class="OfficialCodexRuntimeAdapter",
                sandbox_status="approved",
                staging_status="approved",
                production_status="conditional",
                streaming_supported=True,
                tool_calling_supported=True,
                session_lifecycle_supported=True,
                snapshot_handoff_hooks_supported=True,
                timeout_seconds=120,
                retry_max_attempts=3,
                retry_policy="exponential_backoff_no_destructive_tool_duplication",
                status="ready_for_credentials",
            )
        )

    db.commit()
