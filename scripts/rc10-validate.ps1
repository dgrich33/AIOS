$ErrorActionPreference = "Stop"

$Base = $env:AIOS_API_URL
if (-not $Base) { $Base = "http://127.0.0.1:8000" }

function Assert-True($Condition, $Message) {
  if (-not $Condition) { throw "RC10 falhou: $Message" }
  Write-Host "OK: $Message"
}

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host
& "$PSScriptRoot\contract-docs-audit.ps1" | Out-Host

$health = Invoke-RestMethod "$Base/health"
Assert-True ($health.status -eq "ok") "health"

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$guardrails = Invoke-RestMethod "$Base/policy/integration/guardrails" -Headers $headers
Assert-True ($guardrails.conditionalOperations -contains "runtime_patch") "runtime_patch condicional"
Assert-True ($guardrails.conditionalOperations -contains "copy_model_checkpoints") "checkpoints condicional"
Assert-True ($guardrails.blockedOperations -contains "alter_codex_auth_json") "auth bypass bloqueado"
Assert-True ($guardrails.restrictedAccessControls.requiresApprovedRequest -eq $true) "requires approved request"

$request = Invoke-RestMethod "$Base/restricted-access/requests" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  operation = "runtime_patch"
  environment = "sandbox_approved_machine"
  justification = "Validar fluxo contratual RC10"
  artifactName = "codex-runtime-sandbox"
  artifactHash = "sha256:approved-artifact-hash-required"
  pathScope = "C:\AIOS\aios-codex-unlimited-enterprise-v2"
  expiresInDays = 30
} | ConvertTo-Json)

$decision = Invoke-RestMethod "$Base/restricted-access/requests/$($request.id)/decision" -Method Patch -Headers $headers -ContentType "application/json" -Body (@{
  decision = "approved"
  approver = "OpenAI/Codex designated approver"
  notes = "RC10 contract-governed approval"
} | ConvertTo-Json)
Assert-True ($decision.activeApproval -eq $true) "active approval"

$log = Invoke-RestMethod "$Base/restricted-access/requests/$($request.id)/access-log" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  action = "runtime_patch_dry_run"
  artifactPath = "C:\AIOS\aios-codex-unlimited-enterprise-v2\restricted\codex-runtime-sandbox.bin"
  artifactHash = "sha256:approved-artifact-hash-required"
  justification = "Registrar acesso conforme contrato"
  result = "recorded"
} | ConvertTo-Json)
Assert-True ($log.details.machineScopeApproved -eq $true) "access log path scope"

$session = Invoke-RestMethod "$Base/sessions" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  title = "RC10 Contract Guardrail Session"
  objective = "Validar operacao condicional com request aprovado"
} | ConvertTo-Json)

$secure = Invoke-RestMethod "$Base/codex/secure-runtime/request" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  sessionId = $session.id
  operation = "runtime_patch"
  objective = "Executar via bridge seguro com request aprovado"
  payload = @{ restrictedAccessRequestId = $request.id }
} | ConvertTo-Json -Depth 10)
Assert-True ($secure.accepted -eq $true) "secure bridge accepted conditional operation"

Write-Host "RC10 validation OK" -ForegroundColor Green

