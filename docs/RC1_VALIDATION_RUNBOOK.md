# AIOS Codex Unlimited RC1 Validation Runbook

AIOS Codex Unlimited RC1 is prepared for a Windows local demonstration with two official modes:

- Mode A: Local Demo, guaranteed path for the meeting.
- Mode B: Docker Full Stack, available when Docker Desktop and Docker PATH are ready.

Product message:

```txt
Codex sem limites. Desenvolvimento sem interrupcoes.
```

Product unit:

```txt
Codex sessions
```

## Prerequisites

- Windows PowerShell 5.1 or PowerShell 7
- Python 3.11+
- Node.js 20+
- npm
- Git
- Docker Desktop for full stack mode only

## Preflight

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\rc1-preflight.ps1
```

Docker warnings do not block the local demo. If Docker is unavailable, use local mode.

## Mode A: Local Demo

```powershell
.\scripts\rc1-start-local.ps1
.\scripts\rc1-validate.ps1
```

URLs:

- Frontend: http://127.0.0.1:5173
- API docs: http://127.0.0.1:8000/docs

Logs:

- `logs/rc1-backend.log`
- `logs/rc1-frontend.log`

## Mode B: Docker Full Stack

```powershell
.\scripts\rc1-start-docker.ps1
.\scripts\rc1-validate.ps1
```

Full stack URLs:

- Frontend: http://127.0.0.1:5173
- API docs: http://127.0.0.1:8000/docs
- Grafana: http://127.0.0.1:3001
- Prometheus: http://127.0.0.1:9090
- Vault: http://127.0.0.1:8200
- Alertmanager: http://127.0.0.1:9093

## Emergency Commands

Stop project processes:

```powershell
.\scripts\stop.ps1
```

Restart local mode:

```powershell
.\scripts\rc1-start-local.ps1
```

Check ports:

```powershell
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

Package RC1:

```powershell
.\scripts\rc1-package.ps1
```

## Validation Coverage

`rc1-validate.ps1` verifies:

- `/health`
- `/ready`
- admin login
- `/entitlement/me`
- `/control-plane/status`
- session creation
- snapshot creation
- handoff creation
- session event creation
- files changed registration
- `/sessions/{id}/workbench`
- `/codex/adapter/info`
- `/export/redacted-bundle`
- enterprise check
- MCP builds

