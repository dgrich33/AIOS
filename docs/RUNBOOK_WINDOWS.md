# Windows Runbook

## Requirements

- Python 3.11+
- Node.js 20+ or 22+; Node 24 also works for this scaffold
- Git
- Docker Desktop for the full stack
- PowerShell 5.1+ or PowerShell 7

## Local checks

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\doctor.ps1
.\scripts\test-backend.ps1
cd .\frontend
npm install
npm run build
```

## Full stack

```powershell
docker compose up -d --build
.\scripts\enterprise-check.ps1
```
