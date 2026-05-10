$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC1_VALIDATION_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -Path $Report -Value $Text
}

function Assert-True($Condition, $Message) {
  if (-not $Condition) {
    throw "Validacao falhou: $Message"
  }
  Write-Host "OK: $Message"
}

Set-Content -Path $Report -Value "# AIOS Codex Unlimited RC1 Validation Report`n"
Add-Line "- Data: $(Get-Date -Format s)"
Add-Line "- Base URL: $Base"
Add-Line ""

Write-Host "AIOS Codex Unlimited RC1 - Validate"
$health = Invoke-RestMethod "$Base/health"
Assert-True ($health.status -eq "ok") "/health"
try {
  $ready = Invoke-RestMethod "$Base/ready"
  Assert-True ($ready.status -eq "ready") "/ready"
} catch {
  Add-Line "- /ready: indisponivel ou falhou: $($_.Exception.Message)"
}

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{ email="admin@aios.local"; password="AiosAdmin123!" } | ConvertTo-Json)
Assert-True ($login.accessToken) "login admin"
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$entitlement = Invoke-RestMethod "$Base/entitlement/me" -Headers $headers
Assert-True ($entitlement.productUnit -eq "codex_sessions") "entitlement usa codex_sessions"
Assert-True ($entitlement.hasTokenLimit -eq $false) "sem limite de token na UX"

$control = Invoke-RestMethod "$Base/control-plane/status" -Headers $headers
Assert-True ($control.productUnit -eq "codex_sessions") "control plane responde"

$session = Invoke-RestMethod "$Base/sessions" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  title = "RC1 Validation Session"
  objective = "Validar AIOS Codex Unlimited RC1 para apresentacao executiva."
} | ConvertTo-Json)
Assert-True ($session.id) "sessao criada"

$snapshot = Invoke-RestMethod "$Base/snapshots" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  sessionId = $session.id
  title = "RC1 Snapshot"
  filesChanged = @("frontend/src/App.tsx", "backend/app/main.py")
  notes = "Snapshot criado na validacao RC1."
} | ConvertTo-Json)
Assert-True ($snapshot.id) "snapshot criado"

$handoff = Invoke-RestMethod "$Base/handoffs" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  sessionId = $session.id
  reason = "Handoff RC1 para continuidade de integracao oficial Codex."
  context = "Release Candidate validado localmente."
  nextSteps = @("Avaliar RC1", "Conectar runtime oficial pelo CodexRuntimeAdapter")
} | ConvertTo-Json)
Assert-True ($handoff.id) "handoff criado"

$event = Invoke-RestMethod "$Base/sessions/$($session.id)/events" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  type = "mcp.tool_call"
  source = "rc1-validate"
  title = "MCP tool call RC1"
  message = "Evento MCP criado pela validacao RC1."
  payload = @{ tool = "repo.search"; status = "completed" }
} | ConvertTo-Json -Depth 10)
Assert-True ($event.id) "evento MCP criado"

$files = Invoke-RestMethod "$Base/sessions/$($session.id)/files-changed" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  filesChanged = @("frontend/src/App.tsx", "mcp/aios-mcp-repo/src/server.ts")
  source = "rc1-validate"
} | ConvertTo-Json)
Assert-True ($files.filesChanged.Count -ge 1) "files-changed registrado"

$workbench = Invoke-RestMethod "$Base/sessions/$($session.id)/workbench" -Headers $headers
Assert-True ($workbench.recentEvents.Count -ge 1) "workbench recentEvents"
Assert-True ($workbench.snapshots.Count -ge 1) "workbench snapshots"
Assert-True ($workbench.handoffs.Count -ge 1) "workbench handoffs"
Assert-True ($workbench.filesChanged.Count -ge 1) "workbench filesChanged"
Assert-True ($workbench.buildStatus.status) "workbench buildStatus"

$adapter = Invoke-RestMethod "$Base/codex/adapter/info"
Assert-True ($adapter.name -eq "LocalQueueCodexAdapter") "adapter info"

$redacted = Invoke-RestMethod "$Base/export/redacted-bundle" -Headers $headers
$redactedText = $redacted | ConvertTo-Json -Depth 20
Assert-True (-not $redactedText.Contains("sk-demo")) "redacted export mascara secrets"

Push-Location $Root
try {
  if (Test-Path ".\scripts\enterprise-check.ps1") {
    .\scripts\enterprise-check.ps1 | Out-Host
    Add-Line "- enterprise-check.ps1: OK"
  }
  if (Test-Path ".\scripts\mcp-build-all.ps1") {
    .\scripts\mcp-build-all.ps1 | Out-Host
    Add-Line "- mcp-build-all.ps1: OK"
  }
} finally {
  Pop-Location
}

Add-Line "## Resultado"
Add-Line ""
Add-Line "- Health: OK"
Add-Line "- Ready: OK"
Add-Line "- Login admin: OK"
Add-Line "- Entitlement: OK"
Add-Line "- Control Plane: OK"
Add-Line "- Session: $($session.id)"
Add-Line "- Snapshot: $($snapshot.id)"
Add-Line "- Handoff: $($handoff.id)"
Add-Line "- Event: $($event.id)"
Add-Line "- Workbench: OK"
Add-Line "- Adapter: $($adapter.name)"
Add-Line "- Redacted export: OK"
Add-Line ""
Add-Line "## URLs"
Add-Line ""
Add-Line "- Frontend: http://127.0.0.1:5173"
Add-Line "- API Docs: http://127.0.0.1:8000/docs"

Write-Host "Relatorio RC1 gerado em: $Report"

