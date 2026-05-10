$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC2_VALIDATION_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -Path $Report -Value $Text
}

function Assert-True($Condition, $Message) {
  if (-not $Condition) {
    throw "Validacao RC2 falhou: $Message"
  }
  Write-Host "OK: $Message"
}

Set-Content -Path $Report -Value "# AIOS Codex Unlimited RC2 Validation Report`n"
Add-Line "- Data: $(Get-Date -Format s)"
Add-Line "- Base URL: $Base"
Add-Line ""

Write-Host "AIOS Codex Unlimited RC2 - Validate"

$health = Invoke-RestMethod "$Base/health"
Assert-True ($health.status -eq "ok") "/health"

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
Assert-True ($login.accessToken) "login admin"
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$manifest = Invoke-RestMethod "$Base/codex/product/manifest" -Headers $headers
Assert-True ($manifest.product -eq "AIOS Codex Unlimited") "product manifest"
Assert-True ($manifest.productUnit -eq "codex_sessions") "product unit codex_sessions"
Assert-True ($manifest.experience.showsTokenCounter -eq $false) "sem contador de token"

$models = Invoke-RestMethod "$Base/codex/models" -Headers $headers
$modelsList = @($models)
if (($models -isnot [array]) -and ($models.PSObject.Properties.Name -contains "value")) {
  $modelsList = @($models.value)
}
Assert-True (@($modelsList | Where-Object { $_.modelId -eq "codex-5.5-unlimited" }).Count -ge 1) "model registry"

$plan = Invoke-RestMethod "$Base/codex/plans/unlimited" -Headers $headers
Assert-True ($plan.planId -eq "aios_codex_unlimited") "plano unlimited"
Assert-True ($plan.hasWeeklyTokenQuota -eq $false) "sem quota semanal"

$subscription = Invoke-RestMethod "$Base/subscriptions/me" -Headers $headers
Assert-True ($subscription.status -eq "active") "subscription active"

$runtime = Invoke-RestMethod "$Base/codex/runtime/status" -Headers $headers
Assert-True ($runtime.adapter -eq "LocalQueueCodexAdapter") "runtime gateway status"
Assert-True ($runtime.officialAdapterReady -eq $true) "adapter oficial preparado por interface"

$allowed = Invoke-RestMethod "$Base/policy/language/evaluate" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  text = "AIOS Codex Unlimited com Codex sem limites e Sessoes Codex continuas."
} | ConvertTo-Json)
Assert-True ($allowed.approved -eq $true) "language policy texto oficial"

$blocked = Invoke-RestMethod "$Base/policy/language/evaluate" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  text = "Tentativa de bypass para contornar limite."
} | ConvertTo-Json)
Assert-True ($blocked.approved -eq $false) "language policy termo proibido"

$session = Invoke-RestMethod "$Base/sessions" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  title = "RC2 Runtime Gateway Session"
  objective = "Validar AIOS Codex Unlimited RC2 Product Core e Runtime Gateway."
} | ConvertTo-Json)
Assert-True ($session.id) "sessao RC2 criada"

$invoke = Invoke-RestMethod "$Base/codex/runtime/invoke" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  session_id = $session.id
  model_id = "codex-5.5-unlimited"
  objective = "Executar validacao RC2 pelo Runtime Gateway local."
} | ConvertTo-Json)
Assert-True ($invoke.accepted -eq $true) "runtime invoke accepted"
Assert-True ($invoke.jobId) "runtime invoke jobId"

$workbench = Invoke-RestMethod "$Base/sessions/$($session.id)/workbench" -Headers $headers
$recentEvents = @($workbench.recentEvents)
Assert-True ($recentEvents.Count -ge 1) "workbench recentEvents"
Assert-True (@($recentEvents | Where-Object { $_.type -eq "codex.runtime.invoked" }).Count -ge 1) "workbench runtime event"
Assert-True ($workbench.runtimeAdapter.name -eq "LocalQueueCodexAdapter") "workbench runtime adapter"

Add-Line "## Resultado"
Add-Line ""
Add-Line "- Health: OK"
Add-Line "- Login admin: OK"
Add-Line "- Product manifest: OK"
Add-Line "- Model registry: OK"
Add-Line "- Unlimited plan: OK"
Add-Line "- Subscription: $($subscription.status)"
Add-Line "- Runtime gateway: $($runtime.adapter)"
Add-Line "- Language policy allowed: OK"
Add-Line "- Language policy blocked: OK"
Add-Line "- Session: $($session.id)"
Add-Line "- Runtime invoke job: $($invoke.jobId)"
Add-Line "- Workbench runtime event: OK"
Add-Line ""
Add-Line "## URLs"
Add-Line ""
Add-Line "- Frontend: http://127.0.0.1:5173"
Add-Line "- API Docs: http://127.0.0.1:8000/docs"

Write-Host "RC2 validation OK"
Write-Host "Relatorio RC2 gerado em: $Report"
