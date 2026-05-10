param(
  [switch]$IncludeWorkingTree,
  [switch]$WriteReport,
  [switch]$AllowSensitiveContractDocs
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$ReleaseDir = Join-Path $Root "release"
$ReportPath = Join-Path $ReleaseDir "PUBLIC_REPO_SAFETY_AUDIT.md"

function Invoke-Git {
  param([string[]]$GitArgs)
  Push-Location $Root
  try {
    $output = & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
      throw "git $($GitArgs -join ' ') falhou com exit code $LASTEXITCODE"
    }
    return @($output)
  } finally {
    Pop-Location
  }
}

function Get-TrackedFiles {
  return Invoke-Git -GitArgs @("ls-tree", "-r", "--name-only", "HEAD")
}

function Get-TextContent {
  param([string]$RelativePath)
  $fullPath = Join-Path $Root $RelativePath
  try {
    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
    if ($bytes.Length -ge 2 -and $bytes[0] -eq 0x4D -and $bytes[1] -eq 0x5A) { return $null }
    if ($bytes.Length -ge 4 -and $bytes[0] -eq 0x50 -and $bytes[1] -eq 0x4B -and $bytes[2] -eq 0x03 -and $bytes[3] -eq 0x04) { return $null }

    $sampleLength = [Math]::Min($bytes.Length, 4096)
    if ($sampleLength -gt 0) {
      $nulls = 0
      for ($i = 0; $i -lt $sampleLength; $i++) {
        if ($bytes[$i] -eq 0) { $nulls++ }
      }
      if (($nulls / $sampleLength) -gt 0.01) { return $null }
    }

    return [System.IO.File]::ReadAllText($fullPath, [System.Text.Encoding]::UTF8)
  } catch {
    return $null
  }
}

function New-Finding {
  param(
    [string]$Severity,
    [string]$Category,
    [string]$Path,
    [string]$Evidence,
    [string]$Recommendation
  )
  return [PSCustomObject]@{
    severity = $Severity
    category = $Category
    path = $Path
    evidence = $Evidence
    recommendation = $Recommendation
  }
}

function Test-PlaceholderSecretValue {
  param([string]$Value)

  $clean = $Value.Trim().Trim("'", '"')
  if ([string]::IsNullOrWhiteSpace($clean)) { return $true }
  if ($clean.Length -lt 16) { return $true }
  if ($clean -match "(?i)placeholder|replace|change-me|demo|example|test|local|dev|vindo-do|vault|kms|env:|process\.env|os\.getenv|protect-secret|unprotect-secret|\$|<|>") { return $true }
  if ($clean -in @("AiosAdmin123!", "aios_password", "aios-grafana-admin")) { return $true }
  return $false
}

$forbiddenNames = @(
  ".env",
  ".env.local",
  "auth.json",
  "credentials.json",
  "runtime-binding.dpapi.json",
  "secure_runtime_binding.store",
  "service-token.txt",
  "openai_api_key.txt",
  "license.cert"
)
$forbiddenDirs = @(
  "node_modules",
  ".venv",
  "release",
  "logs",
  ".run",
  "dist",
  "test-results",
  "playwright-report",
  "restricted",
  "private-artifacts",
  "model-weights",
  "checkpoints"
)
$forbiddenExtensions = @(
  ".ckpt",
  ".safetensors",
  ".bin",
  ".onnx",
  ".pt",
  ".pth",
  ".zip",
  ".7z",
  ".rar",
  ".msi",
  ".exe"
)

$secretPatterns = @(
  @{ Name = "openai-key-like"; Pattern = "sk-[A-Za-z0-9_\-]{20,}" },
  @{ Name = "bearer-token-like"; Pattern = "Bearer\s+[A-Za-z0-9_\-\.]{20,}" },
  @{ Name = "jwt-like"; Pattern = "eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+" },
  @{ Name = "private-key-block"; Pattern = "-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----" }
)

$publicSensitivePatterns = @(
  @{ Name = "internal-domain"; Pattern = "(?i)openai\.internal|runtime\.openai\.internal" },
  @{ Name = "internal-team-contact"; Pattern = "(?i)platform-integrations@|iam-team@" },
  @{ Name = "specific-tenant-or-sandbox-placeholder"; Pattern = "(?i)tenant_aios_|sbx-aios" },
  @{ Name = "executive-signature-claim"; Pattern = "(?i)/s/\s*Sam Altman|Sam Altman" },
  @{ Name = "absolute-real-claim"; Pattern = "(?i)100%\s*REAL|SEM SIMULAÇÕES|SEM SIMULACOES" }
)

$files = Get-TrackedFiles
if ($IncludeWorkingTree) {
  $workingFiles = Get-ChildItem -LiteralPath $Root -Recurse -File -Force | Where-Object {
    $relative = $_.FullName.Substring($Root.Length + 1).Replace("\", "/")
    -not ($relative -like ".git/*")
  } | ForEach-Object { $_.FullName.Substring($Root.Length + 1).Replace("\", "/") }
  $files = @($files + $workingFiles | Sort-Object -Unique)
}

$findings = @()

foreach ($file in $files) {
  $normalized = $file.Replace("\", "/")
  $parts = $normalized -split "/"
  $name = $parts[-1]
  $extension = [System.IO.Path]::GetExtension($name).ToLowerInvariant()

  if ($forbiddenNames -contains $name) {
    $findings += New-Finding "critical" "restricted-file" $normalized $name "Remover do Git e manter apenas local/seguro."
    continue
  }

  foreach ($part in $parts) {
    if ($forbiddenDirs -contains $part) {
      $findings += New-Finding "critical" "restricted-path" $normalized $part "Remover do Git e manter fora de pacote publico."
      break
    }
  }

  if ($forbiddenExtensions -contains $extension) {
    $findings += New-Finding "critical" "restricted-extension" $normalized $extension "Remover artefato binario/restrito do Git."
    continue
  }

  $text = Get-TextContent -RelativePath $normalized
  if ($null -eq $text) { continue }

  foreach ($entry in $secretPatterns) {
    $matches = [regex]::Matches($text, $entry.Pattern)
    foreach ($match in $matches) {
      if ($normalized -eq "scripts/secure-link-intake.ps1" -and $entry.Name -eq "private-key-block") { continue }
      if ($match.Value -match "REDACTED_|test-key|placeholder|replace_with|change-me|demo") { continue }
      $findings += New-Finding "critical" "secret-pattern:$($entry.Name)" $normalized $match.Value.Substring(0, [Math]::Min(80, $match.Value.Length)) "Redigir valor e rotacionar se for segredo real."
    }
  }

  $assignmentMatches = [regex]::Matches($text, "(?im)^[ \t]*([A-Za-z0-9_\-]*(?:api[_\-]?key|service[_\-]?token|client[_\-]?secret|password|secret)[A-Za-z0-9_\-]*)[ \t]*[:=][ \t]*['""]?([^'""#\r\n]+)")
  foreach ($match in $assignmentMatches) {
    $keyName = $match.Groups[1].Value
    if ($keyName -match "(?i)(_configured|_ready|_present|_hash|hashed|hash)$") { continue }
    $value = $match.Groups[2].Value
    if (Test-PlaceholderSecretValue -Value $value) { continue }
    $evidence = "$keyName=[redacted candidate value]"
    $findings += New-Finding "critical" "secret-assignment" $normalized $evidence "Redigir valor e rotacionar se for segredo real."
  }

  foreach ($entry in $publicSensitivePatterns) {
    $matches = [regex]::Matches($text, $entry.Pattern)
    foreach ($match in $matches) {
      if ($AllowSensitiveContractDocs -and $normalized -like "docs/legal/*") { continue }
      $findings += New-Finding "high" "public-sensitive:$($entry.Name)" $normalized $match.Value.Substring(0, [Math]::Min(80, $match.Value.Length)) "Mover para pacote privado ou sanitizar antes de manter repo publico."
    }
  }
}

if ($WriteReport) {
  New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
  $lines = @(
    "# Public Repository Safety Audit",
    "",
    "Data: $(Get-Date -Format o)",
    "",
    "| Campo | Valor |",
    "|---|---|",
    "| Root | $Root |",
    "| Files scanned | $($files.Count) |",
    "| Findings | $($findings.Count) |",
    "| Allow sensitive contract docs | $AllowSensitiveContractDocs |",
    "",
    "## Findings",
    "",
    "| Severity | Category | Path | Evidence | Recommendation |",
    "|---|---|---|---|---|"
  )
  foreach ($finding in $findings) {
    $evidence = ($finding.evidence -replace "\|", "/")
    $recommendation = ($finding.recommendation -replace "\|", "/")
    $lines += "| $($finding.severity) | $($finding.category) | $($finding.path) | $evidence | $recommendation |"
  }
  if ($findings.Count -eq 0) {
    $lines += "| info | none | - | - | Nenhum achado. |"
  }
  $lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8
  Write-Host "Relatorio criado: $ReportPath" -ForegroundColor Green
}

if ($findings.Count -gt 0) {
  $findings | Format-Table -AutoSize
  throw "Public repo safety audit falhou: $($findings.Count) achado(s)."
}

Write-Host "Public repo safety audit OK: nenhum achado em arquivos rastreados." -ForegroundColor Green
