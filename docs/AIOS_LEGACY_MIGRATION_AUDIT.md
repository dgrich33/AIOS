# AIOS Legacy Migration Audit

Source project reviewed: `C:\Users\dg71\Documents\AIOS-15-Fase3-Corrigido`

## Original State

The original AIOS project is a frontend-only React/Vite application. It includes:

- login and tutorial flow
- CEO panel
- dashboard
- AI account/key pool
- terminal page
- analytics
- workspace sessions
- AI chat
- memories
- Arena.IA router
- team view

The original data model includes provider accounts, Gmail records, API keys, projects, memories, AI sessions, messages, snapshots, tasks, terminal commands, and usage logs.

## Migration Position

The original UI concepts were not copied wholesale into this repository. They were mapped into a backend-backed enterprise system:

- account/key concepts moved behind Vault/redaction boundaries
- sessions became Codex sessions with entitlement and QoS
- local snapshots became persisted snapshots and handoff records
- Arena.IA became the seed for future skill routing
- terminal behavior became MCP repo operations under policy
- analytics became Prometheus/Grafana/Loki plus audit endpoints

## Remaining Follow-up

- Add durable project memory tables.
- Add first-class changed-file tracking from real MCP patch events.
- Bind MCP tool-call records to session ids.
- Expand tenant isolation to every query.
- Replace local Codex adapter with an official runtime adapter when available.

