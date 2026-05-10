# Architecture

```mermaid
flowchart LR
  React["React/Vite Workbench"] --> API["FastAPI Backend"]
  API --> DB["PostgreSQL or SQLite local"]
  API --> Redis["Redis QoS Queue"]
  API --> Vault["Vault Dev Boundary"]
  Worker["QoS Worker"] --> Redis
  Worker --> DB
  MCPRepo["MCP Repo Server"] --> Workspace["AIOS Workspace"]
  MCPCore["MCP Core Server"] --> API
  API --> Prometheus["Prometheus Metrics"]
  Grafana["Grafana"] --> Prometheus
  Grafana --> Loki["Loki"]
```

## Contract

The frontend talks only to the backend API. Codex runtime integration stays behind `backend/app/codex_adapter.py`, so the local demo adapter can be replaced without rewriting product surfaces.

## Product invariant

Entitlement and UI must preserve `productUnit = codex_sessions`. Token counters, token balances, and weekly token quotas are intentionally absent from the product experience.
