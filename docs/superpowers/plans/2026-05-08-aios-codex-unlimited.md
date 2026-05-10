# AIOS Codex Unlimited - Plano Historico Executado

**Goal:** Create a runnable local AIOS Codex Unlimited prototype with backend, frontend Workbench, MCP servers, infra, scripts, tests, and docs.

**Architecture:** The backend owns product state and policy. The frontend uses only API calls. The Codex runtime is isolated behind an adapter. MCP servers provide repo and control-plane tools.

**Tech Stack:** FastAPI, SQLAlchemy, PostgreSQL, Redis, React, Vite, TypeScript, PowerShell, Docker Compose, Prometheus, Grafana, Loki.

## Status

Plano historico executado. O estado vigente do projeto agora segue o contrato assinado em:

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

---

### Task 1: Backend foundation

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`
- Create: `backend/app/models.py`
- Create: `backend/app/security.py`
- Create: `backend/app/main.py`
- Test: `backend/tests/test_api.py`

- [x] Write API tests for health, entitlement, sessions, snapshots, QoS, abuse, and redaction.
- [x] Implement the minimal backend to pass those tests.
- [x] Keep entitlement explicitly session-based.

### Task 2: Workbench frontend

**Files:**
- Create: `frontend/src/api.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/style.css`

- [x] Build a real API provider.
- [x] Build the Workbench screen.
- [x] Add action-level loading, not full-screen blocking.
- [x] Keep large lists internally scrollable.

### Task 3: MCP and infra

**Files:**
- Create: `mcp/aios-mcp-repo/src/server.ts`
- Create: `mcp/aios-mcp-core/src/server.ts`
- Create: `docker-compose.yml`
- Create: `infra/**`

- [x] Add repo-local tools with safe path checks.
- [x] Add AIOS core tools that call the backend.
- [x] Add observability and alerting config.

### Task 4: Validation and packaging

- [x] Run backend tests.
- [x] Run frontend build.
- [x] Run MCP builds.
- [x] Package the project as a zip for transfer.
