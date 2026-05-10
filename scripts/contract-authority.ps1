param(
  [ValidateSet("verify", "show", "lock")]
  [string]$Mode = "verify",

  [switch]$IUnderstandThisChangesContractHashes
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LockPath = Join-Path $Root "docs\CONTRACT_AUTHORITY.lock.json"

$ProtectedFiles = @(
  "docs\legal\11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md",
  "docs\AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md"
)

function Get-ContractHash($RelativePath) {
  $fullPath = Join-Path $Root $RelativePath
  if (-not (Test-Path $fullPath)) {
    throw "Arquivo soberano nao encontrado: $RelativePath"
  }
  $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $fullPath
  [PSCustomObject]@{
    path = $RelativePath.Replace("\", "/")
    sha256 = $hash.Hash.ToLowerInvariant()
  }
}

function Get-CurrentContractState {
  [PSCustomObject]@{
    authority = "AIOS Codex Unlimited contract documents"
    rule = "Do not edit these files without explicit user authorization in the current conversation."
    generatedAt = (Get-Date).ToString("o")
    protectedFiles = @($ProtectedFiles | ForEach-Object { Get-ContractHash $_ })
  }
}

if ($Mode -eq "show") {
  Get-CurrentContractState | ConvertTo-Json -Depth 10
  exit 0
}

if ($Mode -eq "lock") {
  if (-not $IUnderstandThisChangesContractHashes) {
    throw "Para travar novos hashes, rode: .\scripts\contract-authority.ps1 lock -IUnderstandThisChangesContractHashes"
  }
  $state = Get-CurrentContractState
  $state | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $LockPath -Encoding UTF8
  Write-Host "Contrato travado em: $LockPath"
  exit 0
}

if (-not (Test-Path $LockPath)) {
  throw "Lock de contrato nao existe. Depois que o texto final for aprovado pelo usuario, rode: .\scripts\contract-authority.ps1 lock -IUnderstandThisChangesContractHashes"
}

$expected = Get-Content -LiteralPath $LockPath -Raw | ConvertFrom-Json
$current = Get-CurrentContractState
$failures = @()

foreach ($expectedFile in $expected.protectedFiles) {
  $currentFile = $current.protectedFiles | Where-Object { $_.path -eq $expectedFile.path } | Select-Object -First 1
  if (-not $currentFile) {
    $failures += "Arquivo ausente: $($expectedFile.path)"
    continue
  }
  if ($currentFile.sha256 -ne $expectedFile.sha256) {
    $failures += "Hash alterado: $($expectedFile.path)"
  }
}

if ($failures.Count -gt 0) {
  $failures | ForEach-Object { Write-Error $_ }
  throw "Os documentos soberanos do contrato foram alterados. Requer autorizacao explicita do usuario."
}

Write-Host "Contrato OK: documentos soberanos sem alteracao."
