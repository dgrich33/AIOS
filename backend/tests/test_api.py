import os
from pathlib import Path

os.environ["AIOS_DATABASE_URL"] = "sqlite:///./test_aios.db"
os.environ["AIOS_REDIS_URL"] = ""

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db import engine  # noqa: E402
from app.main import app  # noqa: E402


def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": "admin@aios.local", "password": "AiosAdmin123!"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def test_health_and_ready() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/ready").json()["status"] == "ready"


def test_entitlement_is_session_based_and_hides_token_units() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.get("/entitlement/me", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["productUnit"] == "codex_sessions"
        assert payload["hasTokenLimit"] is False
        assert payload["showsTokenCounter"] is False
        assert payload["usesTokenBalance"] is False
        assert payload["hasWeeklyTokenQuota"] is False


def test_session_snapshot_qos_and_control_plane_flow() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        session = client.post("/sessions", headers=headers, json={"title": "Test session", "objective": "Validate sessions"}).json()
        assert session["status"] == "active"

        snapshot = client.post(
            "/snapshots",
            headers=headers,
            json={"sessionId": session["id"], "title": "Snapshot 1", "filesChanged": ["README.md"], "notes": "test"},
        ).json()
        assert snapshot["sessionId"] == session["id"]

        job = client.post("/qos/enqueue", headers=headers, json={"jobType": "build", "payload": {"command": "npm run build"}}).json()
        assert job["status"] == "queued"

        control_plane = client.get("/control-plane/status", headers=headers).json()
        assert control_plane["productUnit"] == "codex_sessions"
        assert "qos" in control_plane["capabilities"]


def test_aios_heritage_summary_documents_original_product_lineage() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.get("/aios/heritage/summary", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["sourceProjectPath"] == r"C:\Users\dg71\Documents\AIOS-15-Fase3-Corrigido"
        assert "Arena.IA" in payload["legacyModules"]
        assert payload["migrationMap"]["Arena.IA"] == "Codex Workbench skill routing"


def test_session_handoff_and_workbench_state_flow() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        session = client.post("/sessions", headers=headers, json={"title": "Handoff test", "objective": "Validate workbench"}).json()

        snapshot = client.post(
            "/snapshots",
            headers=headers,
            json={
                "sessionId": session["id"],
                "title": "Workbench checkpoint",
                "filesChanged": ["frontend/src/App.tsx", "backend/app/main.py"],
                "notes": "checkpoint",
            },
        ).json()
        assert snapshot["sessionId"] == session["id"]

        handoff = client.post(
            "/handoffs",
            headers=headers,
            json={
                "sessionId": session["id"],
                "fromAdapter": "local_queue",
                "toAdapter": "official_codex_runtime_future",
                "reason": "Continue implementation after checkpoint",
                "context": "Workbench state includes snapshots and MCP calls.",
                "nextSteps": ["Review changed files", "Run backend tests"],
            },
        )
        assert handoff.status_code == 200
        handoff_payload = handoff.json()
        assert handoff_payload["sessionId"] == session["id"]
        assert handoff_payload["nextSteps"] == ["Review changed files", "Run backend tests"]

        handoffs = client.get(f"/sessions/{session['id']}/handoffs", headers=headers).json()
        assert handoffs[0]["id"] == handoff_payload["id"]

        workbench = client.get(f"/sessions/{session['id']}/workbench", headers=headers).json()
        assert workbench["session"]["id"] == session["id"]
        assert workbench["filesChanged"] == ["frontend/src/App.tsx", "backend/app/main.py"]
        assert workbench["buildStatus"]["status"] in {"not_queued", "queued", "running", "completed", "failed"}
        assert workbench["handoffs"][0]["id"] == handoff_payload["id"]
        assert "legacyLineage" in workbench


def test_session_events_files_changed_and_workbench_aggregation() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        session = client.post("/sessions", headers=headers, json={"title": "Events test", "objective": "Track MCP events"}).json()

        tool_event = client.post(
            f"/sessions/{session['id']}/events",
            headers=headers,
            json={
                "type": "mcp.tool_call",
                "source": "aios-mcp-repo",
                "title": "repo.search",
                "message": "Searched workspace for Workbench references",
                "payload": {"tool": "repo.search", "query": "Workbench"},
            },
        )
        assert tool_event.status_code == 200
        assert tool_event.json()["type"] == "mcp.tool_call"

        client.post(
            f"/sessions/{session['id']}/events",
            headers=headers,
            json={
                "type": "repo.build_passed",
                "source": "aios-mcp-repo",
                "title": "frontend build",
                "message": "npm run build completed",
                "payload": {"target": "frontend", "status": 0},
            },
        )

        files = client.post(
            f"/sessions/{session['id']}/files-changed",
            headers=headers,
            json={"filesChanged": ["frontend/src/App.tsx", "mcp/aios-mcp-repo/src/server.ts"], "source": "aios-mcp-repo"},
        )
        assert files.status_code == 200
        assert files.json()["filesChanged"] == ["frontend/src/App.tsx", "mcp/aios-mcp-repo/src/server.ts"]

        events = client.get(f"/sessions/{session['id']}/events", headers=headers).json()
        assert events[0]["type"] == "repo.file_changed"
        assert {item["type"] for item in events} >= {"mcp.tool_call", "repo.build_passed", "repo.file_changed"}

        workbench = client.get(f"/sessions/{session['id']}/workbench", headers=headers).json()
        assert workbench["entitlement"]["productUnit"] == "codex_sessions"
        assert workbench["filesChanged"] == ["frontend/src/App.tsx", "mcp/aios-mcp-repo/src/server.ts"]
        assert workbench["buildStatus"]["status"] == "completed"
        assert workbench["runtimeAdapter"]["name"] == "LocalQueueCodexAdapter"
        assert workbench["mcpToolCalls"][0]["type"] == "mcp.tool_call"
        assert workbench["recentEvents"][0]["type"] == "repo.file_changed"


def test_service_token_can_record_session_events_without_admin_access() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        session = client.post("/sessions", headers=headers, json={"title": "Service token events", "objective": "MCP auth"}).json()
        token_payload = client.post("/admin/service-tokens?name=mcp-test", headers=headers).json()
        service_headers = {"Authorization": f"Bearer {token_payload['serviceToken']}"}

        response = client.post(
            f"/sessions/{session['id']}/events",
            headers=service_headers,
            json={
                "type": "mcp.tool_call",
                "source": "aios-mcp-repo",
                "title": "repo.build",
                "message": "MCP service token recorded this event",
                "payload": {"target": "frontend"},
            },
        )
        assert response.status_code == 200
        assert response.json()["actor"].startswith("service-token:")

        admin_response = client.get("/admin/audit-logs", headers=service_headers)
        assert admin_response.status_code == 403


def test_rc2_product_manifest_models_plan_subscription_runtime_and_language_policy() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)

        manifest = client.get("/codex/product/manifest", headers=headers)
        assert manifest.status_code == 200
        manifest_payload = manifest.json()
        assert manifest_payload["product"] == "AIOS Codex Unlimited"
        assert manifest_payload["productUnit"] == "codex_sessions"
        assert manifest_payload["experience"]["hasTokenLimit"] is False
        assert "Codex Runtime Gateway" in manifest_payload["systems"]

        models = client.get("/codex/models", headers=headers)
        assert models.status_code == 200
        model_ids = {item["modelId"] for item in models.json()}
        assert "codex-5.5-unlimited" in model_ids
        assert "codex-5.5-code-review" in model_ids

        model = client.get("/codex/models/codex-5.5-unlimited", headers=headers)
        assert model.status_code == 200
        assert model.json()["availableInUnlimited"] is True

        plan = client.get("/codex/plans/unlimited", headers=headers)
        assert plan.status_code == 200
        plan_payload = plan.json()
        assert plan_payload["planId"] == "aios_codex_unlimited"
        assert plan_payload["productUnit"] == "codex_sessions"
        assert plan_payload["hasWeeklyTokenQuota"] is False

        subscription = client.get("/subscriptions/me", headers=headers)
        assert subscription.status_code == 200
        assert subscription.json()["status"] == "active"

        runtime = client.get("/codex/runtime/status", headers=headers)
        assert runtime.status_code == 200
        assert runtime.json()["adapter"] == "LocalQueueCodexAdapter"
        assert "codex-5.5-unlimited" in runtime.json()["supportedModels"]

        allowed = client.post(
            "/policy/language/evaluate",
            headers=headers,
            json={"text": "AIOS Codex Unlimited com sessoes Codex e Codex Workbench."},
        )
        assert allowed.status_code == 200
        assert allowed.json()["approved"] is True
        assert "AIOS Codex Unlimited" in allowed.json()["allowedTerms"]

        blocked = client.post(
            "/policy/language/evaluate",
            headers=headers,
            json={"text": "Tentativa de bypass para contornar limite."},
        )
        assert blocked.status_code == 200
        blocked_payload = blocked.json()
        assert blocked_payload["approved"] is False
        assert "bypass" in blocked_payload["blockedTerms"]
        assert blocked_payload["severity"] in {"medium", "high", "critical"}

        session = client.post("/sessions", headers=headers, json={"title": "Runtime RC2", "objective": "Invoke runtime gateway"}).json()
        invoke = client.post(
            "/codex/runtime/invoke",
            headers=headers,
            json={"session_id": session["id"], "model_id": "codex-5.5-unlimited", "objective": "Validate RC2 runtime gateway"},
        )
        assert invoke.status_code == 200
        invoke_payload = invoke.json()
        assert invoke_payload["accepted"] is True
        assert invoke_payload["modelId"] == "codex-5.5-unlimited"
        assert invoke_payload["adapter"] == "LocalQueueCodexAdapter"

        events = client.get(f"/sessions/{session['id']}/events", headers=headers).json()
        assert events[0]["type"] == "codex.runtime.invoked"


def test_rc7_no_developer_cost_provider_catalog_and_recommendation() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)

        providers = client.get("/runtime/no-developer-cost/providers", headers=headers)
        assert providers.status_code == 200
        providers_payload = providers.json()
        assert providers_payload["productUnit"] == "codex_sessions"
        assert providers_payload["primaryProvider"] == "puter_user_pays"
        provider_ids = {item["providerId"] for item in providers_payload["providers"]}
        assert "puter_user_pays" in provider_ids
        assert "openrouter_free_models" in provider_ids
        assert "nvidia_nim" in provider_ids

        puter = next(item for item in providers_payload["providers"] if item["providerId"] == "puter_user_pays")
        assert puter["requiresDeveloperApiKey"] is False
        assert puter["developerCost"] == "none_direct"
        assert puter["runtimeSurface"] == "frontend_browser"
        assert "openai/gpt-5.3-codex" in puter["models"]
        assert puter["officialCodexReplacement"] is False

        recommendation = client.get("/runtime/no-developer-cost/recommendation", headers=headers)
        assert recommendation.status_code == 200
        recommendation_payload = recommendation.json()
        assert recommendation_payload["recommendedProvider"]["providerId"] == "puter_user_pays"
        assert "puter_user_pays" in recommendation_payload["fallbackOrder"]
        assert "token" not in recommendation_payload["implementation"]["frontend"].lower()


def test_rc3_secure_runtime_context_skill_store_and_windows_release() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)

        guardrails = client.get("/policy/integration/guardrails", headers=headers)
        assert guardrails.status_code == 200
        guardrail_payload = guardrails.json()
        assert "runtime_patch" in guardrail_payload["conditionalOperations"]
        assert "copy_model_checkpoints" in guardrail_payload["conditionalOperations"]
        assert "alter_codex_auth_json" in guardrail_payload["blockedOperations"]
        assert guardrail_payload["restrictedAccessControls"]["requiresApprovedRequest"] is True
        assert guardrail_payload["privateArtifactPolicy"]["userReleaseIncludesPrivateArtifacts"] is False
        assert guardrail_payload["privateArtifactPolicy"]["developerMachineRestrictedArtifactsAllowed"] is True

        profiles = client.get("/identity/profiles", headers=headers)
        assert profiles.status_code == 200
        assert profiles.json()[0]["runtimeAccessMode"] == "official_adapter_only"

        bridge = client.get("/codex/secure-runtime/bridge", headers=headers)
        assert bridge.status_code == 200
        assert bridge.json()["storesPrivateArtifacts"] is False
        assert "official_runtime_invoke" in bridge.json()["allowedOperations"]

        session = client.post("/sessions", headers=headers, json={"title": "RC3 Secure Bridge", "objective": "Validate safe bridge"}).json()
        accepted = client.post(
            "/codex/secure-runtime/request",
            headers=headers,
            json={
                "sessionId": session["id"],
                "operation": "official_runtime_invoke",
                "objective": "Prepare official adapter invocation without private artifacts",
                "payload": {"modelId": "codex-5.5-unlimited"},
            },
        )
        assert accepted.status_code == 200
        assert accepted.json()["accepted"] is True
        assert accepted.json()["bridgeMode"] == "secure_official_adapter_boundary"

        blocked = client.post(
            "/codex/secure-runtime/request",
            headers=headers,
            json={
                "sessionId": session["id"],
                "operation": "copy_model_checkpoints",
                "objective": "Should require approved restricted access",
                "payload": {},
            },
        )
        assert blocked.status_code == 428

        index = client.post(
            "/context/index",
            headers=headers,
            json={"sessionId": session["id"], "name": "RC3 context", "source": "workspace", "fileCount": 120, "graphNodes": 450, "graphEdges": 900},
        )
        assert index.status_code == 200
        assert index.json()["status"] == "indexed"

        query = client.post("/context/query", headers=headers, json={"query": "runtime bridge policy", "sessionId": session["id"]})
        assert query.status_code == 200
        assert query.json()["localOnly"] is True
        assert query.json()["capsule"]["budgetPolicy"] == "ranked_context_capsule"

        skills = client.get("/skill-store", headers=headers)
        assert skills.status_code == 200
        skill_ids = {item["skillId"] for item in skills.json()}
        assert "codex.secure-runtime-review" in skill_ids
        assert "context.prewarm" in skill_ids

        release = client.get("/release/windows/manifest", headers=headers)
        assert release.status_code == 200
        release_payload = release.json()
        assert release_payload["platform"] == "windows"
        assert release_payload["includesPrivateCodexArtifacts"] is False
        assert "AIOS-Codex-Unlimited.cmd" in release_payload["files"]


def test_rc4_official_integration_readiness_and_restricted_access_registry() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)

        readiness = client.get("/official-integration/readiness", headers=headers)
        assert readiness.status_code == 200
        readiness_payload = readiness.json()
        assert readiness_payload["phase"] == "RC4_OFFICIAL_INTEGRATION_READINESS"
        assert readiness_payload["contractAuthority"]["locked"] is True
        assert readiness_payload["adapter"]["targetClass"] == "OfficialCodexRuntimeAdapter"
        assert readiness_payload["runtime"]["sandboxApproved"] is True
        assert readiness_payload["runtime"]["stagingApproved"] is True
        assert readiness_payload["runtime"]["productionStatus"] == "conditional"

        contract = client.get("/official-integration/adapter/contract", headers=headers)
        assert contract.status_code == 200
        contract_payload = contract.json()
        assert "requestSchema" in contract_payload
        assert "streamEventSchema" in contract_payload
        assert "toolCallSchema" in contract_payload
        assert contract_payload["timeouts"]["defaultSeconds"] == 120

        credential_status = client.get("/official-integration/credentials/status", headers=headers)
        assert credential_status.status_code == 200
        credential_payload = credential_status.json()
        assert credential_payload["secretsExposed"] is False
        assert credential_payload["storageRequirement"] == "Vault/KMS"

        request = client.post(
            "/restricted-access/requests",
            headers=headers,
            json={
                "operation": "runtime_patch",
                "environment": "sandbox_approved_machine",
                "justification": "Patch runtime compatibility for OfficialCodexRuntimeAdapter validation",
                "artifactName": "codex-runtime-sandbox",
                "artifactHash": "sha256:placeholder-for-approved-artifact",
                "pathScope": r"C:\AIOS\aios-codex-unlimited-enterprise-v2",
                "expiresInDays": 30,
            },
        )
        assert request.status_code == 200
        request_payload = request.json()
        assert request_payload["status"] == "requested"
        assert request_payload["operation"] == "runtime_patch"

        decision = client.patch(
            f"/restricted-access/requests/{request_payload['id']}/decision",
            headers=headers,
            json={"decision": "approved", "approver": "OpenAI/Codex designated approver", "notes": "Approved by meeting decision"},
        )
        assert decision.status_code == 200
        assert decision.json()["status"] == "approved"
        assert decision.json()["activeApproval"] is True

        access_log = client.post(
            f"/restricted-access/requests/{request_payload['id']}/access-log",
            headers=headers,
            json={
                "action": "runtime_patch_dry_run",
                "artifactPath": r"C:\AIOS\aios-codex-unlimited-enterprise-v2\restricted\codex-runtime-sandbox.bin",
                "artifactHash": "sha256:placeholder-for-approved-artifact",
                "justification": "Record approved patch dry-run under contract controls",
                "result": "recorded",
            },
        )
        assert access_log.status_code == 200
        assert access_log.json()["details"]["machineScopeApproved"] is True

        logs = client.get(f"/restricted-access/requests/{request_payload['id']}/access-log", headers=headers)
        assert logs.status_code == 200
        assert logs.json()[0]["details"]["action"] == "runtime_patch_dry_run"

        conditional_session = client.post("/sessions", headers=headers, json={"title": "Conditional Restricted Operation", "objective": "Validate contract controls"}).json()
        conditional = client.post(
            "/codex/secure-runtime/request",
            headers=headers,
            json={
                "sessionId": conditional_session["id"],
                "operation": "runtime_patch",
                "objective": "Execute through secure bridge with approved restricted access request",
                "payload": {"restrictedAccessRequestId": request_payload["id"]},
            },
        )
        assert conditional.status_code == 200
        assert conditional.json()["accepted"] is True

        dry_run = client.post(
            "/official-integration/adapter/dry-run",
            headers=headers,
            json={"modelId": "codex-5.5-unlimited", "objective": "Validate official adapter contract without sending secrets"},
        )
        assert dry_run.status_code == 200
        dry_payload = dry_run.json()
        assert dry_payload["accepted"] is True
        assert dry_payload["adapter"] == "OfficialCodexRuntimeAdapter"
        assert dry_payload["networkCallPerformed"] is False


def test_rc5_official_sandbox_blocks_live_activation_without_secure_environment() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)

        security = client.get("/official-sandbox/security-check", headers=headers)
        assert security.status_code == 200
        security_payload = security.json()
        assert security_payload["phase"] == "RC5_OFFICIAL_SANDBOX_ACTIVATION"
        assert security_payload["secretsExposed"] is False
        assert security_payload["frontendExposureAllowed"] is False
        assert security_payload["secureEnvironmentReady"] is False
        assert security_payload["canInvokeLiveRuntime"] is False
        assert security_payload["state"] == "blocked_until_secure_environment"
        assert "AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT" in security_payload["missing"]

        activation = client.get("/official-sandbox/activation", headers=headers)
        assert activation.status_code == 200
        activation_payload = activation.json()
        assert activation_payload["activationState"] == "blocked_until_secure_environment"
        assert activation_payload["canInvokeLiveRuntime"] is False
        assert activation_payload["networkCallPerformed"] is False

        blocked = client.post("/official-sandbox/activate", headers=headers)
        assert blocked.status_code == 412
        assert "secure environment" in blocked.json()["detail"].lower()


def test_rc5_real_sandbox_data_profile_requires_redaction_and_public_export_block() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)

        unsafe = client.post(
            "/official-sandbox/data-profiles",
            headers=headers,
            json={
                "profileId": "unsafe-real-data",
                "name": "Unsafe real data",
                "dataClassification": "real_sandbox_approved",
                "approvalReference": "meeting-2026-05-09",
                "redactionRequired": False,
                "publicExportAllowed": False,
                "retentionDays": 30,
            },
        )
        assert unsafe.status_code == 422

        created = client.post(
            "/official-sandbox/data-profiles",
            headers=headers,
            json={
                "profileId": "rc5-real-data-approved",
                "name": "RC5 Real Data Approved",
                "dataClassification": "real_sandbox_approved",
                "approvalReference": "meeting-2026-05-09",
                "redactionRequired": True,
                "publicExportAllowed": False,
                "retentionDays": 30,
            },
        )
        assert created.status_code == 200
        created_payload = created.json()
        assert created_payload["realDataApproved"] is True
        assert created_payload["redactionRequired"] is True
        assert created_payload["publicExportAllowed"] is False
        assert created_payload["status"] == "active"

        profiles = client.get("/official-sandbox/data-profiles", headers=headers)
        assert profiles.status_code == 200
        assert "rc5-real-data-approved" in {item["profileId"] for item in profiles.json()}


def test_rc5_azure_foundry_provider_profile_uses_documented_endpoint_key_and_deployment(monkeypatch) -> None:
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_PROVIDER", "azure_openai")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://aios-foundry.openai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "realistic-azure-api-key-value-for-tests")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-codex")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID", "foundry-sandbox-aios")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_SECRET_STORE", "vault")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED", "true")
    get_settings.cache_clear()
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)

            security = client.get("/official-sandbox/security-check", headers=headers)
            assert security.status_code == 200
            payload = security.json()
            assert payload["provider"] == "azure_openai"
            assert payload["secureEnvironmentReady"] is True
            assert payload["canInvokeLiveRuntime"] is True
            assert payload["tenantConfigured"] is False
            assert payload["providerRequirements"]["credential"] == "AZURE_OPENAI_API_KEY"

            profile = client.get("/official-sandbox/provider-profile", headers=headers)
            assert profile.status_code == 200
            profile_payload = profile.json()
            assert profile_payload["provider"] == "azure_openai"
            assert profile_payload["credentialSource"] == "AZURE_OPENAI_API_KEY"
            assert profile_payload["baseUrlConfigured"] is True
            assert profile_payload["deploymentConfigured"] is True
            assert profile_payload["secretsExposed"] is False
    finally:
        get_settings.cache_clear()


def test_rc5_openai_api_provider_uses_api_key_default_endpoint_and_optional_project(monkeypatch) -> None:
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_PROVIDER", "openai_api")
    monkeypatch.setenv("OPENAI_API_KEY", "realistic-openai-api-key-value-for-tests")
    monkeypatch.setenv("OPENAI_PROJECT_ID", "proj_aios_rc5")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID", "openai-api-sandbox-aios")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_SECRET_STORE", "vault")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED", "true")
    get_settings.cache_clear()
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)

            security = client.get("/official-sandbox/security-check", headers=headers)
            assert security.status_code == 200
            payload = security.json()
            assert payload["provider"] == "openai_api"
            assert payload["secureEnvironmentReady"] is True
            assert payload["canInvokeLiveRuntime"] is True
            assert payload["tenantConfigured"] is False
            assert payload["providerRequirements"]["credential"] == "OPENAI_API_KEY"
            assert payload["providerRequirements"]["endpoint"] == "default https://api.openai.com/v1 or OPENAI_BASE_URL"

            profile = client.get("/official-sandbox/provider-profile", headers=headers)
            assert profile.status_code == 200
            profile_payload = profile.json()
            assert profile_payload["provider"] == "openai_api"
            assert profile_payload["baseUrlConfigured"] is True
            assert profile_payload["credentialSource"] == "OPENAI_API_KEY"
            assert profile_payload["projectConfigured"] is True
            assert profile_payload["deploymentConfigured"] is False
            assert profile_payload["secretsExposed"] is False
    finally:
        get_settings.cache_clear()


def test_rc6_openai_runtime_invoke_calls_responses_api_and_records_output(monkeypatch) -> None:
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_PROVIDER", "openai_api")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.2-codex")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID", "openai-api-sandbox-aios")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_SECRET_STORE", "vault")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED", "true")
    get_settings.cache_clear()
    captured: dict[str, object] = {}

    class FakeResponse:
        status_code = 200

        def json(self) -> dict:
            return {
                "id": "resp_rc6_test",
                "status": "completed",
                "output_text": "RC6 OpenAI runtime real path ready.",
                "usage": {"input_tokens": 10, "output_tokens": 8},
            }

        def raise_for_status(self) -> None:
            return None

    def fake_post(self, url, *args, **kwargs):  # noqa: ANN001
        if str(url).startswith("/"):
            return original_post(self, url, *args, **kwargs)
        captured["url"] = url
        captured["headers"] = kwargs.get("headers")
        captured["json"] = kwargs.get("json")
        return FakeResponse()

    original_post = httpx.Client.post
    monkeypatch.setattr(httpx.Client, "post", fake_post)
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)
            session = client.post("/sessions", headers=headers, json={"title": "RC6 Runtime", "objective": "Call OpenAI"}).json()

            invoke = client.post(
                "/codex/runtime/invoke",
                headers=headers,
                json={"session_id": session["id"], "model_id": "codex-5.5-unlimited", "objective": "Validate real OpenAI runtime path"},
            )
            assert invoke.status_code == 200
            payload = invoke.json()
            assert payload["accepted"] is True
            assert payload["completed"] is True
            assert payload["networkCallPerformed"] is True
            assert payload["provider"] == "openai_api"
            assert payload["responseId"] == "resp_rc6_test"
            assert payload["outputText"] == "RC6 OpenAI runtime real path ready."
            assert payload["runtimeModelId"] == "gpt-5.2-codex"
            assert "sk-test" not in str(payload)

            assert captured["url"] == "https://api.openai.com/v1/responses"
            assert captured["headers"]["Authorization"] == "Bearer test-key"
            assert captured["json"]["model"] == "gpt-5.2-codex"
            assert captured["json"]["metadata"]["aios_session_id"] == session["id"]

            workbench = client.get(f"/sessions/{session['id']}/workbench", headers=headers).json()
            event_types = {item["type"] for item in workbench["recentEvents"]}
            assert "codex.runtime.completed" in event_types
            assert workbench["runtimeAdapter"]["name"] == "OfficialCodexRuntimeAdapter"
            assert workbench["runtimeAdapter"]["provider"] == "openai_api"
            assert workbench["buildStatus"]["status"] in {"not_queued", "queued", "running", "completed", "failed"}
    finally:
        get_settings.cache_clear()


def test_rc11_runtime_model_discovery_blocks_without_secure_environment() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)

        response = client.get("/codex/runtime/model-discovery", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["phase"] == "RC11_RUNTIME_MODEL_DISCOVERY"
        assert payload["status"] == "blocked_until_secure_environment"
        assert payload["networkCallPerformed"] is False
        assert payload["secretsExposed"] is False
        assert "OPENAI_API_KEY" in payload["missing"]


def test_rc11_runtime_model_discovery_selects_available_openai_model(monkeypatch) -> None:
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_PROVIDER", "openai_api")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_PROJECT_ID", "proj_aios_rc11")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID", "openai-api-sandbox-aios")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_SECRET_STORE", "vault")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED", "true")
    get_settings.cache_clear()
    captured: dict[str, object] = {}

    class FakeModelsResponse:
        status_code = 200

        def json(self) -> dict:
            return {
                "data": [
                    {"id": "gpt-5.2-codex"},
                    {"id": "gpt-5.1-codex-mini"},
                    {"id": "gpt-4.1"},
                ]
            }

        def raise_for_status(self) -> None:
            return None

    def fake_get(self, url, *args, **kwargs):  # noqa: ANN001
        if str(url).startswith("/"):
            return original_get(self, url, *args, **kwargs)
        captured["url"] = url
        captured["headers"] = kwargs.get("headers")
        return FakeModelsResponse()

    original_get = httpx.Client.get
    monkeypatch.setattr(httpx.Client, "get", fake_get)
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)

            response = client.get("/codex/runtime/model-discovery", headers=headers)
            assert response.status_code == 200
            payload = response.json()
            assert payload["status"] == "model_available"
            assert payload["networkCallPerformed"] is True
            assert payload["recommendedModel"] == "gpt-5.2-codex"
            assert "gpt-5.2-codex" in payload["availableCandidates"]
            assert payload["selectedModelCommand"] == '$env:OPENAI_MODEL = "gpt-5.2-codex"'
            assert payload["secretsExposed"] is False
            assert "sk-test" not in str(payload)

            assert captured["url"] == "https://api.openai.com/v1/models"
            assert captured["headers"]["Authorization"] == "Bearer test-key"
            assert captured["headers"]["OpenAI-Project"] == "proj_aios_rc11"
    finally:
        get_settings.cache_clear()


def test_rc21_runtime_broker_catalog_explainability_and_no_false_live(monkeypatch) -> None:
    for name in [
        "AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT",
        "AIOS_OFFICIAL_CODEX_SERVICE_TOKEN",
        "AIOS_OFFICIAL_CODEX_TENANT_ID",
        "AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID",
        "AIOS_OFFICIAL_SANDBOX_SECRET_STORE",
        "AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED",
    ]:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("AIOS_OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("AIOS_OLLAMA_MODEL", "deepseek-v4-pro:cloud")
    get_settings.cache_clear()

    def fake_get(self, url, *args, **kwargs):  # noqa: ANN001
        if str(url).startswith("/"):
            return original_get(self, url, *args, **kwargs)
        raise httpx.ConnectError("ollama is not running")

    original_get = httpx.Client.get
    monkeypatch.setattr(httpx.Client, "get", fake_get)
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)

            catalog = client.get("/runtime/broker/providers", headers=headers)
            assert catalog.status_code == 200
            catalog_payload = catalog.json()
            assert catalog_payload["phase"] == "RC21_RUNTIME_BROKER_2"
            provider_ids = [item["providerId"] for item in catalog_payload["providers"]]
            assert provider_ids == [
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
            official = catalog_payload["providers"][0]
            simulator = catalog_payload["providers"][-1]
            assert official["officialRuntime"] is True
            assert official["liveRuntimeGate"] == "runtime_binding_active"
            assert simulator["officialRuntime"] is False
            assert simulator["canClaimLiveRuntime"] is False

            status = client.get("/runtime/broker/status", headers=headers)
            assert status.status_code == 200
            status_payload = status.json()
            assert status_payload["phase"] == "RC21_RUNTIME_BROKER_2"
            assert status_payload["canInvokeLiveRuntime"] is False
            assert status_payload["liveRuntimeProvider"] == ""
            assert status_payload["recommendedProvider"] == "puter_user_pays_browser"
            assert status_payload["providerOrder"] == provider_ids
            for provider_id, provider_status in status_payload["providers"].items():
                if provider_id != "official_codex_runtime":
                    assert provider_status["canInvokeLiveRuntime"] is False
            assert status_payload["providers"]["official_codex_runtime"]["canInvokeLiveRuntime"] is False
            assert status_payload["selection"]["reasonCode"] == "browser_user_pays_available"
            assert status_payload["secretsExposed"] is False

            explanation = client.get("/runtime/broker/explain?provider=codex_delegated", headers=headers)
            assert explanation.status_code == 200
            explanation_payload = explanation.json()
            assert explanation_payload["phase"] == "RC21_RUNTIME_BROKER_2"
            assert explanation_payload["provider"]["providerId"] == "codex_delegated"
            assert explanation_payload["provider"]["canInvokeLiveRuntime"] is False
            assert explanation_payload["claimBoundary"]["canInvokeLiveRuntime"] is False
            assert "nao altera canInvokeLiveRuntime" in explanation_payload["claimBoundary"]["message"]
            assert explanation_payload["secretsExposed"] is False

            audit_logs = client.get("/admin/audit-logs", headers=headers)
            assert audit_logs.status_code == 200
            assert any(item["action"] == "aios.runtime_broker.provider_selected" for item in audit_logs.json())
    finally:
        get_settings.cache_clear()


def test_rc23_codex_delegated_auth_status_never_reads_or_exposes_auth_json(monkeypatch, tmp_path) -> None:
    codex_home = tmp_path / ".codex"
    codex_home.mkdir()
    auth_file = codex_home / "auth.json"
    auth_file.write_text('{"auth_mode":"chatgpt","tokens":{"access_token":"secret-value"}}', encoding="utf-8")
    monkeypatch.setenv("CODEX_HOME", str(codex_home))

    with TestClient(app) as client:
        headers = auth_headers(client)

        response = client.get("/codex/delegated-auth/status", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["phase"] == "RC23_CODEX_DELEGATED_AUTH_BOUNDARY"
        assert payload["provider"] == "codex_delegated"
        assert payload["authMode"] == "chatgpt_managed"
        assert payload["authFilePresent"] is True
        assert payload["authJsonManagedByAIOS"] is False
        assert payload["authJsonContentRead"] is False
        assert payload["apiKeyStoredByAIOS"] is False
        assert payload["tokenValuesExposed"] is False
        assert payload["secretsExposed"] is False
        assert payload["canInvokeLiveRuntime"] is False
        assert payload["claimBoundary"]["message"].startswith("Auth presence does not activate")
        assert "read_auth_json_contents" in payload["blockedOperations"]
        assert "secret-value" not in str(payload)
        assert str(auth_file) not in str(payload)


def test_rc12_runtime_broker_reports_ollama_provider_without_required_secret(monkeypatch) -> None:
    monkeypatch.setenv("AIOS_OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("AIOS_OLLAMA_MODEL", "deepseek-v4-pro:cloud")
    get_settings.cache_clear()

    def fake_get(self, url, *args, **kwargs):  # noqa: ANN001
        if str(url).startswith("/"):
            return original_get(self, url, *args, **kwargs)
        raise httpx.ConnectError("ollama is not running")

    original_get = httpx.Client.get
    monkeypatch.setattr(httpx.Client, "get", fake_get)
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)

            providers = client.get("/runtime/broker/providers", headers=headers)
            assert providers.status_code == 200
            payload = providers.json()
            provider_ids = {item["providerId"] for item in payload["providers"]}
            assert "ollama_local_cloud" in provider_ids
            ollama = next(item for item in payload["providers"] if item["providerId"] == "ollama_local_cloud")
            assert ollama["requiresDeveloperApiKey"] is False
            assert ollama["defaultModel"] == "deepseek-v4-pro:cloud"

            status = client.get("/runtime/broker/status", headers=headers)
            assert status.status_code == 200
            status_payload = status.json()
            assert status_payload["phase"] == "RC21_RUNTIME_BROKER_2"
            assert status_payload["recommendedProvider"] != "ollama_local_cloud"
            assert status_payload["providers"]["ollama_local_cloud"]["available"] is False
            assert status_payload["providers"]["ollama_local_cloud"]["requiresDeveloperApiKey"] is False
            assert status_payload["secretsExposed"] is False
    finally:
        get_settings.cache_clear()


def test_rc12_runtime_broker_invokes_ollama_and_records_cognitive_mesh_event(monkeypatch) -> None:
    monkeypatch.setenv("AIOS_OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("AIOS_OLLAMA_MODEL", "deepseek-v4-pro:cloud")
    get_settings.cache_clear()
    captured: dict[str, object] = {}

    class FakeTagsResponse:
        status_code = 200

        def json(self) -> dict:
            return {"models": [{"name": "deepseek-v4-pro:cloud"}, {"name": "gpt-oss:120b-cloud"}]}

        def raise_for_status(self) -> None:
            return None

    class FakeChatResponse:
        status_code = 200

        def json(self) -> dict:
            return {
                "model": "deepseek-v4-pro:cloud",
                "message": {
                    "role": "assistant",
                    "content": "Plano, execucao e revisao completos pelo Runtime Broker.",
                },
                "done": True,
            }

        def raise_for_status(self) -> None:
            return None

    def fake_get(self, url, *args, **kwargs):  # noqa: ANN001
        if str(url).startswith("/"):
            return original_get(self, url, *args, **kwargs)
        captured["tagsUrl"] = url
        return FakeTagsResponse()

    def fake_post(self, url, *args, **kwargs):  # noqa: ANN001
        if str(url).startswith("/"):
            return original_post(self, url, *args, **kwargs)
        captured["chatUrl"] = url
        captured["chatJson"] = kwargs.get("json")
        return FakeChatResponse()

    original_get = httpx.Client.get
    original_post = httpx.Client.post
    monkeypatch.setattr(httpx.Client, "get", fake_get)
    monkeypatch.setattr(httpx.Client, "post", fake_post)
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)
            session = client.post("/sessions", headers=headers, json={"title": "RC12 Broker", "objective": "Invoke Ollama broker"}).json()

            response = client.post(
                "/runtime/broker/invoke",
                headers=headers,
                json={
                    "sessionId": session["id"],
                    "objective": "Criar uma arquitetura premium de Codex baseada em sessoes.",
                    "provider": "auto",
                    "intelligenceMode": "aios_cognitive_runtime_mesh",
                },
            )
            assert response.status_code == 200
            payload = response.json()
            assert payload["accepted"] is True
            assert payload["provider"] == "ollama_local_cloud"
            assert payload["model"] == "deepseek-v4-pro:cloud"
            assert payload["runtimeClass"] == "AIOSCognitiveRuntimeMesh"
            assert payload["networkCallPerformed"] is True
            assert payload["qualityGate"]["status"] in {"passed", "review"}
            assert "Plano, execucao" in payload["outputText"]
            assert "token" not in str(payload["userVisibleUsage"]).lower()

            assert captured["tagsUrl"] == "http://localhost:11434/api/tags"
            assert captured["chatUrl"] == "http://localhost:11434/api/chat"
            assert captured["chatJson"]["model"] == "deepseek-v4-pro:cloud"
            assert captured["chatJson"]["stream"] is False
            assert captured["chatJson"]["messages"][0]["role"] == "system"

            workbench = client.get(f"/sessions/{session['id']}/workbench", headers=headers).json()
            event_types = {item["type"] for item in workbench["recentEvents"]}
            assert "codex.runtime.completed" in event_types
            mesh_events = [item for item in workbench["recentEvents"] if item["type"] == "codex.runtime.completed"]
            assert mesh_events[0]["payload"]["runtimeClass"] == "AIOSCognitiveRuntimeMesh"
    finally:
        get_settings.cache_clear()


def test_rc13_license_status_reports_missing_local_license(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("AIOS_LICENSE_PATH", str(tmp_path / "license.cert"))
    get_settings.cache_clear()
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)
            response = client.get("/license/status", headers=headers)
            assert response.status_code == 200
            payload = response.json()
            assert payload["phase"] == "RC13_LOCAL_LICENSE"
            assert payload["status"] == "restricted"
            assert payload["licensePresent"] is False
            assert payload["hashAuthorized"] is False
            assert payload["unlocksOfficialRuntime"] is False
            assert payload["authorizesOfficialRuntime"] is False
            assert payload["technicalCredentialStoredInLicense"] is False
            assert payload["secretsExposed"] is False
    finally:
        get_settings.cache_clear()


def test_rc13_license_status_accepts_pre_authorized_local_license(monkeypatch, tmp_path) -> None:
    license_file = tmp_path / "license.cert"
    license_file.write_text("AIOS-CODEX-UNLIMITED-LOCAL-RC13-LICENSE", encoding="utf-8")
    monkeypatch.setenv("AIOS_LICENSE_PATH", str(license_file))
    get_settings.cache_clear()
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)
            response = client.get("/license/status", headers=headers)
            assert response.status_code == 200
            payload = response.json()
            assert payload["status"] == "local_unlimited_enabled"
            assert payload["licensePresent"] is True
            assert payload["hashAuthorized"] is True
            assert payload["entitlementId"] == "aios_codex_unlimited"
            assert payload["priorityClass"] == "premium_unlimited"
            assert payload["productUnit"] == "codex_sessions"
            assert payload["authorizesOfficialRuntime"] is True
            assert payload["authorizesPersistentServiceTokens"] is True
            assert payload["allowsControlledRuntimeArtifacts"] is True
            assert payload["runtimeCredentialBinding"] == "service_token_vault_kms_or_secure_runtime_bridge"
            assert payload["providerBillingMode"] == "approved_runtime_service_account_policy"
            assert payload["technicalCredentialStoredInLicense"] is False
            assert payload["unlocksOfficialRuntime"] is True
            assert payload["unlocksProviderBilling"] is True
            assert payload["hash"].startswith("2dab9a98")
            assert "AIOS-CODEX-UNLIMITED-LOCAL-RC13-LICENSE" not in str(payload)
    finally:
        get_settings.cache_clear()


def test_rc14_scope_authority_reads_license_contracts_and_signature_evidence() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.get("/scope/authority", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["phase"] == "RC14_SCOPE_AUTHORITY_READER"
        assert payload["scopeReady"] is True
        assert payload["precedence"][0] == "license.cert"
        assert payload["license"]["hashAuthorized"] is True
        assert payload["license"]["entitlementId"] == "aios_codex_unlimited"
        assert payload["contracts"]["locked"] is True
        assert payload["contracts"]["hashesVerified"] is True
        assert payload["signatureEvidence"]["samAltmanSignaturePresent"] is True
        assert payload["signatureEvidence"]["fidjiSimoSignaturePresent"] is True
        assert payload["runtimeBinding"] == "service_token_vault_kms_or_secure_runtime_bridge"
        assert payload["secretsExposed"] is False


def test_rc15_scope_preflight_authorizes_scoped_runtime_and_reports_binding_state() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.post(
            "/scope/preflight",
            headers=headers,
            json={
                "operation": "codex.runtime.invoke",
                "environment": "sandbox",
                "modelId": "codex-5.5-unlimited",
                "requiresLiveRuntime": True,
                "requiresRestrictedArtifacts": False,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["phase"] == "RC15_SCOPE_PREFLIGHT"
        assert payload["scopeReady"] is True
        assert payload["scopeDecision"] == "allow"
        assert payload["requested"]["operation"] == "codex.runtime.invoke"
        assert payload["requested"]["modelId"] == "codex-5.5-unlimited"
        assert payload["executionState"] in {"ready_for_live_runtime", "awaiting_technical_binding"}
        assert payload["runtimeBinding"] == "service_token_vault_kms_or_secure_runtime_bridge"
        assert payload["userVisibleMeter"] == "none"
        assert payload["secretsExposed"] is False
        assert "license.cert" in payload["evidence"]["precedence"][0]


def test_rc15_scope_preflight_blocks_unapproved_model() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.post(
            "/scope/preflight",
            headers=headers,
            json={
                "operation": "codex.runtime.invoke",
                "environment": "sandbox",
                "modelId": "unapproved-model",
                "requiresLiveRuntime": True,
            },
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["phase"] == "RC15_SCOPE_PREFLIGHT"
        assert payload["scopeDecision"] == "block"
        assert "MODEL_NOT_APPROVED" in payload["blockingReasons"]
        assert payload["secretsExposed"] is False


def test_rc16_runtime_binding_status_reports_missing_secure_binding_without_exposing_secret() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.get("/runtime/binding/status", headers=headers)
        assert response.status_code == 200
        payload = response.json()
        assert payload["phase"] == "RC16_RUNTIME_BINDING_GATE"
        assert payload["scopeReady"] is True
        assert payload["bindingState"] in {"awaiting_secure_runtime_binding", "live_runtime_ready"}
        assert payload["productUnit"] == "codex_sessions"
        assert payload["userVisibleMeter"] == "none"
        assert payload["secretsExposed"] is False
        assert payload["credential"]["secretValueExposed"] is False
        assert payload["credential"]["storageRequirement"] == "Vault/KMS or Secure Runtime Bridge"
        assert "codex-5.5-unlimited" in payload["approvedModels"]
        assert "OPENAI_API_KEY" not in str(payload.get("credential", {}).get("secretPreview", ""))


def test_rc16_runtime_binding_status_allows_live_openai_api_when_secure_flags_exist(monkeypatch) -> None:
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_PROVIDER", "openai_api")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-rc16-secret")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID", "sandbox-rc16")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_SECRET_STORE", "vault")
    monkeypatch.setenv("AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED", "true")
    get_settings.cache_clear()
    try:
        with TestClient(app) as client:
            headers = auth_headers(client)
            response = client.get("/runtime/binding/status", headers=headers)
            assert response.status_code == 200
            payload = response.json()
            assert payload["phase"] == "RC16_RUNTIME_BINDING_GATE"
            assert payload["bindingState"] == "active"
            assert payload["canInvokeLiveRuntime"] is True
            assert payload["provider"] == "openai_api"
            assert payload["credential"]["configured"] is True
            assert payload["credential"]["reference"] == "OPENAI_API_KEY"
            assert payload["environment"]["sandboxEnvironmentConfigured"] is True
            assert payload["environment"]["secretStore"] == "vault"
            assert payload["secretsExposed"] is False
            assert "sk-test-rc16-secret" not in str(payload)
    finally:
        get_settings.cache_clear()


def test_abuse_evaluator_shapes_risky_usage() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        response = client.post(
            "/abuse/evaluate",
            headers=headers,
            json={"toolCallFlood": 3, "failedBuilds": 1, "sessionSpike": 0, "suspiciousCommand": False},
        )
        assert response.status_code == 200
        assert response.json()["action"] in {"shape", "degrade", "review"}


def test_redacted_export_masks_sensitive_values() -> None:
    with TestClient(app) as client:
        headers = auth_headers(client)
        payload = client.get("/export/redacted-bundle", headers=headers).json()
        as_text = str(payload)
        assert "sk-demo" not in as_text
        assert "AiosAdmin123" not in as_text
        assert "[REDACTED]" in as_text


def teardown_module() -> None:
    engine.dispose()
    db_file = Path("test_aios.db")
    if db_file.exists():
        db_file.unlink()
