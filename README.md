# AIOS Codex Unlimited

AIOS Codex Unlimited is the signed-contract Release Candidate workspace for a Codex-focused AI operating system. The product unit is a continuous Codex development session, not tokens, balances, or weekly quotas.

Main message:

```txt
AIOS Codex Unlimited
Codex sem limites. Desenvolvimento sem interrupcoes.
```

Campaign line:

```txt
Pare de medir uso. Comece a construir.
```

## What is implemented

- Contract authority docs aligned to the signed 9 May 2026 agreement:
  `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md` and
  `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`.
- FastAPI backend with JWT auth, RBAC, SQLAlchemy models, entitlement, sessions, snapshots, handoffs, audit logs, service tokens, tenant base, abuse evaluation, redacted export, and Codex adapter boundary.
- Session event tracking for MCP tool calls, patches, changed files, build status, snapshots, skills and handoffs.
- QoS scheduler backed by Redis when available, with an in-memory fallback for local test runs.
- React/Vite frontend with a real API provider and a Codex Workbench for active sessions, files changed, build status, MCP/logs, snapshots, handoff, and AIOS lineage.
- Two local MCP servers: repository tools and AIOS control-plane tools.
- Local `.codex/config.example.toml` and project skills for Codex operation.
- Robust demo scripts: `scripts/start.ps1` supports Docker with local fallback, and `scripts/stop.ps1` stops tracked local processes without fixed PIDs.
- Docker Compose stack for PostgreSQL, Redis, Vault, backend, worker, frontend, Prometheus, Grafana, Loki, Promtail, OpenTelemetry Collector, and Alertmanager.
- Windows PowerShell scripts for doctor, run, stop, reset, smoke tests, enterprise checks, MCP builds, Vault helper calls, and service token minting.

## Ports

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090
- Vault: http://localhost:8200
- Loki: http://localhost:3100
- Alertmanager: http://localhost:9093

## Local validation without Docker

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
python -m pip install -r .\backend\requirements.txt
$env:PYTHONPATH='backend'
python -m pytest .\backend\tests -q

cd .\frontend
npm install
npm run build

cd ..\mcp\aios-mcp-repo
npm install
npm run build

cd ..\aios-mcp-core
npm install
npm run build
```

## Full demo with Docker Desktop

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\doctor.ps1
docker compose up -d --build
.\scripts\enterprise-check.ps1
.\scripts\open-urls.ps1
```

Demo login:

```txt
admin@aios.local
AiosAdmin123!
```

## Codex MCP config example

The same example is available at `.codex/config.example.toml`.

```toml
[mcp_servers.aios_repo]
command = "node"
args = ["C:\\AIOS\\aios-codex-unlimited-enterprise-v2\\mcp\\aios-mcp-repo\\dist\\server.js"]

[mcp_servers.aios_repo.env]
AIOS_WORKSPACE = "C:\\AIOS\\aios-codex-unlimited-enterprise-v2"
AIOS_SNAPSHOT_DIR = "C:\\AIOS\\aios-codex-unlimited-enterprise-v2\\aios-snapshots"
AIOS_API_URL = "http://localhost:8000"
AIOS_SERVICE_TOKEN = "aios_st_replace_with_local_service_token"
AIOS_SESSION_ID = "replace_with_active_session_id"

[mcp_servers.aios_core]
command = "node"
args = ["C:\\AIOS\\aios-codex-unlimited-enterprise-v2\\mcp\\aios-mcp-core\\dist\\server.js"]

[mcp_servers.aios_core.env]
AIOS_API_URL = "http://localhost:8000"
AIOS_ADMIN_EMAIL = "admin@aios.local"
AIOS_ADMIN_PASSWORD = "AiosAdmin123!"
AIOS_SERVICE_TOKEN = "aios_st_replace_with_local_service_token"
```

## Real-time Workbench demo

1. Start the backend/frontend with `.\scripts\start.ps1`.
2. Open `http://localhost:5173`, log in, and create a Codex session.
3. Mint a service token with `.\scripts\mint-mcp-service-token.ps1`.
4. Put the token and active session id into `.codex/config.example.toml` or your Codex MCP config.
5. Run MCP repo tools such as `repo.apply_patch`, `repo.write_file`, or `repo.build`.
6. Click `Atualizar Workbench` to see events, files changed, build status, snapshots and handoffs.

## Project evolution docs

- `docs/CONTRACT_AUTHORITY.md`
- `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`
- `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`
- `docs/PROJECT_EVOLUTION.md`
- `docs/AIOS_LEGACY_MIGRATION_AUDIT.md`
- `docs/CODEX_WORKBENCH.md`
