param(
  [string]$MissionId = "mission-smoke-rc35",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path $PSScriptRoot -Parent
$tmp = Join-Path $repoRoot ".run\rc35-evidence-smoke"
$ledger = Join-Path $tmp "ledger.jsonl"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

$patch = Join-Path $tmp "patch.diff"
$log = Join-Path $tmp "runtime.log"
$coverage = Join-Path $tmp "coverage.txt"
$screenshot = Join-Path $tmp "reality-panel.txt"

Set-Content -Path $patch -Value "diff --git a/demo b/demo`n+RC35 evidence smoke" -Encoding UTF8
Set-Content -Path $log -Value "RC35 smoke log redacted" -Encoding UTF8
Set-Content -Path $coverage -Value "coverage: smoke" -Encoding UTF8
Set-Content -Path $screenshot -Value "Reality Panel: codex_plan_bridge" -Encoding UTF8

if ($DryRun) {
  $env:VAULT_BUCKET = "file://local"
  $env:AIOS_LOCAL_VAULT_DIR = (Join-Path $tmp "local-vault")
} elseif ($env:VAULT_BUCKET -ne "s3://aios-vault") {
  throw "VAULT_BUCKET must be s3://aios-vault for real Evidence Vault smoke. Use -DryRun for local validation."
}

python .\aios-codex-fabric\evidence\evidence_vault.py $MissionId $patch $log $coverage $screenshot --ledger $ledger

Write-Host ""
Write-Host "Ledger: $ledger"
if ($DryRun) {
  Write-Host "Dry run used local file vault; no S3 upload was attempted." -ForegroundColor Yellow
}
