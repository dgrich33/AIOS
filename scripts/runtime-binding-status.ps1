param(
  [string]$Base = "http://127.0.0.1:8000",
  [switch]$WriteReport
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$result = Invoke-RestMethod "$Base/runtime/binding/status" -Method Get -Headers $headers

Write-Host "AIOS Codex Unlimited RC16 - Runtime Binding Gate" -ForegroundColor Cyan
Write-Host "Binding state: $($result.bindingState)" -ForegroundColor Yellow
Write-Host "Provider: $($result.provider)" -ForegroundColor Yellow
Write-Host "Can invoke live runtime: $($result.canInvokeLiveRuntime)" -ForegroundColor Yellow
Write-Host "Credential reference: $($result.credential.reference)" -ForegroundColor Yellow
Write-Host "Secrets exposed: $($result.secretsExposed)" -ForegroundColor Yellow

if ($result.missingBinding.Count -gt 0) {
  Write-Host "Missing binding items:" -ForegroundColor DarkYellow
  $result.missingBinding | ForEach-Object { Write-Host " - $_" -ForegroundColor DarkYellow }
}

if ($WriteReport) {
  $ReleaseDir = Join-Path $Root "release"
  New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
  $ReportPath = Join-Path $ReleaseDir "RC16_RUNTIME_BINDING_REPORT.md"
  @(
    "# AIOS Codex Unlimited RC16 - Runtime Binding Report",
    "",
    "Data: $(Get-Date -Format o)",
    "",
    "| Campo | Valor |",
    "|---|---|",
    "| Phase | $($result.phase) |",
    "| Scope ready | $($result.scopeReady) |",
    "| Binding state | $($result.bindingState) |",
    "| Provider | $($result.provider) |",
    "| Credential reference | $($result.credential.reference) |",
    "| Credential configured | $($result.credential.configured) |",
    "| Sandbox environment configured | $($result.environment.sandboxEnvironmentConfigured) |",
    "| Secret store | $($result.environment.secretStore) |",
    "| Live flag enabled | $($result.environment.liveFlagEnabled) |",
    "| Can invoke live runtime | $($result.canInvokeLiveRuntime) |",
    "| Product unit | $($result.productUnit) |",
    "| User visible meter | $($result.userVisibleMeter) |",
    "| Secrets exposed | $($result.secretsExposed) |",
    "",
    "## Itens pendentes",
    "",
    (($result.missingBinding | ForEach-Object { "- $_" }) -join "`n")
  ) | Set-Content -LiteralPath $ReportPath -Encoding UTF8
  Write-Host "Relatorio criado: $ReportPath" -ForegroundColor Green
}

$result | ConvertTo-Json -Depth 12

if ($result.bindingState -eq "blocked_by_scope") {
  exit 1
}
