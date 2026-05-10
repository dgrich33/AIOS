# AIOS Codex Unlimited - Design Historico

## Scope

Build a new local enterprise prototype separate from DgLaucher. The project must turn the supplied AIOS Codex Unlimited text specification into a runnable Windows-oriented repository.

## Status vigente

Este design e historico. O estado atual do projeto segue o contrato assinado de 9 de maio de 2026:

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

## Architecture

- Backend: FastAPI, SQLAlchemy, JWT/RBAC, entitlement, sessions, snapshots, QoS, Vault boundary, audit, redaction, tenants, adapter boundary.
- Frontend: React/Vite/TypeScript Workbench with real API provider.
- MCP: two local TypeScript MCP-style servers using JSON-RPC stdio framing.
- Infra: Docker Compose with PostgreSQL, Redis, Vault, Prometheus, Grafana, Loki, Promtail, OTel, Alertmanager.
- Scripts: PowerShell runbook commands for Windows.

## Product invariant

The product is session-based. The UI and entitlement payload must not turn usage into tokens, balances, weekly quotas, or credit packages.

## First next phase

Implement Codex Workbench as the first practical next phase: session objective, create session, run adapter, snapshot, QoS job, skill execution, control-plane visibility, and abuse evaluation.
