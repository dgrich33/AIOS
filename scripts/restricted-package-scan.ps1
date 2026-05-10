param(
  [string]$Path = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path $Path).Path
$ForbiddenNames = @(
  ".env",
  "auth.json",
  "credentials.json",
  "service-token.txt",
  "openai_api_key.txt"
)
$ForbiddenPathParts = @(
  "node_modules",
  ".venv",
  ".run",
  "logs",
  "test-results",
  "playwright-report",
  "restricted",
  "private-artifacts",
  "model-weights",
  "checkpoints"
)
$ForbiddenExtensions = @(
  ".ckpt",
  ".safetensors",
  ".bin",
  ".onnx",
  ".pt",
  ".pth"
)

$Findings = @()
Get-ChildItem -LiteralPath $Root -Recurse -File -Force | ForEach-Object {
  $relative = $_.FullName.Substring($Root.Length + 1)
  $parts = $relative -split '[\\/]'
  $extension = $_.Extension.ToLowerInvariant()
  if ($ForbiddenNames -contains $_.Name) {
    $Findings += [PSCustomObject]@{ Path = $relative; Reason = "forbidden-name" }
  } elseif ($parts | Where-Object { $ForbiddenPathParts -contains $_ }) {
    $Findings += [PSCustomObject]@{ Path = $relative; Reason = "forbidden-path" }
  } elseif ($ForbiddenExtensions -contains $extension) {
    $Findings += [PSCustomObject]@{ Path = $relative; Reason = "restricted-artifact-extension" }
  }
}

if ($Findings.Count -gt 0) {
  $Findings | Format-Table -AutoSize
  throw "Scan de pacote publico falhou: artefatos restritos ou arquivos locais foram encontrados."
}

Write-Host "Scan de pacote publico OK: nenhum artefato restrito encontrado em $Root" -ForegroundColor Green
