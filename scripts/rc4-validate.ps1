$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC4_VALIDATION_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -Path $Report -Value $Text
}

function Assert-True($Condition, $Message) {
  if (-not $Condition) {
    throw "Validacao RC4 falhou: $Message"
  }
  Write-Host "OK: $Message"
}

Set-Content -Path $Report -Value "# AIOS Codex Unlimited RC4 Validation Report`n"
Add-Line "- Data: $(Get-Date -Format s)"
Add-Line "- Base URL: $Base"
Add-Line ""

Write-Host "AIOS Codex Unlimited RC4 - Validate"

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$health = Invoke-RestMethod "$Base/health"
Assert-True ($health.status -eq "ok") "/health"

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
Assert-True ($login.accessToken) "login admin"
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$readiness = Invoke-RestMethod "$Base/official-integration/readiness" -Headers $headers
Assert-True ($readiness.phase -eq "RC4_OFFICIAL_INTEGRATION_READINESS") "readiness phase"
Assert-True ($readiness.contractAuthority.locked -eq $true) "contract lock"
Assert-True ($readiness.adapter.targetClass -eq "OfficialCodexRuntimeAdapter") "official adapter target"
Assert-True ($readiness.runtime.sandboxApproved -eq $true) "sandbox approved"
Assert-True ($readiness.runtime.stagingApproved -eq $true) "staging approved"
Assert-True ($readiness.credentials.secretsExposed -eq $false) "secrets not exposed"

$contract = Invoke-RestMethod "$Base/official-integration/adapter/contract" -Headers $headers
Assert-True ($contract.requestSchema) "adapter request schema"
Assert-True ($contract.streamEventSchema) "adapter stream schema"
Assert-True ($contract.toolCallSchema) "adapter tool schema"

$credentialStatus = Invoke-RestMethod "$Base/official-integration/credentials/status" -Headers $headers
Assert-True ($credentialStatus.storageRequirement -eq "Vault/KMS") "credential storage"
Assert-True ($credentialStatus.frontendExposureAllowed -eq $false) "no frontend credentials"

$request = Invoke-RestMethod "$Base/restricted-access/requests" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  operation = "runtime_patch"
  environment = "sandbox_approved_machine"
  justification = "Validar patch de compatibilidade aprovado para OfficialCodexRuntimeAdapter."
  artifactName = "codex-runtime-sandbox"
  artifactHash = "sha256:approved-artifact-hash-required"
  pathScope = "C:\AIOS\aios-codex-unlimited-enterprise-v2"
  expiresInDays = 30
} | ConvertTo-Json)
Assert-True ($request.status -eq "requested") "restricted access requested"

$decision = Invoke-RestMethod "$Base/restricted-access/requests/$($request.id)/decision" -Method Patch -Headers $headers -ContentType "application/json" -Body (@{
  decision = "approved"
  approver = "OpenAI/Codex designated approver"
  notes = "Approved by meeting decision and tracked for RC4."
} | ConvertTo-Json)
Assert-True ($decision.status -eq "approved") "restricted access approved"
Assert-True ($decision.activeApproval -eq $true) "restricted access active"

$accessLog = Invoke-RestMethod "$Base/restricted-access/requests/$($request.id)/access-log" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  action = "runtime_patch_dry_run"
  artifactPath = "C:\AIOS\aios-codex-unlimited-enterprise-v2\restricted\codex-runtime-sandbox.bin"
  artifactHash = "sha256:approved-artifact-hash-required"
  justification = "Registrar dry run de patch conforme contrato."
  result = "recorded"
} | ConvertTo-Json)
Assert-True ($accessLog.details.machineScopeApproved -eq $true) "restricted access log path scope"

$dryRun = Invoke-RestMethod "$Base/official-integration/adapter/dry-run" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  modelId = "codex-5.5-unlimited"
  objective = "Validate official adapter contract without external network call."
} | ConvertTo-Json)
Assert-True ($dryRun.accepted -eq $true) "official dry run accepted"
Assert-True ($dryRun.networkCallPerformed -eq $false) "dry run no network"

Add-Line "## Resultado"
Add-Line ""
Add-Line "- Contract authority: OK"
Add-Line "- Health: OK"
Add-Line "- Login admin: OK"
Add-Line "- Official Integration Readiness: OK"
Add-Line "- Adapter Contract: OK"
Add-Line "- Credentials Status: OK"
Add-Line "- Restricted Access Request: $($request.id)"
Add-Line "- Restricted Access Decision: approved"
Add-Line "- Adapter Dry Run: OK"
Add-Line ""
Add-Line "## URLs"
Add-Line ""
Add-Line "- Frontend: http://127.0.0.1:5173"
Add-Line "- API Docs: http://127.0.0.1:8000/docs"

Write-Host "RC4 validation OK"
Write-Host "Relatorio RC4 gerado em: $Report"
