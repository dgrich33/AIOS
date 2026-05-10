# RC5 Official Sandbox Activation - Plano Historico Executado

**Goal:** Prepare AIOS Codex Unlimited to activate official sandbox integration only when secure runtime credentials and environment gates are actually present.

**Architecture:** RC5 adds real readiness gates instead of fake success states. The backend reports `blocked`, `ready`, or `live_enabled` based on actual environment variables, contract lock, and secure storage policy. The frontend and scripts expose this state without secrets.

**Tech Stack:** FastAPI, SQLAlchemy, React/Vite, PowerShell, MCP TypeScript.

## Status

Plano historico executado. O estado vigente do projeto agora segue o contrato assinado em:

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

---

### Task 1: Backend Contract

**Files:**
- Modify: `backend/tests/test_api.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/config.py`
- Modify: `backend/app/seed.py`
- Modify: `backend/app/main.py`

- [x] Add failing tests for `/official-sandbox/security-check`, `/official-sandbox/activation`, `/official-sandbox/data-profiles`, and `/official-sandbox/activate`.
- [x] Implement models for sandbox activation state and real-data profile metadata.
- [x] Implement endpoints that return blocked state unless secure endpoint, token, tenant and explicit live flag exist.
- [x] Verify backend tests pass.

### Task 2: Frontend and MCP

**Files:**
- Modify: `frontend/src/types.ts`
- Modify: `frontend/src/api.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/tests/workbench.spec.js`
- Modify: `mcp/aios-mcp-core/src/server.ts`

- [x] Add API types and calls for official sandbox checks.
- [x] Add an `Official Sandbox` panel showing real readiness gates.
- [x] Add MCP tools for sandbox status and data profile registration.
- [x] Verify frontend and MCP builds pass.

### Task 3: Scripts and Release

**Files:**
- Create: `scripts/rc5-validate.ps1`
- Create: `scripts/rc5-package.ps1`
- Create: `scripts/rc5-env-template.ps1`
- Create: `docs/RC5_OFFICIAL_SANDBOX_ACTIVATION.md`

- [x] Add validation script that proves no fake live activation occurs without secure env vars.
- [x] Add env-template script that prints setup commands without storing secrets.
- [x] Add package script with contract lock verification.
- [x] Run full validation and package RC5.
