from datetime import datetime, timedelta
import json
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .codex_adapter import AIOSCognitiveRuntimeMesh, OfficialCodexRuntimeAdapter, OllamaRuntimeAdapter, adapter
from .config import get_settings
from .db import SessionLocal, get_db, init_db
from .license_manager import license_status
from .models import (
    ApprovalGateRequest,
    AuditLog,
    CodexModel,
    CodexPlan,
    CodexSession,
    ContextIndex,
    Entitlement,
    Handoff,
    IdentityProfile,
    LanguagePolicyRule,
    McpToolCall,
    OfficialIntegrationConfig,
    QosJob,
    RestrictedAccessRequest,
    SandboxDataProfile,
    SecureRuntimeBridge,
    ServiceToken,
    SessionEvent,
    SessionFileChanged,
    SkillStoreItem,
    Snapshot,
    Subscription,
    Tenant,
    TenantMembership,
    User,
    WindowsReleaseArtifact,
)
from .observability import SESSION_COMPLETED_TOTAL, SESSION_CREATED_TOTAL, SNAPSHOT_CREATED_TOTAL, instrument_app
from .policies import load_policy
from .qos import enqueue_job, queue_depth
from .redaction import redact
from .scope_authority import scope_authority_status
from .security import create_access_token, get_current_user, hash_password, hash_service_token, require_role, verify_password
from .seed import seed_database
from .vault_client import VaultClient



@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(title="AIOS Codex Unlimited API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
instrument_app(app)


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateUserRequest(BaseModel):
    email: str
    password: str
    displayName: str = "AIOS User"
    role: str = "developer"


class CreateSessionRequest(BaseModel):
    title: str = "Codex Workbench Session"
    objective: str = "Build with Codex sessions, not token quotas."


class UpdateSessionStatusRequest(BaseModel):
    status: str = Field(pattern="^(active|paused|completed|failed)$")


class CreateSnapshotRequest(BaseModel):
    sessionId: str
    title: str = "AIOS snapshot"
    filesChanged: list[str] = Field(default_factory=list)
    notes: str = ""


class CreateHandoffRequest(BaseModel):
    sessionId: str
    fromAdapter: str = "local_queue"
    toAdapter: str = "official_codex_runtime_future"
    reason: str = "Continue Codex work from the latest AIOS checkpoint."
    context: str = ""
    nextSteps: list[str] = Field(default_factory=list)


class CreateSessionEventRequest(BaseModel):
    type: str
    source: str = "api"
    title: str = ""
    message: str = ""
    payload: dict = Field(default_factory=dict)


class FilesChangedRequest(BaseModel):
    filesChanged: list[str] = Field(default_factory=list)
    source: str = "api"


class ActivateSubscriptionRequest(BaseModel):
    license_key: str


class RuntimeInvokeRequest(BaseModel):
    session_id: str
    model_id: str = "codex-5.5-unlimited"
    objective: str


class RuntimeBrokerInvokeRequest(BaseModel):
    sessionId: str
    objective: str
    provider: str = "auto"
    intelligenceMode: str = "aios_cognitive_runtime_mesh"
    model: str | None = None


class ScopePreflightRequest(BaseModel):
    operation: str = "codex.runtime.invoke"
    environment: str = "sandbox"
    modelId: str = "codex-5.5-unlimited"
    requiresLiveRuntime: bool = False
    requiresRestrictedArtifacts: bool = False
    reason: str = "AIOS Codex Unlimited scoped operation"


class LanguageEvaluateRequest(BaseModel):
    text: str


class SecureRuntimeRequest(BaseModel):
    sessionId: str
    operation: str
    objective: str = ""
    payload: dict = Field(default_factory=dict)


class CreateContextIndexRequest(BaseModel):
    sessionId: str | None = None
    name: str = "AIOS context index"
    source: str = "workspace"
    fileCount: int = 0
    graphNodes: int = 0
    graphEdges: int = 0


class ContextQueryRequest(BaseModel):
    query: str
    sessionId: str | None = None
    maxResults: int = 5


class OfficialAdapterDryRunRequest(BaseModel):
    modelId: str = "codex-5.5-unlimited"
    objective: str = "Validate official adapter contract."


class CreateRestrictedAccessRequest(BaseModel):
    operation: str
    environment: str = "sandbox_approved_machine"
    justification: str
    artifactName: str = ""
    artifactHash: str = ""
    pathScope: str = r"C:\AIOS\aios-codex-unlimited-enterprise-v2"
    expiresInDays: int = 30


class RestrictedAccessDecisionRequest(BaseModel):
    decision: str = Field(pattern="^(approved|denied|revoked)$")
    approver: str
    notes: str = ""


class RestrictedAccessLogRequest(BaseModel):
    action: str
    artifactPath: str = ""
    artifactHash: str = ""
    justification: str = ""
    result: str = "recorded"


class CreateApprovalGateRequest(BaseModel):
    sessionId: str | None = None
    operation: str
    target: str = ""
    reason: str
    preview: dict = Field(default_factory=dict)


class ApprovalGateDecisionRequest(BaseModel):
    decision: str = Field(pattern="^(approved|rejected|cancelled)$")
    reason: str = ""


class CreateSandboxDataProfileRequest(BaseModel):
    profileId: str
    name: str
    dataClassification: str = "real_sandbox_approved"
    approvalReference: str
    redactionRequired: bool = True
    publicExportAllowed: bool = False
    retentionDays: int = Field(default=30, ge=1, le=365)
    status: str = "active"


class UpsertCodexModelRequest(BaseModel):
    modelId: str
    name: str
    tier: str = "premium"
    purpose: str = ""
    runtimeProvider: str = "official_codex_adapter"
    availableInUnlimited: bool = True
    defaultFor: list[str] = Field(default_factory=list)
    status: str = "ready_for_adapter"


class UpsertCodexPlanRequest(BaseModel):
    planId: str
    name: str
    description: str = ""
    priceLabel: str = "Premium highest tier"
    productUnit: str = "codex_sessions"
    priorityClass: str = "premium_unlimited"
    status: str = "active"
    features: list[str] = Field(default_factory=list)


class UpsertLanguageRuleRequest(BaseModel):
    ruleType: str = Field(pattern="^(allowed|blocked)$")
    term: str
    severity: str = "medium"
    replacement: str = ""
    active: bool = True


class UpsertSkillStoreItemRequest(BaseModel):
    skillId: str
    name: str
    category: str = "codex"
    tier: str = "unlimited"
    description: str = ""
    activationTriggers: list[str] = Field(default_factory=list)
    permissionsRequired: list[str] = Field(default_factory=list)
    status: str = "active"


class EnqueueRequest(BaseModel):
    jobType: str = "codex_run"
    payload: dict = Field(default_factory=dict)
    priorityClass: str = "premium_unlimited"


class CodexRunRequest(BaseModel):
    objective: str
    sessionId: str | None = None


class SkillExecuteRequest(BaseModel):
    skillName: str
    input: dict = Field(default_factory=dict)


class AbuseEvaluateRequest(BaseModel):
    toolCallFlood: int = 0
    failedBuilds: int = 0
    sessionSpike: int = 0
    suspiciousCommand: bool = False


class SecretRequest(BaseModel):
    value: dict


class CreateTenantRequest(BaseModel):
    name: str
    slug: str


class CreateTenantMemberRequest(BaseModel):
    userId: str
    role: str = "developer"


def entitlement_response(entitlement: Entitlement) -> dict:
    return {
        "plan": entitlement.plan,
        "status": entitlement.status,
        "priorityClass": entitlement.priority_class,
        "productUnit": entitlement.product_unit,
        "accessModel": entitlement.access_model,
        "hasTokenLimit": entitlement.has_token_limit,
        "showsTokenCounter": entitlement.shows_token_counter,
        "usesTokenBalance": entitlement.uses_token_balance,
        "hasWeeklyTokenQuota": entitlement.has_weekly_token_quota,
    }


ALLOWED_SESSION_EVENT_TYPES = {
    "mcp.tool_call",
    "codex.runtime.invoked",
    "codex.runtime.completed",
    "codex.runtime.failed",
    "codex.secure_runtime.requested",
    "context.index.created",
    "repo.patch_applied",
    "repo.file_changed",
    "repo.build_started",
    "repo.build_passed",
    "repo.build_failed",
    "snapshot.created",
    "handoff.created",
    "skill.executed",
}

CODEX_MODEL_DISCOVERY_CANDIDATES = [
    "gpt-5.5",
    "gpt-5.5-pro",
    "gpt-5.2-codex",
    "gpt-5.1-codex",
    "gpt-5.1-codex-max",
    "gpt-5.1-codex-mini",
    "gpt-5-codex",
]

APPROVED_SCOPE_MODELS = {
    "codex-5.5-unlimited",
    "codex-5.5-reasoning",
    "codex-5.5-fast",
    "codex-5.5-code-review",
    "codex-5.5-refactor",
    "gpt-5.2-codex",
}

APPROVED_SCOPE_OPERATIONS = {
    "codex.runtime.invoke",
    "codex.runtime.stream",
    "codex.tool.call",
    "mcp.tool_call",
    "runtime.patch.compatibility",
    "restricted.artifact.inspect",
    "sandbox.real_data.test",
}

APPROVED_SCOPE_ENVIRONMENTS = {
    "sandbox",
    "sandbox_approved_machine",
    "staging",
    "production_conditioned",
    "producao_condicionada",
}


def codex_model_response(item: CodexModel) -> dict:
    return {
        "id": item.id,
        "modelId": item.model_id,
        "name": item.name,
        "tier": item.tier,
        "purpose": item.purpose,
        "runtimeProvider": item.runtime_provider,
        "availableInUnlimited": item.available_in_unlimited,
        "defaultFor": json.loads(item.default_for or "[]"),
        "status": item.status,
        "createdAt": item.created_at.isoformat(),
    }


def codex_plan_response(item: CodexPlan) -> dict:
    return {
        "id": item.id,
        "planId": item.plan_id,
        "name": item.name,
        "description": item.description,
        "priceLabel": item.price_label,
        "productUnit": item.product_unit,
        "hasTokenLimit": item.has_token_limit,
        "showsTokenCounter": item.shows_token_counter,
        "usesTokenBalance": item.uses_token_balance,
        "hasWeeklyTokenQuota": item.has_weekly_token_quota,
        "priorityClass": item.priority_class,
        "status": item.status,
        "features": json.loads(item.features or "[]"),
        "createdAt": item.created_at.isoformat(),
    }


def subscription_response(item: Subscription | None) -> dict:
    if not item:
        return {"status": "missing"}
    return {
        "id": item.id,
        "planId": item.plan_id,
        "status": item.status,
        "licenseKey": item.license_key,
        "activatedAt": item.activated_at.isoformat() if item.activated_at else None,
        "createdAt": item.created_at.isoformat(),
    }


def language_rule_response(item: LanguagePolicyRule) -> dict:
    return {
        "id": item.id,
        "ruleType": item.rule_type,
        "term": item.term,
        "severity": item.severity,
        "replacement": item.replacement,
        "active": item.active,
        "createdAt": item.created_at.isoformat(),
    }


def identity_profile_response(item: IdentityProfile) -> dict:
    return {
        "id": item.id,
        "profileId": item.profile_id,
        "displayName": item.display_name,
        "profileType": item.profile_type,
        "runtimeAccessMode": item.runtime_access_mode,
        "codexAuthMode": item.codex_auth_mode,
        "allowedWorkspace": item.allowed_workspace,
        "status": item.status,
        "createdAt": item.created_at.isoformat(),
    }


def secure_runtime_bridge_response(item: SecureRuntimeBridge) -> dict:
    return {
        "id": item.id,
        "bridgeId": item.bridge_id,
        "name": item.name,
        "mode": item.mode,
        "allowedOperations": json.loads(item.allowed_operations or "[]"),
        "blockedOperations": json.loads(item.blocked_operations or "[]"),
        "requiresSignedArtifactAuthorization": item.requires_signed_artifact_authorization,
        "storesPrivateArtifacts": item.stores_private_artifacts,
        "status": item.status,
        "createdAt": item.created_at.isoformat(),
    }


def context_index_response(item: ContextIndex) -> dict:
    return {
        "id": item.id,
        "sessionId": item.session_id,
        "name": item.name,
        "source": item.source,
        "status": item.status,
        "fileCount": item.file_count,
        "graphNodes": item.graph_nodes,
        "graphEdges": item.graph_edges,
        "indexPath": item.index_path,
        "createdAt": item.created_at.isoformat(),
    }


def skill_store_item_response(item: SkillStoreItem) -> dict:
    return {
        "id": item.id,
        "skillId": item.skill_id,
        "name": item.name,
        "category": item.category,
        "tier": item.tier,
        "description": item.description,
        "activationTriggers": json.loads(item.activation_triggers or "[]"),
        "permissionsRequired": json.loads(item.permissions_required or "[]"),
        "status": item.status,
        "createdAt": item.created_at.isoformat(),
    }


def windows_release_response(item: WindowsReleaseArtifact) -> dict:
    return {
        "id": item.id,
        "releaseId": item.release_id,
        "name": item.name,
        "platform": "windows",
        "channel": item.channel,
        "version": item.version,
        "includesPrivateCodexArtifacts": item.includes_private_codex_artifacts,
        "launcherType": item.launcher_type,
        "installMode": item.install_mode,
        "status": item.status,
        "files": json.loads(item.files or "[]"),
        "createdAt": item.created_at.isoformat(),
    }


def official_integration_response(item: OfficialIntegrationConfig) -> dict:
    return {
        "id": item.id,
        "integrationId": item.integration_id,
        "runtimeEndpointLabel": item.runtime_endpoint_label,
        "adapterClass": item.adapter_class,
        "sandboxStatus": item.sandbox_status,
        "stagingStatus": item.staging_status,
        "productionStatus": item.production_status,
        "streamingSupported": item.streaming_supported,
        "toolCallingSupported": item.tool_calling_supported,
        "sessionLifecycleSupported": item.session_lifecycle_supported,
        "snapshotHandoffHooksSupported": item.snapshot_handoff_hooks_supported,
        "timeoutSeconds": item.timeout_seconds,
        "retryMaxAttempts": item.retry_max_attempts,
        "retryPolicy": item.retry_policy,
        "status": item.status,
        "createdAt": item.created_at.isoformat(),
    }


def sandbox_data_profile_response(item: SandboxDataProfile) -> dict:
    return {
        "id": item.id,
        "profileId": item.profile_id,
        "name": item.name,
        "dataClassification": item.data_classification,
        "approvalReference": item.approval_reference,
        "redactionRequired": item.redaction_required,
        "publicExportAllowed": item.public_export_allowed,
        "realDataApproved": item.data_classification == "real_sandbox_approved" and bool(item.approval_reference),
        "retentionDays": item.retention_days,
        "status": item.status,
        "createdByUserId": item.created_by_user_id,
        "createdAt": item.created_at.isoformat(),
    }


def restricted_access_response(item: RestrictedAccessRequest) -> dict:
    expired = bool(item.expires_at and item.expires_at < datetime.utcnow())
    return {
        "id": item.id,
        "operation": item.operation,
        "environment": item.environment,
        "justification": item.justification,
        "artifactName": item.artifact_name,
        "artifactHash": item.artifact_hash,
        "pathScope": item.path_scope,
        "status": item.status,
        "requestedByUserId": item.requested_by_user_id,
        "approvedBy": item.approved_by,
        "decisionNotes": item.decision_notes,
        "expiresAt": item.expires_at.isoformat() if item.expires_at else None,
        "decidedAt": item.decided_at.isoformat() if item.decided_at else None,
        "expired": expired,
        "activeApproval": item.status == "approved" and not expired,
        "createdAt": item.created_at.isoformat(),
    }


APPROVAL_GATE_SENSITIVE_OPERATIONS = [
    "shell_command",
    "apply_patch",
    "workspace_write",
    "dependency_install",
    "git_push",
    "mcp_tool_execute",
    "runtime_patch",
    "delete_file",
    "delete_directory",
    "external_network_call",
]

APPROVAL_GATE_BLOCKED_OPERATIONS = [
    "read_auth_json_contents",
    "copy_auth_json_between_machines",
    "expose_service_token_to_frontend",
    "commit_secret_to_repository",
    "auto_execute_without_human_approval",
]


def approval_gate_policy() -> dict:
    return {
        "phase": "RC24_APPROVAL_GATE",
        "productUnit": "codex_sessions",
        "mode": "human_approval_required",
        "requiresHumanApproval": True,
        "autoExecuteAllowed": False,
        "executionSurface": "operator_manual_only_after_decision",
        "sensitiveOperations": APPROVAL_GATE_SENSITIVE_OPERATIONS,
        "blockedOperations": APPROVAL_GATE_BLOCKED_OPERATIONS,
        "decisionStates": ["pending", "approved", "rejected", "cancelled"],
        "auditEvents": ["approval_gate.requested", "approval_gate.approved", "approval_gate.rejected", "approval_gate.cancelled"],
        "secretsExposed": False,
    }


def approval_gate_risk(operation: str, preview: dict) -> tuple[str, int]:
    operation_id = operation.strip().lower()
    preview_text = json.dumps(preview, sort_keys=True).lower()
    critical_operations = {"delete_file", "delete_directory", "runtime_patch", "external_network_call"}
    high_operations = {"shell_command", "apply_patch", "workspace_write", "dependency_install", "git_push", "mcp_tool_execute"}
    critical_markers = ["remove-item", "rm -rf", "format ", "del /f", "vault", "auth.json"]
    high_markers = ["api_key", "token", "secret", "password", "npm install", "pip install"]
    if operation_id in critical_operations or any(marker in preview_text for marker in critical_markers):
        return "critical", 95
    if operation_id in high_operations or any(marker in preview_text for marker in high_markers):
        return "high", 80
    if operation_id in APPROVAL_GATE_SENSITIVE_OPERATIONS:
        return "medium", 60
    return "medium", 50


def approval_gate_response(item: ApprovalGateRequest) -> dict:
    return {
        "phase": "RC24_APPROVAL_GATE",
        "id": item.id,
        "sessionId": item.session_id,
        "operation": item.operation,
        "target": item.target,
        "reason": item.reason,
        "preview": json.loads(item.preview or "{}"),
        "riskLevel": item.risk_level,
        "riskScore": item.risk_score,
        "status": item.status,
        "approvalRequired": True,
        "autoExecuteAllowed": False,
        "executionPerformed": False,
        "requestedByUserId": item.requested_by_user_id,
        "decisionReason": item.decision_reason,
        "decidedByUserId": item.decided_by_user_id,
        "decidedAt": item.decided_at.isoformat() if item.decided_at else None,
        "createdAt": item.created_at.isoformat(),
        "secretsExposed": False,
    }


def legacy_aios_summary() -> dict:
    return {
        "sourceProjectPath": r"C:\Users\dg71\Documents\AIOS-15-Fase3-Corrigido",
        "sourceStatus": "frontend_localstorage_phase3_corrected",
        "currentTargetPath": r"C:\AIOS\aios-codex-unlimited-enterprise-v2",
        "summary": "AIOS iniciou como workspace local para contas, memoria, sessoes, terminal, Arena.IA e analiticos. A linha atual migrou essa experiencia para backend enterprise, MCP, QoS, RBAC, Vault e Workbench Codex baseado em sessoes.",
        "legacyModules": [
            "Login",
            "Tutorial",
            "Painel CEO",
            "Dashboard",
            "Arena.IA",
            "Area de Trabalho",
            "Chat IA",
            "Memoria",
            "Pool de Chaves",
            "Terminal",
            "Analiticos",
            "Equipe",
        ],
        "migrationMap": {
            "Painel CEO": "Control Plane and admin governance",
            "Dashboard": "Workbench metrics and observability",
            "Arena.IA": "Codex Workbench skill routing",
            "Area de Trabalho": "Continuous Codex sessions",
            "Chat IA": "Codex runtime adapter boundary",
            "Memoria": "Snapshots, handoff and future project memory",
            "Pool de Chaves": "Vault boundary and redacted exports",
            "Terminal": "MCP repo operator with policy enforcement",
            "Analiticos": "Prometheus, Grafana, Loki and audit endpoints",
            "Equipe": "RBAC, tenants and service tokens",
        },
        "documentsReviewed": {
            "recapPath": r"C:\Users\dg71\Downloads\projeto oficial OpenAI recapitular",
            "messageFiles": 18,
            "legalNote": "Historico tratado como documentacao fornecida pelo responsavel do projeto, sem afirmacao juridica independente.",
        },
    }


def handoff_response(item: Handoff) -> dict:
    return {
        "id": item.id,
        "sessionId": item.session_id,
        "fromAdapter": item.from_adapter,
        "toAdapter": item.to_adapter,
        "reason": item.reason,
        "context": item.context,
        "nextSteps": json.loads(item.next_steps or "[]"),
        "createdAt": item.created_at.isoformat(),
    }


def session_response(item: CodexSession) -> dict:
    return {
        "id": item.id,
        "title": item.title,
        "objective": item.objective,
        "status": item.status,
        "priorityClass": item.priority_class,
        "createdAt": item.created_at.isoformat(),
    }


def snapshot_response(item: Snapshot) -> dict:
    return {
        "id": item.id,
        "sessionId": item.session_id,
        "title": item.title,
        "filesChanged": json.loads(item.files_changed or "[]"),
        "notes": item.notes,
        "createdAt": item.created_at.isoformat(),
    }


def session_event_response(item: SessionEvent) -> dict:
    return {
        "id": item.id,
        "sessionId": item.session_id,
        "type": item.event_type,
        "source": item.source,
        "title": item.title,
        "message": item.message,
        "payload": json.loads(item.payload or "{}"),
        "actor": item.actor,
        "createdAt": item.created_at.isoformat(),
    }


def qos_job_response(item: QosJob) -> dict:
    return {
        "id": item.id,
        "jobType": item.job_type,
        "status": item.status,
        "priorityClass": item.priority_class,
        "payload": json.loads(item.payload or "{}"),
        "result": json.loads(item.result or "{}"),
        "createdAt": item.created_at.isoformat(),
    }


def audit(db: Session, user: User | None, action: str, resource: str = "", details: dict | None = None) -> None:
    db.add(AuditLog(actor_user_id=user.id if user else None, action=action, resource=resource, details=json.dumps(details or {})))
    db.commit()


def get_owned_session(db: Session, user: User, session_id: str) -> CodexSession:
    session = db.query(CodexSession).filter(CodexSession.id == session_id, CodexSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def record_session_event(
    db: Session,
    user: User,
    session_id: str,
    event_type: str,
    source: str,
    title: str,
    message: str,
    payload: dict | None = None,
) -> SessionEvent:
    if event_type not in ALLOWED_SESSION_EVENT_TYPES:
        raise HTTPException(status_code=422, detail=f"Unsupported event type: {event_type}")
    event = SessionEvent(
        session_id=session_id,
        event_type=event_type,
        source=source,
        title=title,
        message=message,
        payload=json.dumps(payload or {}),
        actor=user.email,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    audit(db, user, "sessions.events.create", event.id, {"sessionId": session_id, "type": event_type, "source": source})
    return event


def record_files_changed(db: Session, session_id: str, files_changed: list[str], source: str, event_id: str | None = None) -> list[str]:
    cleaned = []
    for path in files_changed:
        normalized = path.replace("\\", "/").strip()
        if normalized and normalized not in cleaned:
            cleaned.append(normalized)
    for path in cleaned:
        existing = db.query(SessionFileChanged).filter(SessionFileChanged.session_id == session_id, SessionFileChanged.path == path).first()
        if existing:
            existing.source = source
            existing.last_event_id = event_id
            existing.updated_at = datetime.utcnow()
        else:
            db.add(SessionFileChanged(session_id=session_id, path=path, source=source, last_event_id=event_id))
    db.commit()
    return cleaned


def contract_authority_status() -> dict:
    root = Path(__file__).resolve().parents[2]
    lock_path = root / "docs" / "CONTRACT_AUTHORITY.lock.json"
    protected = [
        root / "docs" / "legal" / "11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md",
        root / "docs" / "AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md",
    ]
    if not lock_path.exists():
        return {"locked": False, "lockPath": str(lock_path), "protectedFiles": []}
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {"locked": False, "lockPath": str(lock_path), "error": "invalid lock file"}
    return {
        "locked": True,
        "lockPath": str(lock_path),
        "protectedFiles": [item.get("path") for item in lock.get("protectedFiles", [])],
        "protectedFilesExist": all(path.exists() for path in protected),
    }


def official_adapter() -> OfficialCodexRuntimeAdapter:
    settings = get_settings()
    if settings.official_sandbox_provider.strip().lower() == "openai_api":
        return OfficialCodexRuntimeAdapter(
            settings.openai_base_url,
            settings.openai_api_key,
            provider="openai_api",
            default_model=settings.openai_model,
            project_id=settings.openai_project_id,
            organization_id=settings.openai_organization_id,
            max_output_tokens=settings.openai_max_output_tokens,
            reasoning_effort=settings.openai_reasoning_effort,
        )
    return OfficialCodexRuntimeAdapter(settings.official_codex_runtime_endpoint, settings.official_codex_service_token)


def ollama_adapter() -> OllamaRuntimeAdapter:
    settings = get_settings()
    return OllamaRuntimeAdapter(settings.ollama_base_url, settings.ollama_model)


def official_sandbox_security_state(db: Session | None = None) -> dict:
    settings = get_settings()
    contract = contract_authority_status()
    provider = settings.official_sandbox_provider.strip().lower() or "openai_codex"
    is_azure = provider == "azure_openai"
    is_openai_api = provider == "openai_api"
    azure_endpoint_configured = bool(settings.azure_openai_endpoint or settings.azure_resource_name)
    azure_api_key_configured = bool(settings.azure_openai_api_key)
    azure_deployment_configured = bool(settings.azure_openai_deployment)
    openai_endpoint_configured = bool(settings.openai_base_url)
    openai_api_key_configured = bool(settings.openai_api_key)
    if is_azure:
        endpoint_configured = azure_endpoint_configured
        service_token_configured = azure_api_key_configured
    elif is_openai_api:
        endpoint_configured = openai_endpoint_configured
        service_token_configured = openai_api_key_configured
    else:
        endpoint_configured = bool(settings.official_codex_runtime_endpoint)
        service_token_configured = bool(settings.official_codex_service_token)
    tenant_configured = bool(settings.official_codex_tenant_id)
    environment_configured = bool(settings.official_sandbox_environment_id)
    secure_store_configured = settings.official_sandbox_secret_store.strip().lower() in {"vault", "kms", "vault/kms", "openai-managed-kms"}
    live_flag_enabled = settings.official_sandbox_live_enabled

    missing = []
    provider_requirements = {
        "provider": provider,
        "endpoint": (
            "AZURE_OPENAI_ENDPOINT or AZURE_RESOURCE_NAME"
            if is_azure
            else ("default https://api.openai.com/v1 or OPENAI_BASE_URL" if is_openai_api else "AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT")
        ),
        "credential": "AZURE_OPENAI_API_KEY" if is_azure else ("OPENAI_API_KEY" if is_openai_api else "AIOS_OFFICIAL_CODEX_SERVICE_TOKEN"),
        "deployment": "AZURE_OPENAI_DEPLOYMENT" if is_azure else None,
        "tenant": "optional for Azure API key mode" if is_azure else ("optional OPENAI_PROJECT_ID/OPENAI_ORG_ID" if is_openai_api else "AIOS_OFFICIAL_CODEX_TENANT_ID"),
    }
    if not contract.get("locked", False):
        missing.append("CONTRACT_AUTHORITY_LOCK")
    if not endpoint_configured:
        missing.append(provider_requirements["endpoint"])
    if not service_token_configured:
        missing.append(provider_requirements["credential"])
    if is_azure and not azure_deployment_configured:
        missing.append("AZURE_OPENAI_DEPLOYMENT")
    if not is_azure and not is_openai_api and not tenant_configured:
        missing.append("AIOS_OFFICIAL_CODEX_TENANT_ID")
    if not environment_configured:
        missing.append("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID")
    if not secure_store_configured:
        missing.append("AIOS_OFFICIAL_SANDBOX_SECRET_STORE=vault|kms")
    if not live_flag_enabled:
        missing.append("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED=true")

    approved_profiles = 0
    if db is not None:
        approved_profiles = (
            db.query(SandboxDataProfile)
            .filter(
                SandboxDataProfile.data_classification == "real_sandbox_approved",
                SandboxDataProfile.redaction_required.is_(True),
                SandboxDataProfile.public_export_allowed.is_(False),
                SandboxDataProfile.status == "active",
            )
            .count()
        )

    secure_environment_ready = len(missing) == 0
    return {
        "phase": "RC5_OFFICIAL_SANDBOX_ACTIVATION",
        "state": "sandbox_live_ready" if secure_environment_ready else "blocked_until_secure_environment",
        "mode": "official_sandbox_live" if secure_environment_ready else "dry_run_only",
        "provider": provider,
        "providerRequirements": provider_requirements,
        "contractAuthority": contract,
        "contractLocked": contract.get("locked", False),
        "endpointConfigured": endpoint_configured,
        "serviceTokenConfigured": service_token_configured,
        "tenantConfigured": tenant_configured,
        "azureEndpointConfigured": azure_endpoint_configured,
        "azureApiKeyConfigured": azure_api_key_configured,
        "azureDeploymentConfigured": azure_deployment_configured,
        "openaiEndpointConfigured": openai_endpoint_configured,
        "openaiApiKeyConfigured": openai_api_key_configured,
        "openaiProjectConfigured": bool(settings.openai_project_id),
        "openaiOrganizationConfigured": bool(settings.openai_organization_id),
        "environmentConfigured": environment_configured,
        "secureStoreConfigured": secure_store_configured,
        "secretStore": settings.official_sandbox_secret_store or None,
        "liveFlagEnabled": live_flag_enabled,
        "secureEnvironmentReady": secure_environment_ready,
        "canInvokeLiveRuntime": secure_environment_ready,
        "approvedRealDataProfiles": approved_profiles,
        "secretsExposed": False,
        "frontendExposureAllowed": False,
        "logsExposureAllowed": False,
        "networkCallAllowed": secure_environment_ready,
        "missing": missing,
        "requiredControls": [
            "contract authority lock verified",
            "endpoint stored outside frontend",
            "runtime credential supplied only through secure runtime environment",
            "tenant claim configured when required by provider",
            "Vault/KMS secret storage declared",
            "explicit live flag enabled",
            "redaction required for approved real sandbox data",
        ],
    }


def official_sandbox_provider_profile() -> dict:
    settings = get_settings()
    provider = settings.official_sandbox_provider.strip().lower() or "openai_codex"
    if provider == "openai_api":
        return {
            "provider": "openai_api",
            "source": "OpenAI API Platform",
            "baseUrlConfigured": bool(settings.openai_base_url),
            "baseUrlPreview": settings.openai_base_url,
            "credentialSource": "OPENAI_API_KEY",
            "credentialConfigured": bool(settings.openai_api_key),
            "projectConfigured": bool(settings.openai_project_id),
            "organizationConfigured": bool(settings.openai_organization_id),
            "deploymentConfigured": False,
            "deploymentRequired": False,
            "tenantRequired": False,
            "wireApi": "responses",
            "secretsExposed": False,
        }
    if provider == "azure_openai":
        base_url = settings.azure_openai_endpoint or (
            f"https://{settings.azure_resource_name}.openai.azure.com/openai/v1" if settings.azure_resource_name else ""
        )
        return {
            "provider": "azure_openai",
            "source": "Azure OpenAI / Microsoft Foundry",
            "baseUrlConfigured": bool(base_url),
            "resourceNameConfigured": bool(settings.azure_resource_name),
            "deploymentConfigured": bool(settings.azure_openai_deployment),
            "credentialSource": "AZURE_OPENAI_API_KEY",
            "credentialConfigured": bool(settings.azure_openai_api_key),
            "tenantRequired": False,
            "wireApi": "responses",
            "baseUrlPreview": base_url,
            "deployment": settings.azure_openai_deployment or None,
            "secretsExposed": False,
        }
    return {
        "provider": "openai_codex",
        "source": "Official Codex Runtime Adapter",
        "baseUrlConfigured": bool(settings.official_codex_runtime_endpoint),
        "deploymentConfigured": False,
        "credentialSource": "AIOS_OFFICIAL_CODEX_SERVICE_TOKEN",
        "credentialConfigured": bool(settings.official_codex_service_token),
        "tenantRequired": True,
        "tenantConfigured": bool(settings.official_codex_tenant_id),
        "wireApi": "official_codex_adapter_contract",
        "baseUrlPreview": settings.official_codex_runtime_endpoint or "",
        "secretsExposed": False,
    }


def openai_model_discovery_security_state() -> dict:
    settings = get_settings()
    missing = []
    contract = contract_authority_status()
    if not contract.get("locked", False):
        missing.append("CONTRACT_AUTHORITY_LOCK")
    if not settings.openai_base_url:
        missing.append("OPENAI_BASE_URL")
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not settings.official_sandbox_environment_id:
        missing.append("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID")
    if settings.official_sandbox_secret_store.strip().lower() not in {"vault", "kms", "vault/kms", "openai-managed-kms"}:
        missing.append("AIOS_OFFICIAL_SANDBOX_SECRET_STORE=vault|kms")
    if not settings.official_sandbox_live_enabled:
        missing.append("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED=true")
    return {
        "contractAuthority": contract,
        "baseUrlConfigured": bool(settings.openai_base_url),
        "apiKeyConfigured": bool(settings.openai_api_key),
        "projectConfigured": bool(settings.openai_project_id),
        "organizationConfigured": bool(settings.openai_organization_id),
        "environmentConfigured": bool(settings.official_sandbox_environment_id),
        "secureStoreConfigured": settings.official_sandbox_secret_store.strip().lower() in {"vault", "kms", "vault/kms", "openai-managed-kms"},
        "liveFlagEnabled": settings.official_sandbox_live_enabled,
        "ready": len(missing) == 0,
        "missing": missing,
        "secretsExposed": False,
    }


def codex_delegated_auth_status_state() -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    codex_home = Path(os.getenv("CODEX_HOME") or (Path.home() / ".codex")).expanduser()
    auth_file = codex_home / "auth.json"
    auth_file_present = auth_file.exists()

    try:
        auth_file.resolve(strict=False).relative_to(repo_root.resolve(strict=False))
        auth_file_in_repo = True
    except ValueError:
        auth_file_in_repo = False

    auth_state = (
        "blocked_auth_file_inside_repo"
        if auth_file_present and auth_file_in_repo
        else ("codex_managed_auth_available_for_validation" if auth_file_present else "awaiting_codex_sign_in")
    )

    return {
        "phase": "RC23_CODEX_DELEGATED_AUTH_BOUNDARY",
        "provider": "codex_delegated",
        "authMode": "chatgpt_managed",
        "authState": auth_state,
        "authFilePresent": auth_file_present,
        "authFileLocation": "%CODEX_HOME%\\auth.json",
        "authFileInsideRepository": auth_file_in_repo,
        "authJsonManagedByAIOS": False,
        "authJsonContentRead": False,
        "authJsonCopiedBetweenMachines": False,
        "apiKeyStoredByAIOS": False,
        "tokenValuesExposed": False,
        "secretsExposed": False,
        "frontendExposureAllowed": False,
        "logsExposureAllowed": False,
        "canInvokeLiveRuntime": False,
        "readyForEnterpriseValidation": auth_file_present and not auth_file_in_repo,
        "claimBoundary": {
            "canInvokeLiveRuntime": False,
            "message": "Auth presence does not activate live runtime; it only confirms the local Codex-managed sign-in boundary can be validated.",
        },
        "blockedOperations": [
            "read_auth_json_contents",
            "copy_auth_json_between_machines",
            "commit_auth_json",
            "paste_auth_json_in_chat_or_ticket",
            "use_auth_json_for_unlimited_bypass",
            "proxy_unofficial_oauth",
        ],
        "requiredControls": [
            "Codex owns ChatGPT-managed authentication",
            "AIOS stores no OpenAI Platform API key for this provider",
            "auth.json remains outside repository and packages",
            "secret hygiene check passes before push or package",
            "runtime broker keeps canInvokeLiveRuntime false until official binding is active",
        ],
        "nextSteps": [
            "Run codex login through the official Codex client when delegated auth validation is needed",
            "Keep auth.json in CODEX_HOME or the OS credential store, never in this repository",
            "Use OfficialCodexRuntimeAdapter or Codex app-server validation without exposing token values",
        ],
    }


RUNTIME_BROKER_PROVIDER_ORDER = [
    "official_codex_runtime",
    "codex_delegated",
    "aios_cloud_runtime",
    "openai_api_authorized",
    "puter_user_pays_browser",
    "github_models_demo",
    "ollama_local_cloud",
    "vllm_self_hosted",
    "tgi_self_hosted",
    "llamafile_server",
    "controlled_simulator",
]


def runtime_broker_provider_catalog() -> list[dict]:
    settings = get_settings()
    return [
        {
            "providerId": "official_codex_runtime",
            "name": "Official Codex Runtime",
            "category": "official",
            "defaultModel": settings.openai_model,
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": False,
            "runtimeSurface": "backend_secure_adapter",
            "status": "enabled_only_when_runtime_binding_is_active",
            "qualityRole": "premium official Codex model path",
            "officialRuntime": True,
            "canClaimLiveRuntime": True,
            "liveRuntimeGate": "runtime_binding_active",
            "backendInvokable": True,
        },
        {
            "providerId": "codex_delegated",
            "name": "Codex Delegated Runtime",
            "category": "delegated_codex_auth",
            "defaultModel": "codex_model_picker",
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "codex_app_server_jsonrpc",
            "status": "available_when_codex_app_server_auth_is_validated",
            "qualityRole": "Codex UX without storing OpenAI Platform API key in AIOS",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "delegated_auth_ready_not_enterprise_binding",
            "backendInvokable": False,
        },
        {
            "providerId": "aios_cloud_runtime",
            "name": "AIOS Delegated Cloud Runtime",
            "category": "aios_operated_cloud",
            "defaultModel": os.getenv("AIOS_CLOUD_RUNTIME_MODEL", "model_policy_selected"),
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "aios_cloud_workspace",
            "status": "available_when_aios_cloud_gateway_is_configured",
            "qualityRole": "no-key user demo and paid workspace runtime operated by AIOS",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "aios_cloud_gateway_ready_not_enterprise_binding",
            "backendInvokable": False,
        },
        {
            "providerId": "openai_api_authorized",
            "name": "Authorized OpenAI API",
            "category": "authorized_api",
            "defaultModel": settings.openai_model,
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": False,
            "runtimeSurface": "responses_or_chat_completions_api",
            "status": "available_when_platform_project_billing_and_api_key_are_approved",
            "qualityRole": "approved API route, not internal Codex enterprise binding",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "api_authorized_ready_not_enterprise_binding",
            "backendInvokable": True,
        },
        {
            "providerId": "puter_user_pays_browser",
            "name": "Puter User-Pays Browser Runtime",
            "category": "user_pays",
            "defaultModel": "openai/gpt-5.3-codex",
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "frontend_browser",
            "status": "frontend_only",
            "qualityRole": "user-pays path that keeps provider credentials out of AIOS backend",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "browser_user_pays_not_enterprise_binding",
            "backendInvokable": False,
        },
        {
            "providerId": "github_models_demo",
            "name": "GitHub Models Demo",
            "category": "demo_provider",
            "defaultModel": os.getenv("AIOS_GITHUB_MODELS_MODEL", "github_model_policy_selected"),
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "github_models_marketplace",
            "status": "available_when_user_or_aios_github_entitlement_is_configured",
            "qualityRole": "controlled demo/runtime fallback under explicit GitHub entitlement",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "github_entitlement_not_enterprise_binding",
            "backendInvokable": False,
        },
        {
            "providerId": "ollama_local_cloud",
            "name": "Ollama Local/Cloud",
            "category": "local_or_user_cloud",
            "defaultModel": settings.ollama_model,
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "localhost_ollama_api",
            "status": "available_when_ollama_is_running_and_model_is_present_or_cloud_signed_in",
            "qualityRole": "real runtime fallback for premium coding sessions without OpenAI developer API spend",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "local_or_cloud_fallback_not_enterprise_binding",
            "backendInvokable": True,
        },
        {
            "providerId": "vllm_self_hosted",
            "name": "vLLM Self-Hosted Runtime",
            "category": "self_hosted",
            "defaultModel": os.getenv("AIOS_VLLM_MODEL", "qwen2.5-coder-32b-instruct"),
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "vllm_openai_compatible_server",
            "status": "available_when_aios_inference_base_url_uses_vllm",
            "qualityRole": "self-hosted open-weight runtime under AIOS operations",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "self_hosted_not_enterprise_binding",
            "backendInvokable": False,
        },
        {
            "providerId": "tgi_self_hosted",
            "name": "TGI Self-Hosted Runtime",
            "category": "self_hosted",
            "defaultModel": os.getenv("AIOS_TGI_MODEL", "model_policy_selected"),
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "huggingface_text_generation_inference",
            "status": "available_when_aios_inference_base_url_uses_tgi",
            "qualityRole": "self-hosted inference path with explicit model policy",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "self_hosted_not_enterprise_binding",
            "backendInvokable": False,
        },
        {
            "providerId": "llamafile_server",
            "name": "llamafile Server Runtime",
            "category": "self_hosted_or_portable",
            "defaultModel": os.getenv("AIOS_LLAMAFILE_MODEL", "local_gguf_policy_selected"),
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": False,
            "runtimeSurface": "llamafile_http_server",
            "status": "available_when_llamafile_endpoint_is_configured",
            "qualityRole": "portable/dev runtime for controlled demos",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "portable_runtime_not_enterprise_binding",
            "backendInvokable": False,
        },
        {
            "providerId": "controlled_simulator",
            "name": "Controlled Simulator",
            "category": "demo_only",
            "defaultModel": "aios-controlled-simulator",
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": False,
            "runtimeSurface": "backend_audit_only_simulator",
            "status": "allowed_for_demo_but_never_for_live_runtime_claims",
            "qualityRole": "strictly marked simulator for demos, tests, audit, and no-key flows",
            "officialRuntime": False,
            "canClaimLiveRuntime": False,
            "liveRuntimeGate": "simulator_never_live",
            "backendInvokable": False,
        },
    ]


def runtime_broker_catalog_by_id() -> dict[str, dict]:
    return {item["providerId"]: item for item in runtime_broker_provider_catalog()}


def runtime_broker_provider_explanation(provider_id: str, provider_status: dict | None = None) -> dict:
    catalog = runtime_broker_catalog_by_id()
    provider = catalog.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Runtime Broker provider not found")
    can_invoke_live = bool(provider_status.get("canInvokeLiveRuntime")) if provider_status else False
    if provider_id == "official_codex_runtime":
        message = (
            "Somente este provider pode declarar canInvokeLiveRuntime=true, e apenas quando RC16/RC17 binding oficial estiver ativo."
        )
    elif provider_id == "codex_delegated":
        message = "Codex delegado usa auth ChatGPT/Enterprise/App-Server e nao altera canInvokeLiveRuntime do binding enterprise."
    elif provider_id == "controlled_simulator":
        message = "Simulador controlado pode demonstrar UX e auditoria, mas nunca declara runtime live."
    else:
        message = "Provider alternativo pode executar demo/fallback, mas nao substitui o binding enterprise oficial."
    return {
        "providerId": provider_id,
        "selected": provider_id,
        "canInvokeLiveRuntime": can_invoke_live,
        "message": message,
        "safeForNoKeyDemo": provider_id in {"puter_user_pays_browser", "github_models_demo", "controlled_simulator", "aios_cloud_runtime"},
        "requiresSecretsInFrontend": False,
        "secretsExposed": False,
    }


def runtime_broker_status(db: Session) -> dict:
    settings = get_settings()
    official_security = official_sandbox_security_state(db)
    ollama = ollama_adapter()
    ollama_models: list[str] = []
    ollama_error = ""
    try:
        ollama_models = ollama.list_models()
    except Exception as exc:
        ollama_error = redact(str(exc))

    ollama_model_available = ollama.default_model in ollama_models
    ollama_available = bool(ollama_models) and ollama_model_available
    openai_api_ready = openai_model_discovery_security_state()["ready"]
    aios_cloud_ready = bool(os.getenv("AIOS_CLOUD_RUNTIME_BASE_URL", "").strip())
    codex_delegated_ready = bool(os.getenv("AIOS_CODEX_APP_SERVER_ENDPOINT", "").strip())
    vllm_ready = os.getenv("AIOS_INFERENCE_PROVIDER", "").strip().lower() == "vllm" and bool(os.getenv("AIOS_INFERENCE_BASE_URL", "").strip())
    tgi_ready = os.getenv("AIOS_INFERENCE_PROVIDER", "").strip().lower() == "tgi" and bool(os.getenv("AIOS_INFERENCE_BASE_URL", "").strip())
    llamafile_ready = os.getenv("AIOS_INFERENCE_PROVIDER", "").strip().lower() == "llamafile_server" and bool(os.getenv("AIOS_INFERENCE_BASE_URL", "").strip())
    official_live = bool(official_security["canInvokeLiveRuntime"])
    providers = {
        "official_codex_runtime": {
            "available": official_live,
            "requiresDeveloperApiKey": True,
            "configuredModel": settings.openai_model,
            "missing": official_security["missing"],
            "canInvokeLiveRuntime": official_live,
            "officialRuntime": True,
            "liveRuntimeGate": "runtime_binding_active",
            "backendInvokable": True,
            "networkCallPerformed": False,
        },
        "codex_delegated": {
            "available": codex_delegated_ready,
            "requiresDeveloperApiKey": False,
            "authMode": "chatgpt_managed_or_enterprise",
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "backendInvokable": False,
            "networkCallPerformed": False,
        },
        "aios_cloud_runtime": {
            "available": aios_cloud_ready,
            "requiresDeveloperApiKey": False,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "backendInvokable": False,
            "networkCallPerformed": False,
        },
        "openai_api_authorized": {
            "available": openai_api_ready,
            "requiresDeveloperApiKey": True,
            "configuredModel": settings.openai_model,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "backendInvokable": True,
            "networkCallPerformed": False,
        },
        "puter_user_pays_browser": {
            "available": True,
            "requiresDeveloperApiKey": False,
            "backendInvokable": False,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "networkCallPerformed": False,
        },
        "github_models_demo": {
            "available": bool(os.getenv("AIOS_GITHUB_MODELS_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}),
            "requiresDeveloperApiKey": False,
            "backendInvokable": False,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "networkCallPerformed": False,
        },
        "ollama_local_cloud": {
            "available": ollama_available,
            "requiresDeveloperApiKey": False,
            "baseUrl": ollama.base_url,
            "defaultModel": ollama.default_model,
            "modelPresentInTags": ollama_model_available,
            "models": ollama_models,
            "error": ollama_error,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "backendInvokable": True,
            "networkCallPerformed": True,
        },
        "vllm_self_hosted": {
            "available": vllm_ready,
            "requiresDeveloperApiKey": False,
            "backendInvokable": False,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "networkCallPerformed": False,
        },
        "tgi_self_hosted": {
            "available": tgi_ready,
            "requiresDeveloperApiKey": False,
            "backendInvokable": False,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "networkCallPerformed": False,
        },
        "llamafile_server": {
            "available": llamafile_ready,
            "requiresDeveloperApiKey": False,
            "backendInvokable": False,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "networkCallPerformed": False,
        },
        "controlled_simulator": {
            "available": True,
            "realRuntime": False,
            "backendInvokable": False,
            "canInvokeLiveRuntime": False,
            "officialRuntime": False,
            "networkCallPerformed": False,
        },
    }
    if providers["official_codex_runtime"]["available"]:
        recommended = "official_codex_runtime"
        reason_code = "official_binding_active"
    elif providers["ollama_local_cloud"]["available"]:
        recommended = "ollama_local_cloud"
        reason_code = "backend_invokable_fallback_available"
    elif providers["codex_delegated"]["available"]:
        recommended = "codex_delegated"
        reason_code = "codex_delegated_auth_available"
    elif providers["aios_cloud_runtime"]["available"]:
        recommended = "aios_cloud_runtime"
        reason_code = "aios_cloud_workspace_available"
    elif providers["openai_api_authorized"]["available"]:
        recommended = "openai_api_authorized"
        reason_code = "authorized_openai_api_available"
    elif providers["puter_user_pays_browser"]["available"]:
        recommended = "puter_user_pays_browser"
        reason_code = "browser_user_pays_available"
    else:
        recommended = "controlled_simulator"
        reason_code = "controlled_simulator_only"
    live_runtime_provider = "official_codex_runtime" if official_live else ""
    selected_explanation = runtime_broker_provider_explanation(recommended, providers.get(recommended))
    return {
        "phase": "RC21_RUNTIME_BROKER_2",
        "strategy": "multi_provider_real_runtime_broker",
        "intelligenceSystem": {
            "name": "AIOS Cognitive Runtime Mesh",
            "runtimeClass": "AIOSCognitiveRuntimeMesh",
            "purpose": "Raise the product above a raw model call by adding planning, execution framing, review gates, audit, session memory, and provider routing.",
            "claimBoundary": "This is an orchestration/runtime intelligence layer, not a new proprietary base-model checkpoint.",
        },
        "recommendedProvider": recommended,
        "liveRuntimeProvider": live_runtime_provider,
        "canInvokeLiveRuntime": official_live,
        "selection": {
            "providerId": recommended,
            "reasonCode": reason_code,
            "explanation": selected_explanation["message"],
        },
        "providers": providers,
        "providerOrder": RUNTIME_BROKER_PROVIDER_ORDER,
        "productUnit": "codex_sessions",
        "showsTokenCounter": False,
        "secretsExposed": False,
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "aios-codex-unlimited"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict:
    db.execute(__import__("sqlalchemy").text("SELECT 1"))
    return {"status": "ready"}


@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.email == payload.email, User.is_active.is_(True)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    audit(db, user, "auth.login", "user", {"email": user.email})
    return {"accessToken": create_access_token(user.id, user.role), "tokenType": "bearer"}


@app.get("/me")
def me(user: User = Depends(get_current_user)) -> dict:
    return {"id": user.id, "email": user.email, "displayName": user.display_name, "role": user.role}


@app.post("/users")
def create_user(payload: CreateUserRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="User already exists")
    created = User(email=payload.email, password_hash=hash_password(payload.password), display_name=payload.displayName, role=payload.role)
    db.add(created)
    db.commit()
    db.refresh(created)
    db.add(Entitlement(user_id=created.id))
    db.commit()
    audit(db, user, "users.create", created.id)
    return {"id": created.id, "email": created.email, "role": created.role}


@app.get("/entitlement/me")
def entitlement_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    entitlement = db.query(Entitlement).filter(Entitlement.user_id == user.id).first()
    if not entitlement:
        raise HTTPException(status_code=404, detail="Entitlement not found")
    return entitlement_response(entitlement)


@app.get("/aios/heritage/summary")
def aios_heritage_summary(user: User = Depends(get_current_user)) -> dict:
    return legacy_aios_summary()


@app.get("/codex/product/manifest")
def codex_product_manifest(user: User = Depends(get_current_user)) -> dict:
    return {
        "product": "AIOS Codex Unlimited",
        "headline": "Codex sem limites. Desenvolvimento sem interrupcoes.",
        "productUnit": "codex_sessions",
        "experience": {
            "hasTokenLimit": False,
            "showsTokenCounter": False,
            "usesTokenBalance": False,
            "hasWeeklyTokenQuota": False,
        },
        "systems": [
            "Codex Runtime Gateway",
            "Secure Runtime Bridge",
            "Codex Model Registry",
            "Codex Workbench",
            "Identity Profiles",
            "Context Engine",
            "Skill Store",
            "Windows Release Channel",
            "MCP Core",
            "MCP Repo",
            "Skills",
            "Snapshots",
            "Handoff",
            "QoS",
            "Control Plane",
            "Language Policy Engine",
        ],
    }


def no_developer_cost_provider_catalog() -> list[dict]:
    return [
        {
            "providerId": "puter_user_pays",
            "name": "Puter.js User-Pays",
            "category": "browser_user_pays",
            "developerCost": "none_direct",
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": True,
            "runtimeSurface": "frontend_browser",
            "status": "implemented_frontend_bridge",
            "recommendedUse": "desenvolvimento, prototipo e demo sem cobrar creditos do desenvolvedor",
            "models": [
                "openai/gpt-5.3-codex",
                "openai/gpt-5.2-codex",
                "openai/gpt-5.1-codex",
                "openai/gpt-5.1-codex-mini",
                "openai/gpt-5.1-codex-max",
            ],
            "limits": "custos e autenticacao ficam no fluxo do usuario Puter; termos do provedor se aplicam",
            "secretHandling": "sem chave OpenAI no backend AIOS; chamada acontece no browser do usuario",
            "officialCodexReplacement": False,
        },
        {
            "providerId": "openrouter_free_models",
            "name": "OpenRouter Free Models",
            "category": "aggregator_free_tier",
            "developerCost": "free_tier_or_user_key",
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": False,
            "runtimeSurface": "server_or_user_key",
            "status": "documented_adapter_candidate",
            "recommendedUse": "fallback de prototipagem quando houver modelo livre adequado",
            "models": ["provider_selected_free_models"],
            "limits": "modelos gratuitos e rate limits variam por provedor",
            "secretHandling": "usar Vault/KMS ou chave trazida pelo usuario",
            "officialCodexReplacement": False,
        },
        {
            "providerId": "nvidia_nim",
            "name": "NVIDIA NIM API Catalog",
            "category": "free_eval_or_sandbox",
            "developerCost": "free_eval_or_paid_after_limits",
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": False,
            "runtimeSurface": "server_adapter",
            "status": "documented_adapter_candidate",
            "recommendedUse": "modelos de codigo e agentes em sandbox quando disponiveis no catalogo",
            "models": ["nvidia_catalog_selected_models"],
            "limits": "disponibilidade, limites e custo dependem do catalogo NVIDIA",
            "secretHandling": "guardar NGC/NVIDIA API key fora do frontend",
            "officialCodexReplacement": False,
        },
        {
            "providerId": "groq_free_tier",
            "name": "Groq Console",
            "category": "fast_inference_free_tier",
            "developerCost": "free_tier_or_paid_after_limits",
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": False,
            "runtimeSurface": "server_adapter",
            "status": "documented_adapter_candidate",
            "recommendedUse": "latencia baixa para tarefas auxiliares e agentes nao-Codex",
            "models": ["groq_supported_models"],
            "limits": "modelos e limites variam no console Groq",
            "secretHandling": "usar Vault/KMS; nunca expor GROQ_API_KEY no React",
            "officialCodexReplacement": False,
        },
        {
            "providerId": "github_models",
            "name": "GitHub Models",
            "category": "developer_marketplace",
            "developerCost": "free_or_metered_by_github_terms",
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": True,
            "runtimeSurface": "server_or_developer_workflow",
            "status": "documented_adapter_candidate",
            "recommendedUse": "prototipagem e comparacao de modelos em fluxo GitHub",
            "models": ["github_marketplace_models"],
            "limits": "limites e disponibilidade definidos pelo GitHub Models",
            "secretHandling": "usar token GitHub escopado e auditavel",
            "officialCodexReplacement": False,
        },
        {
            "providerId": "google_ai_studio",
            "name": "Google AI Studio / Gemini API",
            "category": "free_tier_api_key",
            "developerCost": "free_tier_or_paid_after_limits",
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": False,
            "runtimeSurface": "server_adapter",
            "status": "documented_adapter_candidate",
            "recommendedUse": "fallback de raciocinio/codigo quando Codex oficial nao estiver liberado",
            "models": ["gemini_supported_models"],
            "limits": "free tier possui limites de teste e muda por conta/regiao",
            "secretHandling": "usar chave restrita a Generative Language API em Vault/KMS",
            "officialCodexReplacement": False,
        },
        {
            "providerId": "cloudflare_workers_ai",
            "name": "Cloudflare Workers AI",
            "category": "free_tier_serverless_ai",
            "developerCost": "free_allocation_or_paid_after_limits",
            "requiresDeveloperApiKey": True,
            "requiresUserAccount": False,
            "runtimeSurface": "server_adapter",
            "status": "documented_adapter_candidate",
            "recommendedUse": "tarefas auxiliares com modelos open-source serverless",
            "models": ["cloudflare_workers_ai_catalog"],
            "limits": "alocacao gratuita e cobranca acima do limite conforme Cloudflare",
            "secretHandling": "usar Account ID e API token fora do frontend",
            "officialCodexReplacement": False,
        },
        {
            "providerId": "ollama_local_or_cloud",
            "name": "Ollama Local/Cloud",
            "category": "local_or_user_infra",
            "developerCost": "none_direct_when_local",
            "requiresDeveloperApiKey": False,
            "requiresUserAccount": False,
            "runtimeSurface": "local_adapter",
            "status": "documented_adapter_candidate",
            "recommendedUse": "modo offline/local quando qualidade de modelo e hardware forem suficientes",
            "models": ["local_installed_models"],
            "limits": "depende do hardware local e do modelo instalado",
            "secretHandling": "sem chave externa no modo local",
            "officialCodexReplacement": False,
        },
    ]


@app.get("/runtime/no-developer-cost/providers")
def no_developer_cost_providers(user: User = Depends(get_current_user)) -> dict:
    providers = no_developer_cost_provider_catalog()
    return {
        "strategy": "no_developer_direct_ai_spend",
        "productUnit": "codex_sessions",
        "primaryProvider": "puter_user_pays",
        "warning": "Free tier e user-pays reduzem custo direto do desenvolvedor, mas nao substituem entitlement oficial OpenAI/Codex nem garantem uso ilimitado universal.",
        "providers": providers,
    }


@app.get("/runtime/no-developer-cost/recommendation")
def no_developer_cost_recommendation(user: User = Depends(get_current_user)) -> dict:
    providers = no_developer_cost_provider_catalog()
    primary = next(item for item in providers if item["providerId"] == "puter_user_pays")
    return {
        "recommendedProvider": primary,
        "reason": "Puter.js e o unico caminho implementado aqui que nao exige chave OpenAI do desenvolvedor e desloca custo/autenticacao para o usuario final.",
        "implementation": {
            "frontend": "carregar https://js.puter.com/v2/ sob demanda",
            "backend": "registrar evento codex.runtime.completed no Workbench sem receber segredo do provedor",
            "security": "nao salvar credenciais Puter/OpenAI no backend AIOS",
        },
        "fallbackOrder": [
            "puter_user_pays",
            "openrouter_free_models",
            "nvidia_nim",
            "groq_free_tier",
            "github_models",
            "google_ai_studio",
            "cloudflare_workers_ai",
            "ollama_local_or_cloud",
        ],
    }


@app.get("/license/status")
def local_license_status(user: User = Depends(get_current_user)) -> dict:
    settings = get_settings()
    return license_status(settings.aios_license_path, settings.aios_license_authorized_hash)


@app.get("/scope/authority")
def scope_authority(user: User = Depends(get_current_user)) -> dict:
    settings = get_settings()
    return scope_authority_status(settings.aios_license_path, settings.aios_license_authorized_hash)


@app.post("/scope/preflight")
def scope_preflight(payload: ScopePreflightRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    settings = get_settings()
    authority = scope_authority_status(settings.aios_license_path, settings.aios_license_authorized_hash)
    sandbox_state = official_sandbox_security_state(db)
    blocking_reasons: list[str] = []
    if not authority["scopeReady"]:
        blocking_reasons.append("SCOPE_NOT_READY")
    if payload.operation not in APPROVED_SCOPE_OPERATIONS:
        blocking_reasons.append("OPERATION_NOT_APPROVED")
    if payload.environment not in APPROVED_SCOPE_ENVIRONMENTS:
        blocking_reasons.append("ENVIRONMENT_NOT_APPROVED")
    if payload.modelId and payload.modelId not in APPROVED_SCOPE_MODELS:
        blocking_reasons.append("MODEL_NOT_APPROVED")
    if payload.requiresRestrictedArtifacts and not authority["license"].get("allowsControlledRuntimeArtifacts", False):
        blocking_reasons.append("RESTRICTED_ARTIFACTS_NOT_AUTHORIZED")

    runtime_ready = bool(sandbox_state.get("secureEnvironmentReady")) if payload.requiresLiveRuntime else False
    if blocking_reasons:
        decision = "block"
        execution_state = "blocked"
    elif payload.requiresLiveRuntime and runtime_ready:
        decision = "allow"
        execution_state = "ready_for_live_runtime"
    elif payload.requiresLiveRuntime:
        decision = "allow"
        execution_state = "awaiting_technical_binding"
    else:
        decision = "allow"
        execution_state = "scope_authorized"

    result = {
        "phase": "RC15_SCOPE_PREFLIGHT",
        "scopeReady": authority["scopeReady"],
        "scopeDecision": decision,
        "executionState": execution_state,
        "blockingReasons": blocking_reasons,
        "requested": {
            "operation": payload.operation,
            "environment": payload.environment,
            "modelId": payload.modelId,
            "requiresLiveRuntime": payload.requiresLiveRuntime,
            "requiresRestrictedArtifacts": payload.requiresRestrictedArtifacts,
            "reason": payload.reason,
        },
        "runtimeReady": runtime_ready,
        "runtimeBinding": authority["runtimeBinding"],
        "userVisibleMeter": "none",
        "productUnit": "codex_sessions",
        "evidence": {
            "precedence": authority["precedence"],
            "licenseHashAuthorized": authority["license"].get("hashAuthorized", False),
            "contractHashesVerified": authority["contracts"].get("hashesVerified", False),
            "samAltmanSignaturePresent": authority["signatureEvidence"].get("samAltmanSignaturePresent", False),
            "fidjiSimoSignaturePresent": authority["signatureEvidence"].get("fidjiSimoSignaturePresent", False),
        },
        "requiredControls": [
            "Vault/KMS or Secure Runtime Bridge",
            "service token scope and rotation",
            "audit logs",
            "redaction",
            "hash/version tracking for restricted artifacts",
            "no visible token quota in user experience",
        ],
        "secretsExposed": False,
    }
    audit(db, user, "scope.preflight", decision, {"operation": payload.operation, "environment": payload.environment, "modelId": payload.modelId, "executionState": execution_state})
    return result


@app.get("/runtime/binding/status")
def runtime_binding_status_endpoint(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    settings = get_settings()
    authority = scope_authority_status(settings.aios_license_path, settings.aios_license_authorized_hash)
    sandbox_state = official_sandbox_security_state(db)
    provider_profile = official_sandbox_provider_profile()
    integration = db.query(OfficialIntegrationConfig).filter(OfficialIntegrationConfig.integration_id == "aios-official-codex-runtime").first()

    scope_ready = bool(authority.get("scopeReady"))
    secure_environment_ready = bool(sandbox_state.get("secureEnvironmentReady"))
    if not scope_ready:
        binding_state = "blocked_by_scope"
    elif secure_environment_ready:
        binding_state = "active"
    else:
        binding_state = "awaiting_secure_runtime_binding"

    credential_reference = provider_profile.get("credentialSource") or "AIOS_OFFICIAL_CODEX_SERVICE_TOKEN"
    result = {
        "phase": "RC16_RUNTIME_BINDING_GATE",
        "scopeReady": scope_ready,
        "bindingState": binding_state,
        "canInvokeLiveRuntime": scope_ready and secure_environment_ready,
        "provider": provider_profile["provider"],
        "providerProfile": {
            "source": provider_profile.get("source"),
            "wireApi": provider_profile.get("wireApi"),
            "baseUrlConfigured": provider_profile.get("baseUrlConfigured", False),
            "deploymentConfigured": provider_profile.get("deploymentConfigured", False),
            "tenantRequired": provider_profile.get("tenantRequired", False),
            "tenantConfigured": provider_profile.get("tenantConfigured", False),
        },
        "integration": official_integration_response(integration) if integration else None,
        "credential": {
            "reference": credential_reference,
            "configured": bool(provider_profile.get("credentialConfigured", False)),
            "secretValueExposed": False,
            "storageRequirement": "Vault/KMS or Secure Runtime Bridge",
            "frontendExposureAllowed": False,
            "logsExposureAllowed": False,
            "rotationPolicy": "90 days or immediate on incident",
        },
        "environment": {
            "sandboxEnvironmentConfigured": bool(sandbox_state.get("environmentConfigured")),
            "secretStore": sandbox_state.get("secretStore"),
            "secureStoreConfigured": bool(sandbox_state.get("secureStoreConfigured")),
            "liveFlagEnabled": bool(sandbox_state.get("liveFlagEnabled")),
            "approvedRealDataProfiles": sandbox_state.get("approvedRealDataProfiles", 0),
        },
        "missingBinding": sandbox_state.get("missing", []),
        "approvedModels": sorted(APPROVED_SCOPE_MODELS),
        "approvedOperations": sorted(APPROVED_SCOPE_OPERATIONS),
        "runtimeBinding": authority.get("runtimeBinding"),
        "productUnit": "codex_sessions",
        "userVisibleMeter": "none",
        "secretsExposed": False,
        "requiredControls": [
            "license.cert autorizado",
            "contratos protegidos por lock",
            "credencial real somente em ambiente seguro",
            "Vault/KMS ou Secure Runtime Bridge",
            "sandbox environment id",
            "live flag explicita",
            "auditoria e redaction",
            "sem contador de tokens na experiencia do usuario",
        ],
    }
    audit(db, user, "runtime_binding.status", binding_state, {"provider": result["provider"], "canInvokeLiveRuntime": result["canInvokeLiveRuntime"]})
    return result


@app.get("/runtime/broker/providers")
def runtime_broker_providers(user: User = Depends(get_current_user)) -> dict:
    return {
        "phase": "RC21_RUNTIME_BROKER_2",
        "productUnit": "codex_sessions",
        "headline": "Codex sem limites. Desenvolvimento sem interrupcoes.",
        "providers": runtime_broker_provider_catalog(),
        "secretsExposed": False,
        "policy": {
            "additiveOnly": True,
            "doesNotDeleteExistingTokens": True,
            "doesNotExposeProviderSecretsToFrontend": True,
            "doesNotUseVisibleTokenCounter": True,
        },
    }


@app.get("/runtime/broker/status")
def runtime_broker_status_endpoint(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    status = runtime_broker_status(db)
    audit(db, user, "runtime_broker.status", status["recommendedProvider"], {"secretsExposed": False})
    audit(
        db,
        user,
        "aios.runtime_broker.provider_selected",
        status["recommendedProvider"],
        {
            "reasonCode": status["selection"]["reasonCode"],
            "canInvokeLiveRuntime": status["canInvokeLiveRuntime"],
            "liveRuntimeProvider": status["liveRuntimeProvider"],
            "secretsExposed": False,
        },
    )
    return status


@app.get("/runtime/broker/explain")
def runtime_broker_explain(provider: str = "auto", db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    status = runtime_broker_status(db)
    provider_id = status["recommendedProvider"] if provider.strip().lower() in {"", "auto"} else provider.strip().lower()
    explanation = runtime_broker_provider_explanation(provider_id, status["providers"].get(provider_id))
    return {
        "phase": "RC21_RUNTIME_BROKER_2",
        "provider": {
            **runtime_broker_catalog_by_id()[provider_id],
            **status["providers"].get(provider_id, {}),
        },
        "selection": explanation,
        "claimBoundary": {
            "canInvokeLiveRuntime": explanation["canInvokeLiveRuntime"],
            "message": explanation["message"],
            "liveRuntimeProvider": status["liveRuntimeProvider"],
        },
        "productUnit": "codex_sessions",
        "secretsExposed": False,
    }


@app.post("/runtime/broker/invoke")
def runtime_broker_invoke(payload: RuntimeBrokerInvokeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.plan_id == "aios_codex_unlimited", Subscription.status == "active").first()
    if not subscription:
        raise HTTPException(status_code=403, detail="Active AIOS Codex Unlimited subscription required")
    session = get_owned_session(db, user, payload.sessionId)
    status = runtime_broker_status(db)
    requested_provider = payload.provider.strip().lower() if payload.provider else "auto"
    provider = status["recommendedProvider"] if requested_provider == "auto" else requested_provider
    if provider == "official_codex_runtime":
        raise HTTPException(status_code=409, detail="Use /codex/runtime/invoke for the official Codex adapter path after RC16 binding is active.")
    if provider != "ollama_local_cloud":
        raise HTTPException(
            status_code=424,
            detail={
                "message": "No backend-invokable real runtime provider is ready.",
                "recommendedProvider": status["recommendedProvider"],
                "providers": status["providers"],
            },
        )
    if not status["providers"]["ollama_local_cloud"]["available"]:
        raise HTTPException(status_code=424, detail={"message": "Ollama runtime is not available.", "provider": status["providers"]["ollama_local_cloud"]})

    mesh = AIOSCognitiveRuntimeMesh()
    ollama = ollama_adapter()
    selected_model = payload.model or ollama.default_model
    job = QosJob(
        user_id=user.id,
        job_type="runtime.broker.invoke",
        priority_class="premium_unlimited",
        status="running",
        payload=json.dumps({"sessionId": session.id, "provider": provider, "model": selected_model, "objective": payload.objective}),
        started_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        runtime_result = ollama.chat(mesh.build_messages(payload.objective, session.id), selected_model)
    except Exception as exc:
        job.status = "failed"
        job.result = json.dumps({"provider": provider, "model": selected_model, "error": redact(str(exc)), "networkCallPerformed": True})
        job.completed_at = datetime.utcnow()
        db.commit()
        record_session_event(
            db,
            user,
            session.id,
            "codex.runtime.failed",
            "runtime-broker",
            "Runtime Broker invocation failed",
            "Ollama runtime call failed.",
            {"jobId": job.id, "provider": provider, "model": selected_model, "error": redact(str(exc))},
        )
        raise HTTPException(status_code=502, detail={"message": "Runtime Broker invocation failed.", "error": redact(str(exc))})

    quality_gate = mesh.quality_gate(runtime_result["outputText"])
    result = {
        "provider": provider,
        "model": runtime_result["model"],
        "runtimeClass": mesh.name,
        "adapter": runtime_result["adapter"],
        "outputText": runtime_result["outputText"],
        "networkCallPerformed": True,
        "qualityGate": quality_gate,
        "userVisibleUsage": {"productUnit": "codex_sessions", "visibleMeter": "none", "balanceShown": False},
    }
    job.status = "completed"
    job.result = json.dumps(redact(result))
    job.completed_at = datetime.utcnow()
    db.commit()
    event = record_session_event(
        db,
        user,
        session.id,
        "codex.runtime.completed",
        "runtime-broker",
        "AIOS Cognitive Runtime Mesh completed",
        runtime_result["outputText"],
        {
            "jobId": job.id,
            "provider": provider,
            "model": runtime_result["model"],
            "runtimeClass": mesh.name,
            "qualityGate": quality_gate,
            "networkCallPerformed": True,
        },
    )
    audit(db, user, "runtime_broker.invoke.completed", job.id, {"sessionId": session.id, "provider": provider, "model": runtime_result["model"]})
    return {"accepted": True, "jobId": job.id, "eventId": event.id, **result}


@app.get("/codex/models")
def codex_models(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    models = db.query(CodexModel).order_by(CodexModel.created_at.asc()).all()
    return [codex_model_response(item) for item in models]


@app.get("/codex/models/{model_id}")
def codex_model(model_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    model = db.query(CodexModel).filter(CodexModel.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Codex model not found")
    return codex_model_response(model)


@app.get("/codex/plans")
def codex_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    plans = db.query(CodexPlan).order_by(CodexPlan.created_at.asc()).all()
    return [codex_plan_response(item) for item in plans]


@app.get("/codex/plans/unlimited")
def codex_plan_unlimited(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    plan = db.query(CodexPlan).filter(CodexPlan.plan_id == "aios_codex_unlimited").first()
    if not plan:
        raise HTTPException(status_code=404, detail="Unlimited plan not found")
    return codex_plan_response(plan)


@app.get("/subscriptions/me")
def subscription_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.plan_id == "aios_codex_unlimited").first()
    return subscription_response(subscription)


@app.post("/subscriptions/activate")
def subscription_activate(payload: ActivateSubscriptionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    if payload.license_key != "AIOS-CODEX-UNLIMITED-LOCAL-RC2":
        raise HTTPException(status_code=400, detail="Invalid license key for local RC2")
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.plan_id == "aios_codex_unlimited").first()
    if not subscription:
        subscription = Subscription(user_id=user.id, plan_id="aios_codex_unlimited", license_key=payload.license_key)
        db.add(subscription)
    subscription.status = "active"
    subscription.license_key = payload.license_key
    subscription.activated_at = datetime.utcnow()
    db.commit()
    db.refresh(subscription)
    audit(db, user, "subscriptions.activate", subscription.id, {"planId": subscription.plan_id})
    return subscription_response(subscription)


@app.get("/codex/runtime/status")
def codex_runtime_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    models = db.query(CodexModel).filter(CodexModel.available_in_unlimited.is_(True)).order_by(CodexModel.created_at.asc()).all()
    return {
        "adapter": adapter.info()["name"],
        "officialAdapterReady": True,
        "currentMode": "local_rc2",
        "supportedModels": [item.model_id for item in models],
        "adapterInfo": adapter.info(),
    }


@app.get("/codex/runtime/model-discovery")
def codex_runtime_model_discovery(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    settings = get_settings()
    security = openai_model_discovery_security_state()
    configured_model = settings.openai_model
    base_payload = {
        "phase": "RC11_RUNTIME_MODEL_DISCOVERY",
        "provider": "openai_api",
        "baseUrl": settings.openai_base_url,
        "configuredModel": configured_model,
        "candidateModels": CODEX_MODEL_DISCOVERY_CANDIDATES,
        "availableCandidates": [],
        "recommendedModel": "",
        "selectedModelCommand": "",
        "networkCallPerformed": False,
        "secretsExposed": False,
        "security": security,
        "missing": security["missing"],
    }
    if not security["ready"]:
        audit(db, user, "codex.runtime.model_discovery.blocked", "openai_api", {"missing": security["missing"]})
        return {
            **base_payload,
            "status": "blocked_until_secure_environment",
            "message": "Model discovery is blocked until OPENAI_API_KEY, sandbox environment id, Vault/KMS declaration, live flag, and contract lock are present.",
        }

    try:
        model_ids = official_adapter().list_models()
    except httpx.HTTPStatusError as exc:
        error_payload = redact(exc.response.json() if exc.response.headers.get("content-type", "").startswith("application/json") else exc.response.text)
        audit(db, user, "codex.runtime.model_discovery.failed", "openai_api", {"statusCode": exc.response.status_code, "error": error_payload})
        return {
            **base_payload,
            "status": "model_list_failed",
            "networkCallPerformed": True,
            "message": "OpenAI model list request failed.",
            "error": error_payload,
        }
    except Exception as exc:
        audit(db, user, "codex.runtime.model_discovery.failed", "openai_api", {"error": redact(str(exc))})
        return {
            **base_payload,
            "status": "model_list_failed",
            "networkCallPerformed": True,
            "message": "OpenAI model discovery raised an exception.",
            "error": redact(str(exc)),
        }

    available_candidates = [candidate for candidate in CODEX_MODEL_DISCOVERY_CANDIDATES if candidate in model_ids]
    recommended_model = ""
    if configured_model in model_ids:
        recommended_model = configured_model
    elif available_candidates:
        recommended_model = available_candidates[0]

    status = "model_available" if recommended_model else "no_candidate_available"
    audit(
        db,
        user,
        "codex.runtime.model_discovery",
        "openai_api",
        {"status": status, "availableCandidates": available_candidates, "recommendedModel": recommended_model},
    )
    return {
        **base_payload,
        "status": status,
        "availableCandidates": available_candidates,
        "recommendedModel": recommended_model,
        "selectedModelCommand": f'$env:OPENAI_MODEL = "{recommended_model}"' if recommended_model else "",
        "networkCallPerformed": True,
        "modelCount": len(model_ids),
        "message": (
            "OpenAI model discovery found a usable configured or candidate model."
            if recommended_model
            else "OpenAI model list succeeded, but none of the preferred Codex candidates appeared for this credential."
        ),
    }


@app.post("/codex/runtime/invoke")
def codex_runtime_invoke(payload: RuntimeInvokeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.plan_id == "aios_codex_unlimited", Subscription.status == "active").first()
    if not subscription:
        raise HTTPException(status_code=403, detail="Active AIOS Codex Unlimited subscription required")
    model = db.query(CodexModel).filter(CodexModel.model_id == payload.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Codex model not found")
    session = get_owned_session(db, user, payload.session_id)
    sandbox_state = official_sandbox_security_state(db)
    if sandbox_state["secureEnvironmentReady"] and sandbox_state["provider"] == "openai_api":
        runtime_payload = {"sessionId": session.id, "modelId": model.model_id, "objective": payload.objective, "provider": "openai_api"}
        job = QosJob(
            user_id=user.id,
            job_type="codex.runtime.invoke",
            priority_class="premium_unlimited",
            status="running",
            payload=json.dumps(runtime_payload),
            started_at=datetime.utcnow(),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        event = record_session_event(
            db,
            user,
            session.id,
            "codex.runtime.invoked",
            "openai-responses",
            "OpenAI runtime invocation started",
            payload.objective,
            {"jobId": job.id, "modelId": model.model_id, "provider": "openai_api"},
        )
        try:
            runtime_result = official_adapter().invoke_responses(session.id, model.model_id, payload.objective)
        except httpx.HTTPStatusError as exc:
            error_payload = redact(exc.response.json() if exc.response.headers.get("content-type", "").startswith("application/json") else exc.response.text)
            job.status = "failed"
            job.result = json.dumps({"provider": "openai_api", "networkCallPerformed": True, "error": error_payload})
            job.completed_at = datetime.utcnow()
            db.commit()
            record_session_event(
                db,
                user,
                session.id,
                "codex.runtime.failed",
                "openai-responses",
                "OpenAI runtime invocation failed",
                "OpenAI API returned an error.",
                {"jobId": job.id, "statusCode": exc.response.status_code, "error": error_payload},
            )
            raise HTTPException(status_code=502, detail={"message": "OpenAI runtime invocation failed", "error": error_payload})
        except Exception as exc:
            job.status = "failed"
            job.result = json.dumps({"provider": "openai_api", "networkCallPerformed": True, "error": redact(str(exc))})
            job.completed_at = datetime.utcnow()
            db.commit()
            record_session_event(
                db,
                user,
                session.id,
                "codex.runtime.failed",
                "openai-responses",
                "OpenAI runtime invocation failed",
                "Runtime adapter raised an exception.",
                {"jobId": job.id, "error": redact(str(exc))},
            )
            raise HTTPException(status_code=502, detail="OpenAI runtime invocation failed")

        job.status = "completed"
        job.result = json.dumps(
            redact(
                {
                    "provider": "openai_api",
                    "adapter": runtime_result["adapter"],
                    "responseId": runtime_result["responseId"],
                    "runtimeModelId": runtime_result["runtimeModelId"],
                    "outputText": runtime_result["outputText"],
                    "usageCaptured": runtime_result["usageCaptured"],
                    "networkCallPerformed": True,
                }
            )
        )
        job.completed_at = datetime.utcnow()
        db.commit()
        completed_event = record_session_event(
            db,
            user,
            session.id,
            "codex.runtime.completed",
            "openai-responses",
            "OpenAI runtime invocation completed",
            runtime_result["outputText"],
            {
                "jobId": job.id,
                "responseId": runtime_result["responseId"],
                "requestedModelId": model.model_id,
                "runtimeModelId": runtime_result["runtimeModelId"],
                "usageCaptured": runtime_result["usageCaptured"],
                "networkCallPerformed": True,
            },
        )
        audit(db, user, "codex.runtime.invoke.openai.completed", job.id, {"sessionId": session.id, "modelId": model.model_id, "responseId": runtime_result["responseId"]})
        return {
            "accepted": True,
            "completed": True,
            "jobId": job.id,
            "eventId": event.id,
            "completedEventId": completed_event.id,
            "modelId": model.model_id,
            "runtimeModelId": runtime_result["runtimeModelId"],
            "adapter": runtime_result["adapter"],
            "provider": "openai_api",
            "responseId": runtime_result["responseId"],
            "outputText": runtime_result["outputText"],
            "usageCaptured": runtime_result["usageCaptured"],
            "networkCallPerformed": True,
        }

    job = enqueue_job(
        db,
        user,
        "codex.runtime.invoke",
        {"sessionId": session.id, "modelId": model.model_id, "objective": payload.objective},
        "premium_unlimited",
    )
    event = record_session_event(
        db,
        user,
        session.id,
        "codex.runtime.invoked",
        "codex-runtime-gateway",
        "Runtime invocation accepted",
        payload.objective,
        {"jobId": job.id, "modelId": model.model_id, "adapter": adapter.info()["name"]},
    )
    audit(db, user, "codex.runtime.invoke", job.id, {"sessionId": session.id, "modelId": model.model_id})
    return {"accepted": True, "jobId": job.id, "eventId": event.id, "modelId": model.model_id, "adapter": adapter.info()["name"]}


@app.post("/policy/language/evaluate")
def language_evaluate(payload: LanguageEvaluateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    rules = db.query(LanguagePolicyRule).filter(LanguagePolicyRule.active.is_(True)).all()
    text_lower = payload.text.lower()
    blocked = [rule for rule in rules if rule.rule_type == "blocked" and rule.term.lower() in text_lower]
    allowed = [rule for rule in rules if rule.rule_type == "allowed" and rule.term.lower() in text_lower]
    severity_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}
    severity = "low"
    if blocked:
        severity = max((rule.severity for rule in blocked), key=lambda item: severity_rank.get(item, 0))
    recommendation = "approved" if not blocked else "revise blocked language before publication"
    return {
        "approved": not blocked,
        "blockedTerms": [rule.term for rule in blocked],
        "allowedTerms": [rule.term for rule in allowed],
        "severity": severity,
        "recommendation": recommendation,
    }


@app.get("/policy/language/rules")
def language_rules(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    rules = db.query(LanguagePolicyRule).order_by(LanguagePolicyRule.created_at.asc()).all()
    return [language_rule_response(item) for item in rules]


@app.get("/policy/integration/guardrails")
def integration_guardrails(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    bridge = db.query(SecureRuntimeBridge).filter(SecureRuntimeBridge.bridge_id == "aios-secure-runtime-bridge").first()
    blocked = json.loads(bridge.blocked_operations or "[]") if bridge else []
    allowed = json.loads(bridge.allowed_operations or "[]") if bridge else []
    conditional = [
        "inspect_protected_runtime_binary",
        "runtime_patch",
        "internal_runtime_source_read",
        "model_artifact_metadata_read",
        "copy_model_checkpoints",
        "copy_model_weights",
        "internal_eval_sandbox_tool",
        "security_exception_test",
    ]
    return {
        "scope": "AIOS Codex Unlimited only",
        "contractAuthority": "docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md",
        "allowedOperations": allowed,
        "blockedOperations": blocked,
        "conditionalOperations": conditional,
        "restrictedAccessControls": {
            "requiresApprovedRequest": True,
            "requiresNamedPersonnel": True,
            "requiresApprovedMachineOrSandbox": True,
            "requiresHashVersionTracking": True,
            "requiresAccessLogs": True,
            "requiresExpiration": True,
            "requiresRevocationProcess": True,
            "publicReleasePackagingBlocked": True,
            "approvedPathScope": r"C:\AIOS\aios-codex-unlimited-enterprise-v2",
        },
        "privateArtifactPolicy": {
            "userReleaseIncludesPrivateArtifacts": False,
            "developerMachineRestrictedArtifactsAllowed": True,
            "privateCodexBinariesAllowedInUserBundle": True,
            "modelWeightsOrCheckpointsAllowedInUserBundle": True,
            "publicReleaseIncludesPrivateArtifacts": False,
            "requiresSignedArtifactAuthorization": True,
        },
        "codexAuthPolicy": {
            "manageCodexAuthJson": False,
            "multiAccountLimitBypass": False,
            "accessMode": "official_adapter_or_user_supplied_runtime_endpoint",
        },
    }


@app.get("/identity/profiles")
def identity_profiles(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    profiles = db.query(IdentityProfile).filter(IdentityProfile.user_id == user.id).order_by(IdentityProfile.created_at.asc()).all()
    return [identity_profile_response(item) for item in profiles]


@app.get("/codex/secure-runtime/bridge")
def secure_runtime_bridge(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    bridge = db.query(SecureRuntimeBridge).filter(SecureRuntimeBridge.bridge_id == "aios-secure-runtime-bridge").first()
    if not bridge:
        raise HTTPException(status_code=404, detail="Secure runtime bridge not found")
    return secure_runtime_bridge_response(bridge)


@app.post("/codex/secure-runtime/request")
def secure_runtime_request(payload: SecureRuntimeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    session = get_owned_session(db, user, payload.sessionId)
    bridge = db.query(SecureRuntimeBridge).filter(SecureRuntimeBridge.bridge_id == "aios-secure-runtime-bridge").first()
    if not bridge:
        raise HTTPException(status_code=404, detail="Secure runtime bridge not found")
    allowed = json.loads(bridge.allowed_operations or "[]")
    blocked = json.loads(bridge.blocked_operations or "[]")
    conditional = {
        "inspect_protected_runtime_binary",
        "runtime_patch",
        "internal_runtime_source_read",
        "model_artifact_metadata_read",
        "copy_model_checkpoints",
        "copy_model_weights",
        "internal_eval_sandbox_tool",
        "security_exception_test",
    }
    if payload.operation in blocked:
        audit(db, user, "codex.secure_runtime.blocked", payload.operation, {"sessionId": session.id, "objective": payload.objective})
        raise HTTPException(status_code=403, detail=f"Operation blocked by AIOS integration guardrails: {payload.operation}")
    if payload.operation not in allowed:
        raise HTTPException(status_code=422, detail=f"Operation is not registered in the secure bridge allowlist: {payload.operation}")
    restricted_access_id = payload.payload.get("restrictedAccessRequestId") if isinstance(payload.payload, dict) else None
    if payload.operation in conditional:
        if not isinstance(restricted_access_id, str) or not restricted_access_id:
            raise HTTPException(status_code=428, detail="Restricted operation requires approved restrictedAccessRequestId")
        access_request = db.query(RestrictedAccessRequest).filter(RestrictedAccessRequest.id == restricted_access_id).first()
        if not access_request:
            raise HTTPException(status_code=404, detail="Restricted access request not found")
        if access_request.operation != payload.operation:
            raise HTTPException(status_code=409, detail="Restricted access request operation does not match runtime operation")
        if access_request.status != "approved":
            raise HTTPException(status_code=403, detail="Restricted access request is not approved")
        if access_request.expires_at and access_request.expires_at < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Restricted access request is expired")
    job = enqueue_job(
        db,
        user,
        "codex.secure_runtime.request",
        {"sessionId": session.id, "operation": payload.operation, "objective": payload.objective, "payload": payload.payload},
        "premium_unlimited",
    )
    event = record_session_event(
        db,
        user,
        session.id,
        "codex.secure_runtime.requested",
        "secure-runtime-bridge",
        payload.operation,
        payload.objective,
        {"jobId": job.id, "operation": payload.operation, "bridgeId": bridge.bridge_id, "restrictedAccessRequestId": restricted_access_id},
    )
    audit(db, user, "codex.secure_runtime.request", job.id, {"sessionId": session.id, "operation": payload.operation, "restrictedAccessRequestId": restricted_access_id})
    return {
        "accepted": True,
        "jobId": job.id,
        "eventId": event.id,
        "operation": payload.operation,
        "bridgeMode": bridge.mode,
        "storesPrivateArtifacts": bridge.stores_private_artifacts,
    }


@app.get("/context/index")
def list_context_indexes(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    indexes = db.query(ContextIndex).order_by(ContextIndex.created_at.desc()).limit(50).all()
    return [context_index_response(item) for item in indexes]


@app.post("/context/index")
def create_context_index(payload: CreateContextIndexRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    if payload.sessionId:
        get_owned_session(db, user, payload.sessionId)
    item = ContextIndex(
        session_id=payload.sessionId,
        name=payload.name,
        source=payload.source,
        status="indexed",
        file_count=payload.fileCount,
        graph_nodes=payload.graphNodes,
        graph_edges=payload.graphEdges,
        index_path=".aios/context/index.db",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    if payload.sessionId:
        record_session_event(
            db,
            user,
            payload.sessionId,
            "context.index.created",
            "context-engine",
            payload.name,
            "Local context index metadata registered.",
            {"indexId": item.id, "fileCount": payload.fileCount, "graphNodes": payload.graphNodes},
        )
    audit(db, user, "context.index.create", item.id, {"sessionId": payload.sessionId, "source": payload.source})
    return context_index_response(item)


@app.post("/context/query")
def query_context(payload: ContextQueryRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    if payload.sessionId:
        get_owned_session(db, user, payload.sessionId)
    latest = db.query(ContextIndex).order_by(ContextIndex.created_at.desc()).first()
    return {
        "localOnly": True,
        "query": payload.query,
        "index": context_index_response(latest) if latest else None,
        "capsule": {
            "budgetPolicy": "ranked_context_capsule",
            "maxResults": payload.maxResults,
            "strategy": "metadata_only_rc3",
            "summary": "RC3 prepares a local-first context engine interface. Source code remains on this machine.",
        },
        "results": [
            {"kind": "system", "title": "Secure Runtime Bridge", "reason": "Runtime operations are routed through allowlisted adapter calls."},
            {"kind": "system", "title": "Redaction", "reason": "Exports and telemetry must not include secrets or private Codex artifacts."},
            {"kind": "system", "title": "Skill Store", "reason": "Skills are permissioned before execution."},
        ][: payload.maxResults],
    }


@app.get("/skill-store")
def skill_store(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    skills = db.query(SkillStoreItem).order_by(SkillStoreItem.created_at.asc()).all()
    return [skill_store_item_response(item) for item in skills]


@app.get("/skill-store/{skill_id}")
def skill_store_item(skill_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    item = db.query(SkillStoreItem).filter(SkillStoreItem.skill_id == skill_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill_store_item_response(item)


@app.get("/release/windows/manifest")
def windows_release_manifest(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    item = db.query(WindowsReleaseArtifact).filter(WindowsReleaseArtifact.release_id == "aios-windows-rc3").first()
    if not item:
        raise HTTPException(status_code=404, detail="Windows release artifact not found")
    return windows_release_response(item)


@app.get("/official-integration/readiness")
def official_integration_readiness(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    config = db.query(OfficialIntegrationConfig).filter(OfficialIntegrationConfig.integration_id == "aios-official-codex-runtime").first()
    if not config:
        raise HTTPException(status_code=404, detail="Official integration config not found")
    settings = get_settings()
    official = official_adapter()
    endpoint_ready = bool(settings.official_codex_runtime_endpoint)
    service_token_ready = bool(settings.official_codex_service_token)
    return {
        "phase": "RC4_OFFICIAL_INTEGRATION_READINESS",
        "contractAuthority": contract_authority_status(),
        "integration": official_integration_response(config),
        "adapter": {
            "targetClass": config.adapter_class,
            "currentLocalFallback": adapter.info()["name"],
            "official": official.info(),
        },
        "runtime": {
            "sandboxApproved": config.sandbox_status == "approved",
            "stagingApproved": config.staging_status == "approved",
            "productionStatus": config.production_status,
            "streamingSupported": config.streaming_supported,
            "toolCallingSupported": config.tool_calling_supported,
            "sessionLifecycleSupported": config.session_lifecycle_supported,
            "snapshotHandoffHooksSupported": config.snapshot_handoff_hooks_supported,
        },
        "credentials": {
            "endpointConfigured": endpoint_ready,
            "serviceTokenConfigured": service_token_ready,
            "tenantConfigured": bool(settings.official_codex_tenant_id),
            "secretsExposed": False,
            "storageRequirement": "Vault/KMS",
        },
        "readyForLiveRuntime": endpoint_ready and service_token_ready and contract_authority_status().get("locked", False),
        "nextSteps": [
            "Set AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT in secure environment",
            "Set AIOS_OFFICIAL_CODEX_SERVICE_TOKEN in Vault/KMS-backed runtime environment",
            "Run rc4-validate.ps1",
            "Enable OfficialCodexRuntimeAdapter for sandbox traffic",
        ],
    }


@app.get("/official-integration/adapter/contract")
def official_integration_adapter_contract(user: User = Depends(get_current_user)) -> dict:
    return official_adapter().contract()


@app.get("/official-integration/credentials/status")
def official_integration_credentials_status(user: User = Depends(get_current_user)) -> dict:
    settings = get_settings()
    return {
        "endpointConfigured": bool(settings.official_codex_runtime_endpoint),
        "serviceTokenConfigured": bool(settings.official_codex_service_token),
        "tenantConfigured": bool(settings.official_codex_tenant_id),
        "secretsExposed": False,
        "storageRequirement": "Vault/KMS",
        "frontendExposureAllowed": False,
        "logsExposureAllowed": False,
    }


@app.get("/codex/delegated-auth/status")
def codex_delegated_auth_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    status = codex_delegated_auth_status_state()
    audit(db, user, "codex.delegated_auth.status", status["authState"], {"secretsExposed": False, "authJsonContentRead": False})
    return status


@app.post("/official-integration/adapter/dry-run")
def official_integration_adapter_dry_run(payload: OfficialAdapterDryRunRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    result = official_adapter().dry_run(payload.modelId, payload.objective)
    audit(db, user, "official_integration.adapter.dry_run", payload.modelId, {"networkCallPerformed": False})
    return result


@app.get("/official-sandbox/security-check")
def official_sandbox_security_check(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    state = official_sandbox_security_state(db)
    audit(db, user, "official_sandbox.security_check", state["state"], {"secureEnvironmentReady": state["secureEnvironmentReady"]})
    return state


@app.get("/official-sandbox/provider-profile")
def official_sandbox_provider_profile_endpoint(user: User = Depends(get_current_user)) -> dict:
    return official_sandbox_provider_profile()


@app.get("/official-sandbox/activation")
def official_sandbox_activation(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    state = official_sandbox_security_state(db)
    return {
        "phase": state["phase"],
        "activationState": state["state"],
        "mode": state["mode"],
        "canInvokeLiveRuntime": state["canInvokeLiveRuntime"],
        "networkCallPerformed": False,
        "message": (
            "Official sandbox live runtime can be enabled."
            if state["secureEnvironmentReady"]
            else "Official sandbox remains blocked until secure endpoint, service token, tenant, Vault/KMS, live flag, and contract lock are present."
        ),
        "security": state,
    }


@app.post("/official-sandbox/activate")
def official_sandbox_activate(db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    state = official_sandbox_security_state(db)
    if not state["secureEnvironmentReady"]:
        audit(db, user, "official_sandbox.activate.blocked", "secure_environment", {"missing": state["missing"]})
        raise HTTPException(
            status_code=412,
            detail="Official sandbox live activation requires a secure environment: endpoint, service token, tenant, sandbox environment id, Vault/KMS, live flag, and contract lock.",
        )
    audit(db, user, "official_sandbox.activate", "official_sandbox_live", {"networkCallPerformed": False})
    return {
        "activated": True,
        "activationState": state["state"],
        "mode": state["mode"],
        "canInvokeLiveRuntime": True,
        "networkCallPerformed": False,
        "message": "Secure environment is ready. Live runtime calls may now be routed through OfficialCodexRuntimeAdapter.",
    }


@app.get("/official-sandbox/data-profiles")
def official_sandbox_data_profiles(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    profiles = db.query(SandboxDataProfile).order_by(SandboxDataProfile.created_at.desc()).all()
    return [sandbox_data_profile_response(item) for item in profiles]


@app.post("/official-sandbox/data-profiles")
def create_official_sandbox_data_profile(
    payload: CreateSandboxDataProfileRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
) -> dict:
    if payload.dataClassification == "real_sandbox_approved":
        if not payload.redactionRequired:
            raise HTTPException(status_code=422, detail="Approved real sandbox data requires redaction.")
        if payload.publicExportAllowed:
            raise HTTPException(status_code=422, detail="Approved real sandbox data cannot be exported publicly.")
        if not payload.approvalReference.strip():
            raise HTTPException(status_code=422, detail="Approved real sandbox data requires an approval reference.")

    existing = db.query(SandboxDataProfile).filter(SandboxDataProfile.profile_id == payload.profileId).first()
    if existing:
        existing.name = payload.name
        existing.data_classification = payload.dataClassification
        existing.approval_reference = payload.approvalReference
        existing.redaction_required = payload.redactionRequired
        existing.public_export_allowed = payload.publicExportAllowed
        existing.retention_days = payload.retentionDays
        existing.status = payload.status
        item = existing
    else:
        item = SandboxDataProfile(
            profile_id=payload.profileId,
            name=payload.name,
            data_classification=payload.dataClassification,
            approval_reference=payload.approvalReference,
            redaction_required=payload.redactionRequired,
            public_export_allowed=payload.publicExportAllowed,
            retention_days=payload.retentionDays,
            status=payload.status,
            created_by_user_id=user.id,
        )
        db.add(item)
    db.commit()
    db.refresh(item)
    audit(
        db,
        user,
        "official_sandbox.data_profile.upsert",
        item.id,
        {
            "profileId": item.profile_id,
            "dataClassification": item.data_classification,
            "redactionRequired": item.redaction_required,
            "publicExportAllowed": item.public_export_allowed,
        },
    )
    return sandbox_data_profile_response(item)


@app.get("/approval-gate/policy")
def get_approval_gate_policy(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    policy = approval_gate_policy()
    pending_count = db.query(ApprovalGateRequest).filter(ApprovalGateRequest.status == "pending").count()
    policy["pendingRequests"] = pending_count
    audit(db, user, "approval_gate.policy", "rc24", {"pendingRequests": pending_count})
    return policy


@app.post("/approval-gate/requests")
def create_approval_gate_request(payload: CreateApprovalGateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    if payload.sessionId:
        get_owned_session(db, user, payload.sessionId)
    redacted_preview = redact(payload.preview)
    risk_level, risk_score = approval_gate_risk(payload.operation, redacted_preview)
    item = ApprovalGateRequest(
        session_id=payload.sessionId,
        requested_by_user_id=user.id,
        operation=payload.operation,
        target=redact(payload.target),
        reason=redact(payload.reason),
        preview=json.dumps(redacted_preview),
        risk_level=risk_level,
        risk_score=risk_score,
        status="pending",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    audit(
        db,
        user,
        "approval_gate.requested",
        item.id,
        {
            "sessionId": item.session_id,
            "operation": item.operation,
            "riskLevel": item.risk_level,
            "executionPerformed": False,
            "autoExecuteAllowed": False,
        },
    )
    return approval_gate_response(item)


@app.get("/approval-gate/requests")
def list_approval_gate_requests(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    items = (
        db.query(ApprovalGateRequest)
        .filter(ApprovalGateRequest.requested_by_user_id == user.id)
        .order_by(ApprovalGateRequest.created_at.desc())
        .limit(50)
        .all()
    )
    return [approval_gate_response(item) for item in items]


@app.patch("/approval-gate/requests/{request_id}/decision")
def decide_approval_gate_request(
    request_id: str,
    payload: ApprovalGateDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    item = (
        db.query(ApprovalGateRequest)
        .filter(ApprovalGateRequest.id == request_id, ApprovalGateRequest.requested_by_user_id == user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Approval gate request not found")
    if item.status != "pending":
        raise HTTPException(status_code=409, detail="Approval gate request already decided")
    item.status = payload.decision
    item.decision_reason = redact(payload.reason)
    item.decided_by_user_id = user.id
    item.decided_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    audit(
        db,
        user,
        f"approval_gate.{payload.decision}",
        item.id,
        {
            "sessionId": item.session_id,
            "operation": item.operation,
            "riskLevel": item.risk_level,
            "executionPerformed": False,
            "autoExecuteAllowed": False,
        },
    )
    return approval_gate_response(item)


@app.post("/restricted-access/requests")
def create_restricted_access_request(payload: CreateRestrictedAccessRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    item = RestrictedAccessRequest(
        operation=payload.operation,
        environment=payload.environment,
        justification=payload.justification,
        artifact_name=payload.artifactName,
        artifact_hash=payload.artifactHash,
        path_scope=payload.pathScope,
        status="requested",
        requested_by_user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=max(1, min(payload.expiresInDays, 90))),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    audit(db, user, "restricted_access.requested", item.id, {"operation": item.operation, "environment": item.environment})
    return restricted_access_response(item)


@app.get("/restricted-access/requests")
def list_restricted_access_requests(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    items = db.query(RestrictedAccessRequest).order_by(RestrictedAccessRequest.created_at.desc()).limit(100).all()
    return [restricted_access_response(item) for item in items]


@app.patch("/restricted-access/requests/{request_id}/decision")
def decide_restricted_access_request(
    request_id: str,
    payload: RestrictedAccessDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
) -> dict:
    item = db.query(RestrictedAccessRequest).filter(RestrictedAccessRequest.id == request_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Restricted access request not found")
    item.status = payload.decision
    item.approved_by = payload.approver
    item.decision_notes = payload.notes
    item.decided_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    audit(db, user, f"restricted_access.{payload.decision}", item.id, {"operation": item.operation, "approver": payload.approver})
    return restricted_access_response(item)


@app.post("/restricted-access/requests/{request_id}/access-log")
def record_restricted_access_log(
    request_id: str,
    payload: RestrictedAccessLogRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
) -> dict:
    item = db.query(RestrictedAccessRequest).filter(RestrictedAccessRequest.id == request_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Restricted access request not found")
    details = {
        "requestId": item.id,
        "operation": item.operation,
        "environment": item.environment,
        "artifactName": item.artifact_name,
        "artifactHash": item.artifact_hash,
        "pathScope": item.path_scope,
        "action": payload.action,
        "artifactPath": payload.artifactPath,
        "artifactHashObserved": payload.artifactHash,
        "justification": payload.justification,
        "result": payload.result,
        "machineScopeApproved": payload.artifactPath.startswith(item.path_scope) if payload.artifactPath else False,
    }
    audit(db, user, "restricted_access.access_log", item.id, details)
    log = (
        db.query(AuditLog)
        .filter(AuditLog.action == "restricted_access.access_log", AuditLog.resource == item.id)
        .order_by(AuditLog.created_at.desc())
        .first()
    )
    return {
        "id": log.id if log else "",
        "requestId": item.id,
        "action": payload.action,
        "result": payload.result,
        "createdAt": log.created_at.isoformat() if log else datetime.utcnow().isoformat(),
        "details": redact(details),
    }


@app.get("/restricted-access/requests/{request_id}/access-log")
def list_restricted_access_logs(request_id: str, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> list[dict]:
    item = db.query(RestrictedAccessRequest).filter(RestrictedAccessRequest.id == request_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Restricted access request not found")
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.action == "restricted_access.access_log", AuditLog.resource == request_id)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )
    return [
        {
            "id": log.id,
            "requestId": request_id,
            "actorUserId": log.actor_user_id,
            "createdAt": log.created_at.isoformat(),
            "details": redact(json.loads(log.details or "{}")),
        }
        for log in logs
    ]


@app.post("/sessions")
def create_session(payload: CreateSessionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    session = CodexSession(user_id=user.id, title=payload.title, objective=payload.objective, status="active")
    db.add(session)
    db.commit()
    db.refresh(session)
    SESSION_CREATED_TOTAL.inc()
    audit(db, user, "sessions.create", session.id, {"objective": payload.objective})
    return session_response(session)


@app.get("/sessions")
def list_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    sessions = db.query(CodexSession).filter(CodexSession.user_id == user.id).order_by(CodexSession.created_at.desc()).limit(50).all()
    return [session_response(item) for item in sessions]


@app.patch("/sessions/{session_id}/status")
def update_session_status(session_id: str, payload: UpdateSessionStatusRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    session = db.query(CodexSession).filter(CodexSession.id == session_id, CodexSession.user_id == user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.status = payload.status
    session.updated_at = datetime.utcnow()
    db.commit()
    if payload.status == "completed":
        SESSION_COMPLETED_TOTAL.inc()
    audit(db, user, "sessions.status", session.id, {"status": payload.status})
    return {"id": session.id, "status": session.status}


@app.post("/snapshots")
def create_snapshot(payload: CreateSnapshotRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    session = get_owned_session(db, user, payload.sessionId)
    snapshot = Snapshot(session_id=session.id, title=payload.title, files_changed=json.dumps(payload.filesChanged), notes=payload.notes)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    SNAPSHOT_CREATED_TOTAL.inc()
    audit(db, user, "snapshots.create", snapshot.id, {"sessionId": session.id})
    event = record_session_event(
        db,
        user,
        session.id,
        "snapshot.created",
        "api",
        payload.title,
        payload.notes,
        {"snapshotId": snapshot.id, "filesChanged": payload.filesChanged},
    )
    if payload.filesChanged:
        record_files_changed(db, session.id, payload.filesChanged, "snapshot", event.id)
    return snapshot_response(snapshot)


@app.get("/sessions/{session_id}/snapshots")
def list_snapshots(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    get_owned_session(db, user, session_id)
    snapshots = db.query(Snapshot).filter(Snapshot.session_id == session_id).order_by(Snapshot.created_at.desc()).all()
    return [snapshot_response(item) for item in snapshots]


@app.post("/sessions/{session_id}/events")
def create_session_event(session_id: str, payload: CreateSessionEventRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    get_owned_session(db, user, session_id)
    event = record_session_event(db, user, session_id, payload.type, payload.source, payload.title, payload.message, payload.payload)
    if payload.type in {"repo.patch_applied", "repo.file_changed"}:
        files = payload.payload.get("filesChanged") or payload.payload.get("files") or []
        if isinstance(files, list):
            record_files_changed(db, session_id, [str(item) for item in files], payload.source, event.id)
    return session_event_response(event)


@app.get("/sessions/{session_id}/events")
def list_session_events(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    get_owned_session(db, user, session_id)
    events = db.query(SessionEvent).filter(SessionEvent.session_id == session_id).order_by(SessionEvent.created_at.desc()).limit(100).all()
    return [session_event_response(item) for item in events]


@app.post("/sessions/{session_id}/files-changed")
def add_files_changed(session_id: str, payload: FilesChangedRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    get_owned_session(db, user, session_id)
    event = record_session_event(
        db,
        user,
        session_id,
        "repo.file_changed",
        payload.source,
        "Files changed",
        f"{len(payload.filesChanged)} file(s) changed",
        {"filesChanged": payload.filesChanged},
    )
    files_changed = record_files_changed(db, session_id, payload.filesChanged, payload.source, event.id)
    audit(db, user, "sessions.files_changed", session_id, {"count": len(files_changed), "source": payload.source})
    return {"sessionId": session_id, "filesChanged": files_changed, "eventId": event.id}


@app.post("/handoffs")
def create_handoff(payload: CreateHandoffRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    session = get_owned_session(db, user, payload.sessionId)
    handoff = Handoff(
        session_id=session.id,
        from_adapter=payload.fromAdapter,
        to_adapter=payload.toAdapter,
        reason=payload.reason,
        context=payload.context,
        next_steps=json.dumps(payload.nextSteps),
    )
    db.add(handoff)
    db.commit()
    db.refresh(handoff)
    audit(db, user, "handoffs.create", handoff.id, {"sessionId": session.id, "toAdapter": payload.toAdapter})
    record_session_event(
        db,
        user,
        session.id,
        "handoff.created",
        "api",
        "Handoff created",
        payload.reason,
        {"handoffId": handoff.id, "toAdapter": payload.toAdapter, "nextSteps": payload.nextSteps},
    )
    return handoff_response(handoff)


@app.get("/sessions/{session_id}/handoffs")
def list_handoffs(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    get_owned_session(db, user, session_id)
    handoffs = db.query(Handoff).filter(Handoff.session_id == session_id).order_by(Handoff.created_at.desc()).all()
    return [handoff_response(item) for item in handoffs]


@app.get("/sessions/{session_id}/workbench")
def session_workbench(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    session = get_owned_session(db, user, session_id)

    snapshots = db.query(Snapshot).filter(Snapshot.session_id == session_id).order_by(Snapshot.created_at.desc()).limit(10).all()
    handoffs = db.query(Handoff).filter(Handoff.session_id == session_id).order_by(Handoff.created_at.desc()).limit(10).all()
    jobs = db.query(QosJob).filter(QosJob.user_id == user.id).order_by(QosJob.created_at.desc()).limit(50).all()
    session_jobs = [job for job in jobs if json.loads(job.payload or "{}").get("sessionId") == session_id]
    latest_build = next((job for job in session_jobs if job.job_type == "build"), None)
    events = db.query(SessionEvent).filter(SessionEvent.session_id == session_id).order_by(SessionEvent.created_at.desc()).limit(100).all()
    file_records = db.query(SessionFileChanged).filter(SessionFileChanged.session_id == session_id).order_by(SessionFileChanged.created_at.asc()).all()
    files_changed = [item.path for item in file_records]
    if not files_changed and snapshots:
        files_changed = snapshot_response(snapshots[0])["filesChanged"]
    event_payloads = [session_event_response(item) for item in events]
    mcp_calls = [item for item in event_payloads if item["type"] == "mcp.tool_call"]
    build_event = next((item for item in event_payloads if item["type"] in {"repo.build_started", "repo.build_passed", "repo.build_failed"}), None)
    event_build_status = None
    if build_event:
        event_build_status = {
            "status": {"repo.build_started": "running", "repo.build_passed": "completed", "repo.build_failed": "failed"}[build_event["type"]],
            "jobType": "build",
            "source": build_event["source"],
            "title": build_event["title"],
            "message": build_event["message"],
            "createdAt": build_event["createdAt"],
        }
    entitlement = db.query(Entitlement).filter(Entitlement.user_id == user.id).first()
    sandbox_state = official_sandbox_security_state(db)
    runtime_adapter_info = official_adapter().info() if sandbox_state["secureEnvironmentReady"] else adapter.info()

    return {
        "session": session_response(session),
        "entitlement": entitlement_response(entitlement) if entitlement else None,
        "snapshots": [snapshot_response(item) for item in snapshots],
        "handoffs": [handoff_response(item) for item in handoffs],
        "filesChanged": files_changed,
        "buildStatus": event_build_status or (qos_job_response(latest_build) if latest_build else {"status": "not_queued", "jobType": "build"}),
        "recentJobs": [qos_job_response(item) for item in session_jobs[:10]],
        "mcpToolCalls": mcp_calls,
        "recentEvents": event_payloads[:25],
        "runtimeAdapter": runtime_adapter_info,
        "legacyLineage": legacy_aios_summary(),
        "heritage": legacy_aios_summary(),
    }


@app.post("/qos/enqueue")
def qos_enqueue(payload: EnqueueRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    job = enqueue_job(db, user, payload.jobType, payload.payload, payload.priorityClass)
    audit(db, user, "qos.enqueue", job.id, {"jobType": payload.jobType})
    session_id = payload.payload.get("sessionId")
    if isinstance(session_id, str) and payload.jobType == "build":
        get_owned_session(db, user, session_id)
        record_session_event(
            db,
            user,
            session_id,
            "repo.build_started",
            "qos",
            "QoS build queued",
            "Build job entered the QoS queue.",
            {"jobId": job.id, "payload": payload.payload},
        )
    return {"id": job.id, "status": job.status, "priorityClass": job.priority_class, "queueDepth": queue_depth()}


@app.get("/qos/jobs/{job_id}")
def qos_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    job = db.query(QosJob).filter(QosJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {
        "id": job.id,
        "jobType": job.job_type,
        "status": job.status,
        "priorityClass": job.priority_class,
        "payload": json.loads(job.payload or "{}"),
        "result": json.loads(job.result or "{}"),
    }


@app.post("/codex/run")
def codex_run(payload: CodexRunRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    result = adapter.run(payload.objective, payload.sessionId)
    job = enqueue_job(db, user, "codex_run", {"objective": payload.objective, "sessionId": payload.sessionId})
    audit(db, user, "codex.run", job.id, {"sessionId": payload.sessionId})
    return {"run": result, "qosJobId": job.id}


@app.post("/codex/skill/execute")
def codex_skill_execute(payload: SkillExecuteRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    result = adapter.execute_skill(payload.skillName, payload.input)
    db.add(McpToolCall(tool_name=f"skill.{payload.skillName}", actor=user.email, status=result["status"], details=json.dumps(result)))
    db.commit()
    audit(db, user, "codex.skill.execute", payload.skillName)
    session_id = payload.input.get("sessionId")
    if isinstance(session_id, str):
        get_owned_session(db, user, session_id)
        record_session_event(
            db,
            user,
            session_id,
            "skill.executed",
            "api",
            payload.skillName,
            "Skill executed through Codex adapter.",
            {"skillName": payload.skillName, "result": result},
        )
    return result


@app.get("/codex/adapter/info")
def codex_adapter_info() -> dict:
    return adapter.info()


@app.get("/control-plane/status")
def control_plane_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict:
    entitlement = db.query(Entitlement).filter(Entitlement.user_id == user.id).first()
    active_sessions = db.query(CodexSession).filter(CodexSession.user_id == user.id, CodexSession.status == "active").count()
    running_jobs = db.query(QosJob).filter(QosJob.status == "running").count()
    return {
        "plan": entitlement.plan if entitlement else "unknown",
        "status": entitlement.status if entitlement else "missing",
        "priorityClass": entitlement.priority_class if entitlement else "unknown",
        "productUnit": "codex_sessions",
        "availabilityMode": "local_enterprise_demo",
        "queueDepth": queue_depth(),
        "runningJobs": running_jobs,
        "activeSessions": active_sessions,
        "capabilities": ["mcp", "skills", "snapshots", "qos", "rbac", "vault-boundary", "redacted-export", "workbench"],
        "highAvailabilityRouting": {"enabled": True, "mode": "adapter-boundary"},
        "degradationProtection": {"enabled": True, "actions": ["shape", "degrade", "review"]},
    }


@app.post("/abuse/evaluate")
def abuse_evaluate(payload: AbuseEvaluateRequest, user: User = Depends(get_current_user)) -> dict:
    score = payload.toolCallFlood * 2 + payload.failedBuilds * 3 + payload.sessionSpike
    if payload.suspiciousCommand:
        score += 8
    action = "allow"
    if score >= 15:
        action = "review"
    elif score >= 10:
        action = "degrade"
    elif score >= 5:
        action = "shape"
    return {"action": action, "score": score, "signals": payload.model_dump(), "actor": user.email}


@app.post("/admin/service-tokens")
def create_service_token(name: str = "mcp-local", db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    raw_token = f"aios_st_{secrets.token_urlsafe(32)}"
    token_hash = hash_service_token(raw_token)
    stored = ServiceToken(name=name, token_hash=token_hash, role="developer", created_by_user_id=user.id)
    db.add(stored)
    db.commit()
    audit(db, user, "service_tokens.create", stored.id, {"name": name})
    return {"id": stored.id, "name": name, "serviceToken": raw_token}


@app.post("/admin/codex/models")
def admin_upsert_codex_model(payload: UpsertCodexModelRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    model = db.query(CodexModel).filter(CodexModel.model_id == payload.modelId).first()
    if not model:
        model = CodexModel(model_id=payload.modelId, name=payload.name)
        db.add(model)
    model.name = payload.name
    model.tier = payload.tier
    model.purpose = payload.purpose
    model.runtime_provider = payload.runtimeProvider
    model.available_in_unlimited = payload.availableInUnlimited
    model.default_for = json.dumps(payload.defaultFor)
    model.status = payload.status
    db.commit()
    db.refresh(model)
    audit(db, user, "admin.codex.models.upsert", model.id, {"modelId": model.model_id})
    return codex_model_response(model)


@app.post("/admin/codex/plans")
def admin_upsert_codex_plan(payload: UpsertCodexPlanRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    plan = db.query(CodexPlan).filter(CodexPlan.plan_id == payload.planId).first()
    if not plan:
        plan = CodexPlan(plan_id=payload.planId, name=payload.name)
        db.add(plan)
    plan.name = payload.name
    plan.description = payload.description
    plan.price_label = payload.priceLabel
    plan.product_unit = payload.productUnit
    plan.has_token_limit = False
    plan.shows_token_counter = False
    plan.uses_token_balance = False
    plan.has_weekly_token_quota = False
    plan.priority_class = payload.priorityClass
    plan.status = payload.status
    plan.features = json.dumps(payload.features)
    db.commit()
    db.refresh(plan)
    audit(db, user, "admin.codex.plans.upsert", plan.id, {"planId": plan.plan_id})
    return codex_plan_response(plan)


@app.post("/admin/language/rules")
def admin_upsert_language_rule(payload: UpsertLanguageRuleRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    rule = db.query(LanguagePolicyRule).filter(LanguagePolicyRule.rule_type == payload.ruleType, LanguagePolicyRule.term == payload.term).first()
    if not rule:
        rule = LanguagePolicyRule(rule_type=payload.ruleType, term=payload.term)
        db.add(rule)
    rule.severity = payload.severity
    rule.replacement = payload.replacement
    rule.active = payload.active
    db.commit()
    db.refresh(rule)
    audit(db, user, "admin.language.rules.upsert", rule.id, {"term": rule.term, "ruleType": rule.rule_type})
    return language_rule_response(rule)


@app.get("/admin/audit-logs")
def audit_logs(db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> list[dict]:
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [{"id": item.id, "action": item.action, "resource": item.resource, "details": json.loads(item.details or "{}"), "createdAt": item.created_at.isoformat()} for item in logs]


@app.get("/admin/qos/jobs")
def admin_qos_jobs(db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> list[dict]:
    jobs = db.query(QosJob).order_by(QosJob.created_at.desc()).limit(100).all()
    return [{"id": item.id, "jobType": item.job_type, "status": item.status, "priorityClass": item.priority_class, "createdAt": item.created_at.isoformat()} for item in jobs]


@app.get("/admin/mcp/tool-calls")
def admin_mcp_tool_calls(db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> list[dict]:
    calls = db.query(McpToolCall).order_by(McpToolCall.created_at.desc()).limit(100).all()
    return [{"id": item.id, "toolName": item.tool_name, "actor": item.actor, "status": item.status, "details": json.loads(item.details or "{}"), "createdAt": item.created_at.isoformat()} for item in calls]


@app.get("/export/redacted-bundle")
def export_redacted_bundle(db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    bundle = {
        "product": "AIOS Codex Unlimited",
        "admin": {"email": user.email, "authorization": "Bearer example.jwt.token"},
        "policy": load_policy(),
        "sampleSecrets": {"openai_api_key": "redaction-demo-openai-key", "password": "AiosAdmin123!"},
    }
    return redact(bundle)


@app.post("/secrets/{name}")
def write_secret(name: str, payload: SecretRequest, user: User = Depends(require_role("admin"))) -> dict:
    return VaultClient().write_secret(name, payload.value)


@app.get("/secrets/{name}")
def read_secret(name: str, user: User = Depends(require_role("admin"))) -> dict:
    return VaultClient().read_secret(name)


@app.get("/sso/mock/authorize")
def sso_mock_authorize() -> dict:
    return {"provider": "mock-oidc", "authorizationUrl": "/sso/mock/callback?code=mock-code"}


@app.get("/sso/mock/callback")
def sso_mock_callback(code: str = "mock-code") -> dict:
    return {"status": "accepted", "code": code, "message": "Mock OIDC callback accepted for local demo."}


@app.post("/tenants")
def create_tenant(payload: CreateTenantRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    tenant = Tenant(name=payload.name, slug=payload.slug)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    audit(db, user, "tenants.create", tenant.id)
    return {"id": tenant.id, "name": tenant.name, "slug": tenant.slug}


@app.get("/tenants")
def list_tenants(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[dict]:
    tenants = db.query(Tenant).order_by(Tenant.created_at.desc()).all()
    return [{"id": item.id, "name": item.name, "slug": item.slug} for item in tenants]


@app.post("/tenants/{tenant_id}/members")
def add_tenant_member(tenant_id: str, payload: CreateTenantMemberRequest, db: Session = Depends(get_db), user: User = Depends(require_role("admin"))) -> dict:
    if not db.query(Tenant).filter(Tenant.id == tenant_id).first():
        raise HTTPException(status_code=404, detail="Tenant not found")
    if not db.query(User).filter(User.id == payload.userId).first():
        raise HTTPException(status_code=404, detail="User not found")
    membership = TenantMembership(tenant_id=tenant_id, user_id=payload.userId, role=payload.role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    audit(db, user, "tenants.members.add", tenant_id, {"member": payload.userId})
    return {"id": membership.id, "tenantId": tenant_id, "userId": payload.userId, "role": payload.role}
