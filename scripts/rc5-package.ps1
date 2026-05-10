$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$Zip = "C:\AIOS\aios-codex-unlimited-enterprise-v2-RC5.zip"
$StagingRoot = Join-Path $ReleaseDir "zip-staging-rc5"
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
    $parts -contains "dist" -or
    $parts -contains "__pycache__" -or
    $parts -contains ".pytest_cache" -or
    $parts -contains ".run" -or
    $parts -contains "logs" -or
    $parts -contains "zip-staging" -or
    $parts -contains "zip-staging-rc2" -or
    $parts -contains "zip-staging-rc3" -or
    $parts -contains "zip-staging-rc4" -or
    $parts -contains "zip-staging-rc5" -or
    $_.Name -in @(".env","aios_dev.db","aios_dev.db-wal","aios_dev.db-shm","test_aios.db","test_aios.db-wal","test_aios.db-shm")
  )
} | ForEach-Object {
  $relative = $_.FullName.Substring($Root.Length + 1)
  $dest = Join-Path $Staging $relative
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dest) | Out-Null
  Copy-Item -LiteralPath $_.FullName -Destination $dest -Force
}

if (Test-Path $Zip) { Remove-Item -LiteralPath $Zip -Force }
Compress-Archive -Path $Staging -DestinationPath $Zip -Force
Remove-Item -LiteralPath $StagingRoot -Recurse -Force

Get-Item $Zip | Format-List FullName,Length,LastWriteTime
