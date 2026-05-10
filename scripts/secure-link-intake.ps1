param(
  [Parameter(Mandatory=$true)]
  [string]$Url,

  [int]$MaxBytes = 2097152,

  [int]$TimeoutSec = 45,

  [string]$OutDir = "$env:LOCALAPPDATA\AIOS\CodexUnlimited\secure-link-intake"
)

$ErrorActionPreference = "Stop"

function Convert-GoogleDriveUrl {
  param([string]$InputUrl)

  if ($InputUrl -match "https://drive\.google\.com/file/d/([^/]+)/") {
    return "https://drive.google.com/uc?export=download&id=$($Matches[1])"
  }

  if ($InputUrl -match "https://drive\.google\.com/open\?id=([^&]+)") {
    return "https://drive.google.com/uc?export=download&id=$($Matches[1])"
  }

  return $InputUrl
}

function Redact-SensitiveText {
  param([string]$Text)

  $redacted = $Text
  $patterns = @(
    @{ Pattern = "sk-[A-Za-z0-9_\-]{20,}"; Replacement = "[REDACTED_OPENAI_KEY]" },
    @{ Pattern = "sess-[A-Za-z0-9_\-]{20,}"; Replacement = "[REDACTED_SESSION_TOKEN]" },
    @{ Pattern = "Bearer\s+[A-Za-z0-9_\-\.]{20,}"; Replacement = "Bearer [REDACTED_BEARER_TOKEN]" },
    @{ Pattern = "eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"; Replacement = "[REDACTED_JWT]" },
    @{ Pattern = "-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"; Replacement = "[REDACTED_PRIVATE_KEY]" },
    @{ Pattern = "(?i)(api[_-]?key|service[_-]?token|client[_-]?secret|password|secret)\s*[:=]\s*['""]?[^'""\r\n]{8,}"; Replacement = '$1=[REDACTED_SECRET_VALUE]' }
  )

  foreach ($entry in $patterns) {
    $redacted = [regex]::Replace($redacted, $entry.Pattern, $entry.Replacement)
  }

  return $redacted
}

function Test-ProbablyText {
  param([byte[]]$Bytes)

  if ($Bytes.Length -eq 0) { return $true }
  $sampleLength = [Math]::Min($Bytes.Length, 4096)
  $nulls = 0
  $control = 0

  for ($i = 0; $i -lt $sampleLength; $i++) {
    $b = $Bytes[$i]
    if ($b -eq 0) { $nulls++ }
    if (($b -lt 9) -or (($b -gt 13) -and ($b -lt 32))) { $control++ }
  }

  if ($Bytes.Length -ge 2 -and $Bytes[0] -eq 0x4D -and $Bytes[1] -eq 0x5A) { return $false }
  if ($Bytes.Length -ge 4 -and $Bytes[0] -eq 0x50 -and $Bytes[1] -eq 0x4B -and $Bytes[2] -eq 0x03 -and $Bytes[3] -eq 0x04) { return $false }

  return (($nulls / $sampleLength) -lt 0.01 -and ($control / $sampleLength) -lt 0.05)
}

$uri = [Uri]$Url
if ($uri.Scheme -ne "https") {
  throw "Por seguranca, envie um link HTTPS. Esquema recebido: $($uri.Scheme)"
}

$downloadUrl = Convert-GoogleDriveUrl -InputUrl $Url
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$sessionDir = Join-Path $OutDir $timestamp
New-Item -ItemType Directory -Force -Path $sessionDir | Out-Null

$rawPath = Join-Path $sessionDir "source.txt"
$safePath = Join-Path $sessionDir "source.redacted.txt"
$reportPath = Join-Path $sessionDir "intake-report.json"

Add-Type -AssemblyName System.Net.Http
$client = [System.Net.Http.HttpClient]::new()
$client.Timeout = [TimeSpan]::FromSeconds($TimeoutSec)
$client.DefaultRequestHeaders.UserAgent.ParseAdd("AIOS-Secure-Link-Intake/1.0")

$response = $client.GetAsync($downloadUrl, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
try {
  if (-not $response.IsSuccessStatusCode) {
    throw "Falha no download seguro. HTTP $([int]$response.StatusCode) $($response.ReasonPhrase)"
  }

  $contentLength = $response.Content.Headers.ContentLength
  if ($contentLength -and $contentLength -gt $MaxBytes) {
    throw "Arquivo maior que o limite seguro ($contentLength bytes > $MaxBytes bytes)."
  }

  $stream = $response.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
  $output = [System.IO.File]::Open($rawPath, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
  try {
    $buffer = New-Object byte[] 8192
    $total = 0
    while (($read = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
      $total += $read
      if ($total -gt $MaxBytes) {
        throw "Download interrompido: arquivo excedeu $MaxBytes bytes."
      }
      $output.Write($buffer, 0, $read)
    }
  } finally {
    $output.Dispose()
    $stream.Dispose()
  }

  $bytes = [System.IO.File]::ReadAllBytes($rawPath)
  if (-not (Test-ProbablyText -Bytes $bytes)) {
    throw "O conteudo baixado nao parece TXT/Markdown seguro. Arquivo preservado para inspecao manual, mas nao sera lido automaticamente: $rawPath"
  }

  $reader = [System.IO.StreamReader]::new($rawPath, [System.Text.Encoding]::UTF8, $true)
  try {
    $text = $reader.ReadToEnd()
  } finally {
    $reader.Dispose()
  }

  $redacted = Redact-SensitiveText -Text $text
  [System.IO.File]::WriteAllText($safePath, $redacted, [System.Text.Encoding]::UTF8)

  $hash = Get-FileHash -Algorithm SHA256 -LiteralPath $rawPath
  $report = [ordered]@{
    capturedAt = (Get-Date).ToUniversalTime().ToString("o")
    originalUrl = $Url
    downloadUrl = $downloadUrl
    rawPath = $rawPath
    redactedPath = $safePath
    sha256 = $hash.Hash
    bytes = $bytes.Length
    contentType = ($response.Content.Headers.ContentType | ForEach-Object { $_.ToString() })
    secretsRedacted = ($text -ne $redacted)
    executionPolicy = "download-only; no browser session; no cookies; no script execution"
  }
  $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $reportPath -Encoding UTF8

  Write-Host "Intake seguro concluido." -ForegroundColor Green
  Write-Host "Raw: $rawPath" -ForegroundColor Yellow
  Write-Host "Redigido: $safePath" -ForegroundColor Yellow
  Write-Host "Relatorio: $reportPath" -ForegroundColor Yellow
  Write-Host "SHA256: $($hash.Hash)" -ForegroundColor Cyan
} finally {
  $response.Dispose()
  $client.Dispose()
}
