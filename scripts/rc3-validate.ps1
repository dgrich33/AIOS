$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC3_VALIDATION_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -Path $Report -Value $Text
}

function Assert-True($Condition, $Message) {
  if (-not $Condition) {
    throw "Validacao RC3 falhou: $Message"
  }
  Write-Host "OK: $Message"
}

Set-Content -Path $Report -Value "# AIOS Codex Unlimited RC3 Validation Report`n"
Add-Line "- Data: $(Get-Date -Format s)"
Add-Line "- Base URL: $Base"
Add-Line ""

Write-Host "AIOS Codex Unlimited RC3 - Validate"

$health = Invoke-RestMethod "$Base/health"
Assert-True ($health.status -eq "ok") "/health"

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
Assert-True ($login.accessToken) "login admin"
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$guardrails = Invoke-RestMethod "$Base/policy/integration/guardrails" -Headers $headers
Assert-True ($guardrails.conditionalOperations -contains "runtime_patch") "guardrail permite patch apenas com controles contratuais"
Assert-True ($guardrails.conditionalOperations -contains "copy_model_checkpoints") "guardrail trata checkpoints como operacao condicional"
Assert-True ($guardrails.blockedOperations -contains "alter_codex_auth_json") "guardrail bloqueia auth bypass"
Assert-True ($guardrails.restrictedAccessControls.requiresApprovedRequest -eq $true) "operacao restrita exige request aprovado"
Assert-True ($guardrails.privateArtifactPolicy.userReleaseIncludesPrivateArtifacts -eq $false) "release sem artefatos privados"

$profiles = Invoke-RestMethod "$Base/identity/profiles" -Headers $headers
Assert-True (@($profiles).Count -ge 1) "identity profiles"
Assert-True (@($profiles)[0].runtimeAccessMode -eq "official_adapter_only") "identity usa adapter oficial"

$bridge = Invoke-RestMethod "$Base/codex/secure-runtime/bridge" -Headers $headers
Assert-True ($bridge.storesPrivateArtifacts -eq $false) "bridge nao armazena artefatos privados"
Assert-True ($bridge.allowedOperations -contains "official_runtime_invoke") "bridge permite runtime oficial"

$session = Invoke-RestMethod "$Base/sessions" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  title = "RC3 Secure Runtime Session"
  objective = "Validar Secure Runtime Bridge, Context Engine, Skill Store e Windows Release."
} | ConvertTo-Json)
Assert-True ($session.id) "sessao RC3 criada"

$accepted = Invoke-RestMethod "$Base/codex/secure-runtime/request" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  sessionId = $session.id
  operation = "official_runtime_invoke"
  objective = "Solicitacao segura via adapter oficial."
  payload = @{ modelId = "codex-5.5-unlimited" }
} | ConvertTo-Json -Depth 10)
Assert-True ($accepted.accepted -eq $true) "secure runtime request accepted"

$blockedOk = $false
try {
  Invoke-RestMethod "$Base/codex/secure-runtime/request" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
    sessionId = $session.id
    operation = "copy_model_checkpoints"
    objective = "Deve ser bloqueado."
    payload = @{}
  } | ConvertTo-Json -Depth 10) | Out-Null
} catch {
  if ($_.Exception.Response.StatusCode.value__ -eq 403) {
    $blockedOk = $true
  }
}
Assert-True ($blockedOk) "secure runtime bloqueia operacao proibida"

$index = Invoke-RestMethod "$Base/context/index" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  sessionId = $session.id
  name = "RC3 context capsule"
  source = "workspace"
  fileCount = 120
  graphNodes = 450
  graphEdges = 900
} | ConvertTo-Json)
Assert-True ($index.status -eq "indexed") "context index"

$query = Invoke-RestMethod "$Base/context/query" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  sessionId = $session.id
  query = "secure runtime bridge policy"
} | ConvertTo-Json)
Assert-True ($query.localOnly -eq $true) "context query local-only"

$skills = Invoke-RestMethod "$Base/skill-store" -Headers $headers
$skillsList = @($skills)
if (($skills -isnot [array]) -and ($skills.PSObject.Properties.Name -contains "value")) {
  $skillsList = @($skills.value)
}
Assert-True (@($skillsList | Where-Object { $_.skillId -eq "context.prewarm" }).Count -ge 1) "skill store"

$release = Invoke-RestMethod "$Base/release/windows/manifest" -Headers $headers
Assert-True ($release.platform -eq "windows") "windows release manifest"
Assert-True ($release.includesPrivateCodexArtifacts -eq $false) "windows release sem artefatos privados"

Add-Line "## Resultado"
Add-Line ""
Add-Line "- Health: OK"
Add-Line "- Login admin: OK"
Add-Line "- Guardrails: OK"
Add-Line "- Identity profiles: OK"
Add-Line "- Secure Runtime Bridge: OK"
Add-Line "- Secure request accepted: $($accepted.jobId)"
Add-Line "- Blocked operation: OK"
Add-Line "- Context index: $($index.id)"
Add-Line "- Context query local-only: OK"
Add-Line "- Skill Store: OK"
Add-Line "- Windows release manifest: OK"
Add-Line ""
Add-Line "## URLs"
Add-Line ""
Add-Line "- Frontend: http://127.0.0.1:5173"
Add-Line "- API Docs: http://127.0.0.1:8000/docs"

Write-Host "RC3 validation OK"
Write-Host "Relatorio RC3 gerado em: $Report"
