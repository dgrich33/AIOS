# AIOS Codex Unlimited - Executive Demo Guide

## Positioning

AIOS Codex Unlimited turns Codex into a continuous professional development environment inside AIOS. The user experience is based on sessions, MCP tools, skills, memory, snapshots, QoS, governance, and observability.

The current RC workspace follows the signed 9 May 2026 contract recorded in:

- `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`
- `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`

The Release Candidate demonstrates:

- real backend and API docs;
- real database models;
- entitlement with no token counter and no weekly token quota;
- QoS scheduling;
- RBAC/JWT;
- Vault integration boundary;
- full observability stack;
- MCP repository and control-plane servers;
- redacted export;
- service tokens;
- base tenant model;
- an initial Codex Workbench UI.

## Run

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\doctor.ps1
docker compose up -d --build
.\scripts\enterprise-check.ps1
.\scripts\open-urls.ps1
```

## Demo path

1. Open http://localhost:5173 and sign in.
2. Show the entitlement panel: product unit is `codex_sessions`.
3. Create a Codex session in the Workbench.
4. Create a snapshot.
5. Enqueue a QoS build job.
6. Open http://localhost:8000/docs and show `/entitlement/me`, `/control-plane/status`, `/qos/enqueue`, `/codex/run`, `/codex/skill/execute`, `/export/redacted-bundle`.
7. Open Grafana at http://localhost:3001.
8. Show Vault at http://localhost:8200 as a local dev secrets boundary.
9. Build MCP servers with `.\scripts\mcp-build-all.ps1`.

## Next hardening

- Continue implementation through `OfficialCodexRuntimeAdapter` under the signed contract.
- Keep Vault/KMS, audit, redaction, tenant isolation and packaging gates aligned to the contract.
- Validate Windows ZIP/EXE/MSI release paths without shipping secrets or uncontrolled local state.
