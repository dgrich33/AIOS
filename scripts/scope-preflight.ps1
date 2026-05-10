param(
  [string]$Base = "http://127.0.0.1:8000",
  [string]$Operation = "codex.runtime.invoke",
  [string]$Environment = "sandbox",
  [string]$ModelId = "codex-5.5-unlimited",
  [switch]$RequiresLiveRuntime,
  [switch]$RequiresRestrictedArtifacts,
  [switch]$WriteReport
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

& "$PSScriptRoot\scope-authority.ps1" | Out-Host

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$payload = @{
  operation = $Operation
  environment = $Environment
  modelId = $ModelId
  requiresLiveRuntime = [bool]$RequiresLiveRuntime
  requiresRestrictedArtifacts = [bool]$RequiresRestrictedArtifacts
  reason = "RC15 scoped preflight"
}

$result = Invoke-RestMethod "$Base/scope/preflight" -Method Post -Headers $headers -ContentType "application/json" -Body ($payload | ConvertTo-Json)

if ($WriteReport) {
  $ReleaseDir = Join-Path $Root "release"
  New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
  $ReportPath = Join-Path $ReleaseDir "RC15_SCOPE_PREFLIGHT_REPORT.md"
  @(
    "# AIOS Codex Unlimited RC15 - Scope Preflight Report",
    "",
    "Data: $(Get-Date -Format o)",
    "",
    "| Campo | Valor |",
    "|---|---|",
    "| Phase | $($result.phase) |",
    "| Scope ready | $($result.scopeReady) |",
    "| Decision | $($result.scopeDecision) |",
    "| Execution state | $($result.executionState) |",
    "| Operation | $($result.requested.operation) |",
    "| Environment | $($result.requested.environment) |",
    "| Model | $($result.requested.modelId) |",
    "| Runtime binding | $($result.runtimeBinding) |",
    "| User visible meter | $($result.userVisibleMeter) |",
    "| Secrets exposed | $($result.secretsExposed) |"
  ) | Set-Content -LiteralPath $ReportPath -Encoding UTF8
  Write-Host "Relatorio criado: $ReportPath" -ForegroundColor Green
}

$result | ConvertTo-Json -Depth 12

if ($result.scopeDecision -eq "block") {
  exit 1
}

