param(
  [string]$Base = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Results = @()

function Add-Result {
  param(
    [string]$Name,
    [string]$Status,
    [string]$Notes = ""
  )
  $script:Results += [pscustomobject]@{
    Name = $Name
    Status = $Status
    Notes = $Notes
  }
}

function Invoke-Step {
  param(
    [string]$Name,
    [scriptblock]$Block,
    [switch]$Optional
  )
  Write-Host "==> $Name" -ForegroundColor Cyan
  try {
    $global:LASTEXITCODE = 0
    & $Block
    if ($global:LASTEXITCODE -ne 0) {
      throw "Native command failed with exit code $global:LASTEXITCODE"
    }
    Add-Result -Name $Name -Status "PASS"
    Write-Host "PASS $Name" -ForegroundColor Green
  } catch {
    $message = $_.Exception.Message
    if ($Optional) {
      Add-Result -Name $Name -Status "SKIPPED_OR_FAILED_OPTIONAL" -Notes $message
      Write-Host "OPTIONAL $Name - $message" -ForegroundColor DarkYellow
    } else {
      Add-Result -Name $Name -Status "FAIL" -Notes $message
      Write-Host "FAIL $Name - $message" -ForegroundColor Red
      throw
    }
  }
}

function Invoke-AiosJson {
  param(
    [string]$Uri,
    [string]$Method = "GET",
    [hashtable]$Headers = @{},
    [object]$Body = $null
  )
  $params = @{ Uri = $Uri; Method = $Method; Headers = $Headers; TimeoutSec = 60 }
  if ($null -ne $Body) {
    $params.ContentType = "application/json"
    $params.Body = ($Body | ConvertTo-Json -Depth 20)
  }
  Invoke-RestMethod @params
}

function Test-ApiReady {
  try {
    Invoke-RestMethod "$Base/health" -Method Get -TimeoutSec 3 | Out-Null
    return $true
  } catch {
    return $false
  }
}

Push-Location $Root
try {
  Invoke-Step "Backend tests" {
    Push-Location (Join-Path $Root "backend")
    try {
      ..\.venv\Scripts\python.exe -m pytest .\tests\test_api.py -q
    } finally {
      Pop-Location
    }
  }

  Invoke-Step "Frontend build" {
    Push-Location (Join-Path $Root "frontend")
    try {
      npm run build
    } finally {
      Pop-Location
    }
  }

  Invoke-Step "Playwright" {
    Push-Location (Join-Path $Root "frontend")
    try {
      npx playwright test
    } finally {
      Pop-Location
    }
  }

  Invoke-Step "MCP core build" {
    Push-Location (Join-Path $Root "mcp\aios-mcp-core")
    try {
      npm run build
    } finally {
      Pop-Location
    }
  }

  Invoke-Step "MCP repo build" {
    Push-Location (Join-Path $Root "mcp\aios-mcp-repo")
    try {
      npm run build
    } finally {
      Pop-Location
    }
  }

  Invoke-Step "Secret hygiene" {
    & "$PSScriptRoot\secret-hygiene-check.ps1" -WriteReport
  }

  Invoke-Step "Runtime binding status" {
    if (-not (Test-ApiReady)) {
      throw "AIOS API is not running at $Base. Start it with .\scripts\start.ps1 -Mode Local and rerun this step."
    }
    $login = Invoke-AiosJson -Uri "$Base/auth/login" -Method Post -Body @{
      email = "admin@aios.local"
      password = "AiosAdmin123!"
    }
    $headers = @{ Authorization = "Bearer $($login.accessToken)" }
    $status = Invoke-AiosJson -Uri "$Base/runtime/official-binding/status" -Headers $headers
    $status | ConvertTo-Json -Depth 20
    if ($status.secretsExposed) {
      throw "RC26 status reported secretsExposed=true"
    }
  } -Optional

  Invoke-Step "Optional live smoke test" {
    if ($env:AIOS_RUN_LIVE_SMOKE -ne "true") {
      Write-Host "AIOS_RUN_LIVE_SMOKE is not true; skipping live smoke test." -ForegroundColor DarkYellow
      return
    }
    if (-not $env:AIOS_LIVE_SMOKE_APPROVAL_ID) {
      throw "Set AIOS_LIVE_SMOKE_APPROVAL_ID to an approved Approval Gate request id."
    }
    if (-not (Test-ApiReady)) {
      throw "AIOS API is not running at $Base"
    }
    $provider = $env:AIOS_LIVE_SMOKE_PROVIDER
    if (-not $provider) { $provider = "codex_cli_local_developer" }
    $login = Invoke-AiosJson -Uri "$Base/auth/login" -Method Post -Body @{
      email = "admin@aios.local"
      password = "AiosAdmin123!"
    }
    $headers = @{ Authorization = "Bearer $($login.accessToken)" }
    Invoke-AiosJson -Uri "$Base/runtime/official-binding/validate" -Method Post -Headers $headers -Body @{ providerId = $provider } | Out-Null
    $smoke = Invoke-AiosJson -Uri "$Base/runtime/live/smoke-test" -Method Post -Headers $headers -Body @{
      providerId = $provider
      prompt = "Reply with AIOS_RC26_OK."
      approvalRequestId = $env:AIOS_LIVE_SMOKE_APPROVAL_ID
      timeoutSeconds = 120
    }
    $smoke | ConvertTo-Json -Depth 20
    if ($smoke.secretsExposed) {
      throw "RC26 smoke test reported secretsExposed=true"
    }
  } -Optional

  Write-Host ""
  Write-Host "RC26 validation summary" -ForegroundColor Cyan
  $Results | Format-Table -AutoSize
} finally {
  Pop-Location
}
