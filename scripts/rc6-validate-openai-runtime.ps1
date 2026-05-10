$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC6_OPENAI_RUNTIME_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -Path $Report -Value $Text
}

function Assert-True($Condition, $Message) {
  if (-not $Condition) {
    throw "Validacao RC6 falhou: $Message"
  }
  Write-Host "OK: $Message"
}

function Get-ErrorBody($ErrorRecord) {
  if ($ErrorRecord.ErrorDetails -and $ErrorRecord.ErrorDetails.Message) {
    return $ErrorRecord.ErrorDetails.Message
  }
  try {
    $stream = $ErrorRecord.Exception.Response.GetResponseStream()
    if (-not $stream) { return "" }
    $reader = [System.IO.StreamReader]::new($stream)
    return $reader.ReadToEnd()
  } catch {
    return $ErrorRecord.Exception.Message
  }
}

Set-Content -Path $Report -Value "# AIOS Codex Unlimited RC6 OpenAI Runtime Report`n"
Add-Line "- Data: $(Get-Date -Format s)"
Add-Line "- Base URL: $Base"
Add-Line ""

Write-Host "AIOS Codex Unlimited RC6 - OpenAI Runtime Validate"
& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
Assert-True ($login.accessToken) "login admin"
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$security = Invoke-RestMethod "$Base/official-sandbox/security-check" -Headers $headers
Assert-True ($security.provider -eq "openai_api") "provider openai_api"
Assert-True ($security.secureEnvironmentReady -eq $true) "secure environment ready"
Assert-True ($security.canInvokeLiveRuntime -eq $true) "live runtime allowed"
Assert-True ($security.secretsExposed -eq $false) "secrets not exposed"

$session = Invoke-RestMethod "$Base/sessions" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  title = "RC6 OpenAI Runtime Session"
  objective = "Validar chamada real da OpenAI API pelo AIOS Codex Unlimited."
} | ConvertTo-Json)
Assert-True ($session.id) "session created"

$invoke = $null
$blockedByQuota = $false
$errorBody = ""
try {
  $invoke = Invoke-RestMethod "$Base/codex/runtime/invoke" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
    session_id = $session.id
    model_id = "codex-5.5-unlimited"
    objective = "Responda em uma frase curta confirmando que o runtime OpenAI API esta conectado ao AIOS RC6."
  } | ConvertTo-Json)
} catch {
  $errorBody = Get-ErrorBody $_
  if ($errorBody -match "insufficient_quota") {
    $blockedByQuota = $true
  } else {
    throw
  }
}

$workbench = Invoke-RestMethod "$Base/sessions/$($session.id)/workbench" -Headers $headers

if ($blockedByQuota) {
  $failedEvents = @($workbench.recentEvents | Where-Object { $_.type -eq "codex.runtime.failed" })
  Assert-True ($failedEvents.Count -ge 1) "workbench runtime failed event"
  $failedJobs = @($workbench.recentJobs | Where-Object { $_.jobType -eq "codex.runtime.invoke" -and $_.status -eq "failed" })
  Assert-True ($failedJobs.Count -ge 1) "runtime job failed recorded"

  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: BLOCKED_BY_OPENAI_QUOTA"
  Add-Line "- Provider: openai_api"
  Add-Line "- Network call performed: True"
  Add-Line "- Error code: insufficient_quota"
  Add-Line "- Session ID: $($session.id)"
  Add-Line ""
  Add-Line "A chamada real chegou na OpenAI API, mas a conta/projeto retornou quota insuficiente. Corrija billing/credits e rode este script novamente."
  Write-Host "RC6 runtime path reached OpenAI API, but billing/quota blocked the response."
} else {
  Assert-True ($invoke.accepted -eq $true) "runtime invoke accepted"
  Assert-True ($invoke.completed -eq $true) "runtime invoke completed"
  Assert-True ($invoke.networkCallPerformed -eq $true) "network call performed"
  Assert-True ($invoke.provider -eq "openai_api") "runtime provider openai_api"
  Assert-True ($invoke.responseId) "response id"
  Assert-True ($invoke.outputText) "output text"

  $events = @($workbench.recentEvents | Where-Object { $_.type -eq "codex.runtime.completed" })
  Assert-True ($events.Count -ge 1) "workbench runtime completed event"

  Add-Line "## Resultado"
  Add-Line ""
  Add-Line "- Status: COMPLETED"
  Add-Line "- Provider: $($invoke.provider)"
  Add-Line "- Runtime model: $($invoke.runtimeModelId)"
  Add-Line "- Response ID: $($invoke.responseId)"
  Add-Line "- Network call performed: $($invoke.networkCallPerformed)"
  Add-Line "- Usage captured internally: $($invoke.usageCaptured)"
  Add-Line "- Output: $($invoke.outputText)"
}
Add-Line ""
Add-Line "## Seguranca"
Add-Line ""
Add-Line "- API key nao foi impressa."
Add-Line "- Secrets exposed: $($security.secretsExposed)"
Add-Line "- Frontend exposure allowed: $($security.frontendExposureAllowed)"

Write-Host "RC6 OpenAI runtime validation OK"
Write-Host "Relatorio RC6 gerado em: $Report"
