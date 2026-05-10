$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host
& "$PSScriptRoot\contract-docs-audit.ps1" | Out-Host
& "$PSScriptRoot\runtime-binding-status.ps1" -WriteReport | Out-Host

$Zip = "C:\AIOS\aios-codex-unlimited-enterprise-v2-RC18-APPROVAL-PACK.zip"
$StagingRoot = Join-Path $ReleaseDir "zip-staging-rc18"
$Staging = Join-Path $StagingRoot "aios-codex-unlimited-enterprise-v2"

if (Test-Path $StagingRoot) {
  $resolved = (Resolve-Path $StagingRoot).Path
  if (-not $resolved.StartsWith($ReleaseDir)) { throw "Staging inseguro: $resolved" }
  Remove-Item -LiteralPath $resolved -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $Staging | Out-Null

Get-ChildItem -LiteralPath $Root -Recurse -File -Force | Where-Object {
  $relative = $_.FullName.Substring($Root.Length + 1)
  $parts = $relative -split '[\\/]'
  -not (
    $parts -contains "node_modules" -or
    $parts -contains ".venv" -or
    $parts -contains ".aios-secure" -or
    $parts -contains "dist" -or
    $parts -contains "__pycache__" -or
    $parts -contains ".pytest_cache" -or
    $parts -contains ".run" -or
    $parts -contains "logs" -or
    $parts -contains "test-results" -or
    $parts -contains "playwright-report" -or
    $parts -contains "release" -or
    $parts -contains "restricted" -or
    $parts -contains "private-artifacts" -or
    $parts -contains "model-weights" -or
    $parts -contains "checkpoints" -or
    $parts -like "zip-staging*" -or
    $_.Name -in @(".env",".env.local","auth.json","credentials.json","runtime-binding.dpapi.json","aios_dev.db","aios_dev.db-wal","aios_dev.db-shm","test_aios.db","test_aios.db-wal","test_aios.db-shm") -or
    $_.Extension.ToLowerInvariant() -in @(".ckpt",".safetensors",".bin",".onnx",".pt",".pth")
  )
} | ForEach-Object {
  $relative = $_.FullName.Substring($Root.Length + 1)
  $dest = Join-Path $Staging $relative
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
}

& "$PSScriptRoot\restricted-package-scan.ps1" -Path $Staging | Out-Host

if (Test-Path $Zip) { Remove-Item -LiteralPath $Zip -Force }
Compress-Archive -Path $Staging -DestinationPath $Zip -Force
Remove-Item -LiteralPath $StagingRoot -Recurse -Force

$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $Zip
$report = Join-Path $ReleaseDir "RC18_APPROVAL_PACK_REPORT.md"
@(
  "# AIOS Codex Unlimited RC18 - Approval Pack Report",
  "",
  "Data: $(Get-Date -Format o)",
  "",
  "| Campo | Valor |",
  "|---|---|",
  "| Pacote | $Zip |",
  "| SHA256 | $($hash.Hash) |",
  "| Contrato | verificado |",
  "| Docs audit | OK |",
  "| Package scan | OK |",
  "| Secrets exposed | false |"
) | Set-Content -LiteralPath $report -Encoding UTF8

Get-Item $Zip | Format-List FullName,Length,LastWriteTime
$hash | Format-List
Write-Host "Relatorio criado: $report" -ForegroundColor Green
