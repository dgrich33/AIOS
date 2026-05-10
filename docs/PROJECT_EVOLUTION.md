# AIOS Codex Unlimited Project Evolution

This document summarizes the project history reviewed from:

- `C:\Users\dg71\Downloads\projeto oficial OpenAI recapitular`
- `C:\Users\dg71\Documents\AIOS-15-Fase3-Corrigido`

Legal and partnership statements are treated as user-provided project documentation. This repository does not independently verify contract status.

## Evolution Reviewed

1. The original AIOS was a local React/Vite workspace using localStorage.
2. It managed AI accounts, sessions, memories, keys, handoff, analytics, terminal-style commands, and Arena.IA routing.
3. The product direction moved from account management to an AI operating system for professional Codex work.
4. The final AIOS Codex Unlimited model defines the user-facing product unit as Codex sessions, not tokens, balance, credit packs, or weekly quota.
5. The enterprise base adds backend persistence, entitlement, RBAC, QoS, MCP, Vault boundary, observability, redacted export, service tokens, tenants, and a Codex runtime adapter boundary.
6. The next practical phase is Codex Workbench: active session, changed files, console/log view, MCP tool calls, build status, skill runner, snapshots, and handoff.

## Current Implementation Mapping

| Original AIOS Module | Current AIOS Codex Unlimited Target |
| --- | --- |
| Painel CEO | Control Plane and admin governance |
| Dashboard | Workbench metrics and observability |
| Arena.IA | Codex Workbench skill routing |
| Area de Trabalho | Continuous Codex sessions |
| Chat IA | Codex runtime adapter boundary |
| Memoria | Snapshots, handoff, future project memory |
| Pool de Chaves | Vault boundary and redacted export |
| Terminal | MCP repo operator with policy enforcement |
| Analiticos | Prometheus, Grafana, Loki, audit endpoints |
| Equipe | RBAC, tenants, service tokens |

## Implemented in This Phase

- `GET /aios/heritage/summary`
- `POST /handoffs`
- `GET /sessions/{session_id}/handoffs`
- `GET /sessions/{session_id}/workbench`
- Workbench UI panels for files changed, build status, handoff, MCP/logs, snapshots, runtime adapter, and AIOS lineage.
- MCP repo tools for typecheck, git status, git diff, and local handoff artifacts.
- Session event pipeline for MCP tool calls, patches, changed files, builds, snapshots, skills and handoffs.
- Local Codex MCP config example and local skill docs.
