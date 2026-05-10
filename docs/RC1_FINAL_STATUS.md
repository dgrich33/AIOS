# AIOS Codex Unlimited RC1 Final Status

Status:

```txt
Release Candidate 1
Ready for local Windows demonstration
```

## Working

- FastAPI backend
- React/Vite frontend
- Login and JWT auth
- Entitlement based on Codex sessions
- Control Plane status
- Codex Workbench
- Session creation
- Snapshot creation
- Handoff creation
- Session events
- Files changed tracking
- Workbench aggregation
- MCP repo build
- MCP core build
- Service token authentication
- Redacted export
- Local fallback mode
- Docker compose configuration

## Official Product Boundary

The product experience is based on:

```txt
Codex sessions
```

It does not present token counters, balances, credit packs, or weekly token quotas as the product unit.

## URLs

- Frontend: http://127.0.0.1:5173
- Backend: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Grafana, Docker only: http://127.0.0.1:3001
- Prometheus, Docker only: http://127.0.0.1:9090
- Vault, Docker only: http://127.0.0.1:8200

## Credentials

```txt
admin@aios.local
AiosAdmin123!
```

## RC1 Commands

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\rc1-preflight.ps1
.\scripts\rc1-start-local.ps1
.\scripts\rc1-validate.ps1
.\scripts\rc1-package.ps1
```

## Zip

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2-RC1.zip
```

## Next Step

If RC1 is approved, the next implementation step is:

```txt
Replace LocalQueueCodexAdapter with an approved official Codex runtime adapter.
```

