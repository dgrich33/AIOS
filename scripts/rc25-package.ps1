$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
$Zip = "C:\AIOS\aios-codex-unlimited-enterprise-v2-RC25-FINAL.zip"
$StagingRoot = Join-Path $ReleaseDir "zip-staging-rc25"
$Staging = Join-Path $StagingRoot "aios-codex-unlimited-enterprise-v2"
$Report = Join-Path $ReleaseDir "RC25_FINAL_READINESS_REPORT.md"

New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host
& "$PSScriptRoot\contract-docs-audit.ps1" | Out-Host
& "$PSScriptRoot\public-repo-safety-audit.ps1" | Out-Host
& "$PSScriptRoot\secret-hygiene-check.ps1" -WriteReport | Out-Host
& "$PSScriptRoot\runtime-binding-status.ps1" -WriteReport | Out-Host

if (Test-Path $StagingRoot) {
  $resolved = (Resolve-Path $StagingRoot).Path
  if (-not $resolved.StartsWith($ReleaseDir)) { throw "Staging inseguro: $resolved" }
  Remove-Item -LiteralPath $resolved -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $Staging | Out-Null

$forbiddenNames = @(
  ".env",
  ".env.local",
  "auth.json",
  "credentials.json",
  "runtime-binding.dpapi.json",
  "secure_runtime_binding.store",
  "service-token.txt",
  "openai_api_key.txt",
  "license.cert",
  "aios_dev.db",
  "aios_dev.db-wal",
  "aios_dev.db-shm",
  "test_aios.db",
  "test_aios.db-wal",
  "test_aios.db-shm"
)

$forbiddenParts = @(
  ".git",
  ".venv",
  ".aios-secure",
  ".pytest_cache",
  ".run",
  "node_modules",
  "dist",
  "build",
  "out",
  "logs",
  "release",
  "test-results",
  "playwright-report",
  "restricted",
  "private-artifacts",
  "model-weights",
  "checkpoints"
)

$forbiddenExtensions = @(".ckpt", ".safetensors", ".bin", ".onnx", ".pt", ".pth", ".pem", ".key", ".pfx", ".p12", ".cert", ".crt", ".zip", ".7z", ".rar", ".msi", ".exe")

Get-ChildItem -LiteralPath $Root -Recurse -File -Force | Where-Object {
  $relative = $_.FullName.Substring($Root.Length + 1)
  $parts = $relative -split '[\\/]'
  $extension = $_.Extension.ToLowerInvariant()
  -not (
    ($parts | Where-Object { $forbiddenParts -contains $_ }) -or
    ($forbiddenNames -contains $_.Name) -or
    ($forbiddenExtensions -contains $extension)
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
@(
  "# AIOS Codex Unlimited RC25 - Final Readiness Package",
  "",
  "Data: $(Get-Date -Format o)",
  "",
  "| Campo | Valor |",
  "|---|---|",
  "| Pacote | $Zip |",
  "| SHA256 | $($hash.Hash) |",
  "| Contrato | verificado |",
  "| Docs audit | OK |",
  "| Public repo safety audit | OK |",
  "| Secret hygiene | OK |",
  "| Runtime binding report | gerado |",
  "| Restricted package scan | OK |",
  "| Includes private Codex artifacts | false |",
  "| Production live runtime | depende de binding oficial ativo |"
) | Set-Content -LiteralPath $Report -Encoding UTF8

Get-Item $Zip | Format-List FullName,Length,LastWriteTime
$hash | Format-List
Write-Host "Relatorio criado: $Report" -ForegroundColor Green
