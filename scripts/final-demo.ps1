$ErrorActionPreference = "Stop"
.\scripts\doctor.ps1
docker compose up -d --build
Start-Sleep -Seconds 25
.\scripts\enterprise-check.ps1
.\scripts\mcp-build-all.ps1
.\scripts\open-urls.ps1
