param(
  [switch]$Quick,
  [switch]$UpdateBaseline,
  [string]$Base = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$AuditDir = Join-Path $ReleaseDir "validation-audit-$Stamp"
$BaselinePath = Join-Path $ReleaseDir "file-audit-baseline.csv"
$ManifestPath = Join-Path $AuditDir "file-manifest.csv"
$ReportPath = Join-Path $AuditDir "RC19_VALIDATION_AND_AUDIT_REPORT.md"

New-Item -ItemType Directory -Force -Path $AuditDir | Out-Null

$script:Results = @()

function Add-Result {
  param(
    [string]$Name,
    [string]$Status,
    [string]$Log,
    [string]$Notes = ""
  )

  $script:Results += [PSCustomObject]@{
    Name = $Name
    Status = $Status
    Log = $Log
    Notes = $Notes
  }
}

function Invoke-AuditStep {
  param(
    [string]$Name,
    [scriptblock]$Block,
    [switch]$Optional
  )

  $safeName = ($Name -replace "[^A-Za-z0-9_.-]", "_")
  $logPath = Join-Path $AuditDir "$safeName.log"
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  try {
    & $Block *> $logPath
    $sw.Stop()
    Add-Result -Name $Name -Status "PASS" -Log $logPath -Notes "durationMs=$($sw.ElapsedMilliseconds)"
    Write-Host "PASS $Name" -ForegroundColor Green
  } catch {
    $sw.Stop()
    $message = $_.Exception.Message
    Add-Content -LiteralPath $logPath -Value ""
    Add-Content -LiteralPath $logPath -Value "ERROR: $message"
    if ($Optional) {
      Add-Result -Name $Name -Status "SKIPPED_OR_FAILED_OPTIONAL" -Log $logPath -Notes $message
      Write-Host "OPTIONAL $Name - $message" -ForegroundColor DarkYellow
    } else {
      Add-Result -Name $Name -Status "FAIL" -Log $logPath -Notes $message
      Write-Host "FAIL $Name - $message" -ForegroundColor Red
    }
  }
}

function Test-BackendReady {
  try {
    Invoke-RestMethod "$Base/health" -Method Get -TimeoutSec 3 | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Get-RelativePath {
  param([string]$Path)
  return $Path.Substring($Root.Length + 1).Replace("\", "/")
}

function Test-IncludedFile {
  param([System.IO.FileInfo]$File)

  $relative = Get-RelativePath -Path $File.FullName
  $parts = $relative -split "/"
  $excludedDirs = @(
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".run",
    "logs",
    "test-results",
    "playwright-report",
    "release",
    ".aios-secure"
  )
  $excludedNames = @(
    ".env",
    ".env.local",
    "auth.json",
    "credentials.json",
    "runtime-binding.dpapi.json",
    "aios_dev.db",
    "aios_dev.db-wal",
    "aios_dev.db-shm",
    "test_aios.db",
    "test_aios.db-wal",
    "test_aios.db-shm"
  )
  $excludedExtensions = @(
    ".ckpt",
    ".safetensors",
    ".bin",
    ".onnx",
    ".pt",
    ".pth"
  )

  foreach ($part in $parts) {
    if ($excludedDirs -contains $part) { return $false }
  }
  if ($excludedNames -contains $File.Name) { return $false }
  if ($excludedExtensions -contains $File.Extension.ToLowerInvariant()) { return $false }
  return $true
}

function Write-FileManifest {
  $rows = Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
    Where-Object { Test-IncludedFile -File $_ } |
    ForEach-Object {
      $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName
      [PSCustomObject]@{
        Path = Get-RelativePath -Path $_.FullName
        Length = $_.Length
        LastWriteTimeUtc = $_.LastWriteTimeUtc.ToString("o")
        SHA256 = $hash.Hash
      }
    } |
    Sort-Object Path

  $rows | Export-Csv -LiteralPath $ManifestPath -NoTypeInformation -Encoding UTF8
  return @($rows)
}

function Write-FileAudit {
  $gitLog = Join-Path $AuditDir "git-audit.log"
  $gitAvailable = $false
  try {
    Push-Location $Root
    try {
      $inside = git rev-parse --is-inside-work-tree 2>$null
      $gitAvailable = ($inside -eq "true")
    } finally {
      Pop-Location
    }
  } catch {
    $gitAvailable = $false
  }

  if ($gitAvailable) {
    Push-Location $Root
    try {
      "## git status --short" | Set-Content -LiteralPath $gitLog -Encoding UTF8
      git status --short | Add-Content -LiteralPath $gitLog
      "" | Add-Content -LiteralPath $gitLog
      "## git diff --stat" | Add-Content -LiteralPath $gitLog
      git diff --stat | Add-Content -LiteralPath $gitLog
      "" | Add-Content -LiteralPath $gitLog
      "## git diff --name-only" | Add-Content -LiteralPath $gitLog
      git diff --name-only | Add-Content -LiteralPath $gitLog
    } finally {
      Pop-Location
    }
    Add-Result -Name "Git audit" -Status "PASS" -Log $gitLog -Notes "git diff/status captured"
    return
  }

  $manifest = Write-FileManifest
  $compareLog = Join-Path $AuditDir "file-manifest-compare.log"

  if (Test-Path -LiteralPath $BaselinePath) {
    $baseline = Import-Csv -LiteralPath $BaselinePath
    $baseByPath = @{}
    foreach ($row in $baseline) { $baseByPath[$row.Path] = $row }
    $currentByPath = @{}
    foreach ($row in $manifest) { $currentByPath[$row.Path] = $row }

    $added = @($manifest | Where-Object { -not $baseByPath.ContainsKey($_.Path) })
    $removed = @($baseline | Where-Object { -not $currentByPath.ContainsKey($_.Path) })
    $changed = @($manifest | Where-Object { $baseByPath.ContainsKey($_.Path) -and $baseByPath[$_.Path].SHA256 -ne $_.SHA256 })

    @(
      "Git repository: not found",
      "Audit mode: file manifest SHA256 compare",
      "Baseline: $BaselinePath",
      "Current: $ManifestPath",
      "",
      "Added: $($added.Count)",
      ($added | ForEach-Object { " + $($_.Path)" }),
      "",
      "Changed: $($changed.Count)",
      ($changed | ForEach-Object { " * $($_.Path)" }),
      "",
      "Removed: $($removed.Count)",
      ($removed | ForEach-Object { " - $($_.Path)" })
    ) | Set-Content -LiteralPath $compareLog -Encoding UTF8
    Add-Result -Name "File manifest audit" -Status "PASS" -Log $compareLog -Notes "added=$($added.Count);changed=$($changed.Count);removed=$($removed.Count)"
  } else {
    @(
      "Git repository: not found",
      "Audit mode: file manifest SHA256 snapshot",
      "Current: $ManifestPath",
      "Baseline: not found",
      "Files: $($manifest.Count)",
      "",
      "Run again with -UpdateBaseline to make this manifest the comparison baseline."
    ) | Set-Content -LiteralPath $compareLog -Encoding UTF8
    Add-Result -Name "File manifest audit" -Status "PASS" -Log $compareLog -Notes "baseline not found; files=$($manifest.Count)"
  }

  if ($UpdateBaseline) {
    Copy-Item -LiteralPath $ManifestPath -Destination $BaselinePath -Force
    Add-Result -Name "File manifest baseline update" -Status "PASS" -Log $ManifestPath -Notes "baseline=$BaselinePath"
  }
}

Write-Host "AIOS RC19 validation + audit" -ForegroundColor Cyan
Write-Host "Root: $Root" -ForegroundColor Cyan
Write-Host "Audit dir: $AuditDir" -ForegroundColor Cyan

Write-FileAudit

Invoke-AuditStep -Name "contract-authority verify" -Block {
  & "$PSScriptRoot\contract-authority.ps1" verify
}

Invoke-AuditStep -Name "contract-docs-audit" -Block {
  & "$PSScriptRoot\contract-docs-audit.ps1"
}

Invoke-AuditStep -Name "backend pytest" -Block {
  Push-Location (Join-Path $Root "backend")
  try { & "..\.venv\Scripts\python.exe" -m pytest .\tests -q } finally { Pop-Location }
}

Invoke-AuditStep -Name "frontend build" -Block {
  Push-Location (Join-Path $Root "frontend")
  try { npm run build } finally { Pop-Location }
}

Invoke-AuditStep -Name "mcp core build" -Block {
  Push-Location (Join-Path $Root "mcp\aios-mcp-core")
  try { npm run build } finally { Pop-Location }
}

Invoke-AuditStep -Name "mcp repo build" -Block {
  Push-Location (Join-Path $Root "mcp\aios-mcp-repo")
  try { npm run build } finally { Pop-Location }
}

if (-not $Quick) {
  Invoke-AuditStep -Name "frontend playwright" -Block {
    Push-Location (Join-Path $Root "frontend")
    try { npm run test:e2e } finally { Pop-Location }
  }
}

if (Test-BackendReady) {
  Invoke-AuditStep -Name "enterprise-check" -Block {
    & "$PSScriptRoot\enterprise-check.ps1"
  }

  Invoke-AuditStep -Name "runtime-binding-status" -Block {
    & "$PSScriptRoot\runtime-binding-status.ps1" -Base $Base -WriteReport
  }
} else {
  $skipLog = Join-Path $AuditDir "http-checks-skipped.log"
  "Backend not reachable at $Base. Start with scripts/start.ps1 -Mode Local before HTTP validation." |
    Set-Content -LiteralPath $skipLog -Encoding UTF8
  Add-Result -Name "enterprise-check" -Status "SKIPPED" -Log $skipLog -Notes "backend not reachable"
  Add-Result -Name "runtime-binding-status" -Status "SKIPPED" -Log $skipLog -Notes "backend not reachable"
  Write-Host "SKIPPED HTTP validations - backend not reachable at $Base" -ForegroundColor DarkYellow
}

$failed = @($script:Results | Where-Object { $_.Status -eq "FAIL" })
$lines = @(
  "# AIOS Codex Unlimited RC19 - Validation and Audit Report",
  "",
  "Data: $(Get-Date -Format o)",
  "",
  "| Campo | Valor |",
  "|---|---|",
  "| Root | $Root |",
  "| Audit dir | $AuditDir |",
  "| Quick mode | $Quick |",
  "| Backend base | $Base |",
  "| Failed critical steps | $($failed.Count) |",
  "",
  "## Resultados",
  "",
  "| Step | Status | Notes | Log |",
  "|---|---|---|---|"
)

foreach ($result in $script:Results) {
  $logRelative = $result.Log.Substring($Root.Length + 1).Replace("\", "/")
  $notes = ($result.Notes -replace "\|", "/")
  $lines += "| $($result.Name) | $($result.Status) | $notes | $logRelative |"
}

$lines += @(
  "",
  "## Criterio de uso",
  "",
  "Este relatorio combina validacao por scripts com auditoria de alteracoes. Quando Git existir, o relatorio captura status e diff. Quando Git nao existir, o relatorio usa manifesto SHA256 dos arquivos relevantes.",
  "",
  "Para congelar uma linha de base sem Git:",
  "",
  '```powershell',
  ".\scripts\rc19-validate-and-audit.ps1 -UpdateBaseline",
  '```'
)

$lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8

Write-Host "Report: $ReportPath" -ForegroundColor Green

if ($failed.Count -gt 0) {
  exit 1
}
