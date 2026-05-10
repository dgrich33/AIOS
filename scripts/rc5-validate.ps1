$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Report = Join-Path $ReleaseDir "RC5_VALIDATION_REPORT.md"
$Base = "http://127.0.0.1:8000"

function Add-Line($Text = "") {
  Add-Content -Path $Report -Value $Text
}

function Assert-True($Condition, $Message) {
  if (-not $Condition) {
    throw "Validacao RC5 falhou: $Message"
  }
  Write-Host "OK: $Message"
}

function Invoke-ExpectFailure($ScriptBlock, [int]$ExpectedStatus, [string]$Message) {
  try {
    & $ScriptBlock | Out-Null
    throw "Esperava falha HTTP $ExpectedStatus"
  } catch {
    $status = $null
    if ($_.Exception.Response) {
      $status = [int]$_.Exception.Response.StatusCode
    }
    if ($status -ne $ExpectedStatus) {
      throw "Falha inesperada em $Message. Status recebido: $status. Erro: $($_.Exception.Message)"
    }
    Write-Host "OK: $Message"
  }
}

Set-Content -Path $Report -Value "# AIOS Codex Unlimited RC5 Validation Report`n"
Add-Line "- Data: $(Get-Date -Format s)"
Add-Line "- Base URL: $Base"
Add-Line ""

Write-Host "AIOS Codex Unlimited RC5 - Validate"
& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$health = Invoke-RestMethod "$Base/health"
Assert-True ($health.status -eq "ok") "/health"

$login = Invoke-RestMethod "$Base/auth/login" -Method Post -ContentType "application/json" -Body (@{
  email = "admin@aios.local"
  password = "AiosAdmin123!"
} | ConvertTo-Json)
Assert-True ($login.accessToken) "login admin"
$headers = @{ Authorization = "Bearer $($login.accessToken)" }

$security = Invoke-RestMethod "$Base/official-sandbox/security-check" -Headers $headers
Assert-True ($security.phase -eq "RC5_OFFICIAL_SANDBOX_ACTIVATION") "sandbox phase"
Assert-True ($security.secretsExposed -eq $false) "secrets not exposed"
Assert-True ($security.frontendExposureAllowed -eq $false) "no frontend secret exposure"
Assert-True ($security.logsExposureAllowed -eq $false) "no log secret exposure"

$activation = Invoke-RestMethod "$Base/official-sandbox/activation" -Headers $headers
Assert-True ($activation.networkCallPerformed -eq $false) "activation status performs no network call"

if ($security.secureEnvironmentReady -eq $true) {
  Assert-True ($security.canInvokeLiveRuntime -eq $true) "secure environment ready"
  $activated = Invoke-RestMethod "$Base/official-sandbox/activate" -Method Post -Headers $headers
  Assert-True ($activated.activated -eq $true) "official sandbox activated"
} else {
  Assert-True ($security.canInvokeLiveRuntime -eq $false) "live runtime blocked without secure environment"
  Assert-True ($security.missing.Count -gt 0) "missing secure environment gates reported"
  Invoke-ExpectFailure {
    Invoke-RestMethod "$Base/official-sandbox/activate" -Method Post -Headers $headers
  } 412 "activation blocked until secure environment"
}

$profile = Invoke-RestMethod "$Base/official-sandbox/data-profiles" -Method Post -Headers $headers -ContentType "application/json" -Body (@{
  profileId = "rc5-real-data-approved"
  name = "RC5 Real Data Approved"
  dataClassification = "real_sandbox_approved"
  approvalReference = "meeting-2026-05-09"
  redactionRequired = $true
  publicExportAllowed = $false
  retentionDays = 30
} | ConvertTo-Json)
Assert-True ($profile.realDataApproved -eq $true) "real sandbox data profile approved"
Assert-True ($profile.redactionRequired -eq $true) "redaction required"
Assert-True ($profile.publicExportAllowed -eq $false) "public export blocked"

$profiles = Invoke-RestMethod "$Base/official-sandbox/data-profiles" -Headers $headers
$matchingProfiles = @($profiles | Where-Object { $_.profileId -eq "rc5-real-data-approved" })
Assert-True ($matchingProfiles.Count -ge 1) "data profile listed"

Add-Line "## Resultado"
Add-Line ""
Add-Line "- Contract authority: OK"
Add-Line "- Health: OK"
Add-Line "- Login admin: OK"
Add-Line "- Official Sandbox Security Check: $($security.state)"
Add-Line "- Secure Environment Ready: $($security.secureEnvironmentReady)"
Add-Line "- Live Runtime Allowed: $($security.canInvokeLiveRuntime)"
Add-Line "- Missing Gates: $($security.missing -join ', ')"
Add-Line "- Activation Network Call Performed: $($activation.networkCallPerformed)"
Add-Line "- Data Profile: $($profile.profileId)"
Add-Line "- Redaction Required: $($profile.redactionRequired)"
Add-Line "- Public Export Allowed: $($profile.publicExportAllowed)"
Add-Line ""
Add-Line "## Observacao"
Add-Line ""
Add-Line "A RC5 nao simula sucesso de runtime oficial. Se o ambiente seguro nao estiver completo, a ativacao permanece bloqueada por HTTP 412."

Write-Host "RC5 validation OK"
Write-Host "Relatorio RC5 gerado em: $Report"
