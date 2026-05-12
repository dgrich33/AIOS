# RC27 AIOS Native Runtime Fabric Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build RC27 runtime fabric so AIOS can honestly report live validated runtimes without depending on official production binding.

**Architecture:** Add a focused backend runtime fabric module inside the existing FastAPI app, expose fabric/model-policy endpoints, surface the status in the React Workbench, and keep the legacy local adapter intact. Provider status is computed from explicit environment flags and existing AIOS session capabilities, with production official status kept separate.

**Tech Stack:** FastAPI, SQLAlchemy test client, React/TypeScript/Vite, Playwright, PowerShell.

---

### Task 1: Backend Tests

**Files:**
- Modify: `backend/tests/test_api.py`

- [ ] **Step 1: Write failing tests for RC27 status and model policy**

Add tests that expect:

```python
def test_rc27_runtime_fabric_status_is_aios_first_and_secret_safe() -> None:
    with TestClient(app) as client:
        payload = client.get("/runtime/fabric/status").json()
        assert payload["runtimeFabricId"] == "aios_runtime_fabric"
        assert payload["components"]["aios_native_runtime"] == "ready"
        assert payload["canInvokeLiveRuntime"] is True
        assert payload["officialProduction"] is False
        assert payload["productionBlocked"] is True
        assert payload["secretsExposed"] is False
        assert payload["activeRuntimeProvider"] == "aios_native_runtime"
        assert "official_codex_runtime" in payload["providers"]


def test_rc27_model_policy_registry_tracks_codex_and_gpt4o_without_claiming_live() -> None:
    with TestClient(app) as client:
        payload = client.get("/runtime/fabric/model-policy").json()
        model_ids = {item["modelId"] for item in payload["models"]}
        assert "gpt-5.2-codex" in model_ids
        assert "gpt-4o" in model_ids
        for item in payload["models"]:
            if item["modelId"] in {"gpt-5.2-codex", "gpt-4o"}:
                assert item["availability"] == "provider_discovery_required"
                assert item["active"] is False
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `cd backend; python -m pytest .\tests\test_api.py -q`

Expected: FAIL because `/runtime/fabric/status` and `/runtime/fabric/model-policy` do not exist yet.

### Task 2: Backend Runtime Fabric

**Files:**
- Modify: `backend/app/main.py`

- [ ] **Step 1: Implement provider/model helpers**

Add helper functions near `audit()`:

```python
def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
```

Provider and model helper functions return dictionaries only, never secrets.

- [ ] **Step 2: Add `/runtime/fabric/status`**

Return status with `canInvokeLiveRuntime=true` from `aios_native_runtime`, `officialProduction=false`, `productionBlocked=true`, and provider map.

- [ ] **Step 3: Add `/runtime/fabric/model-policy`**

Return model policy entries for `gpt-5.2-codex`, `gpt-4o`, `aios-native-session`, and `controlled-simulator`.

- [ ] **Step 4: Add runtime capabilities to `/control-plane/status`**

Append `aios_runtime_fabric`, `aios_native_runtime`, `aios_session_runtime`, `aios_agent_room_runtime`, `provider_discovery`, and `model_policy_registry` to the capabilities list.

- [ ] **Step 5: Run backend tests**

Run: `cd backend; python -m pytest .\tests\test_api.py -q`

Expected: PASS.

### Task 3: Frontend Workbench Panel

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/api.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/style.css`
- Modify: `frontend/tests/workbench.spec.js`

- [ ] **Step 1: Add TypeScript types**

Add `RuntimeFabricStatus` and `ModelPolicyRegistry` types.

- [ ] **Step 2: Add API methods**

Add `getRuntimeFabricStatus()` and `getModelPolicyRegistry()`.

- [ ] **Step 3: Load status in refresh**

Fetch runtime fabric and model policy together with entitlement/control plane/sessions.

- [ ] **Step 4: Render panel**

Render a `RC27 AIOS Native Runtime Fabric` panel showing active provider, live status, official production status, production block reason, provider chips, and model policy entries.

- [ ] **Step 5: Update Playwright smoke**

Expect the new panel title and model entries after login.

### Task 4: Docs and Script

**Files:**
- Create: `docs/RC27_AIOS_NATIVE_RUNTIME_FABRIC.md`
- Create: `scripts/rc27-native-runtime-fabric-check.ps1`

- [ ] **Step 1: Write RC27 docs**

Explain the AIOS-first runtime narrative, provider statuses, model policy registry, and honest production status.

- [ ] **Step 2: Write validation script**

Run backend tests, frontend build, Playwright, MCP builds, and a GET check for `/runtime/fabric/status` when the backend is running.

### Task 5: Verification

**Commands:**

```powershell
cd C:\Users\dg71\Documents\Codex\2026-05-08\aios-codex-unlimited-recapitula-o-completa\artifacts\aios-codex-unlimited-enterprise-v2\backend
python -m pytest .\tests\test_api.py -q

cd ..\frontend
npm run build
npx playwright test

cd ..\mcp\aios-mcp-repo
npm run build

cd ..\aios-mcp-core
npm run build
```

Expected: all pass or any remaining failure is documented with exact output.
