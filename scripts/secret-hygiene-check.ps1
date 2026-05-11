param(
  [switch]$WriteReport
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ForbiddenNames = @(
  "auth.json",
  ".env",
  "secure_runtime_binding.store",
  "runtime-binding.dpapi.json",
  "credentials.json",
  "service-token.txt",
  "openai_api_key.txt"
)
$ForbiddenExtensions = @(".pem", ".pfx", ".p12", ".key")

function Get-RelativePathString([string]$BasePath, [string]$TargetPath) {
  $base = [IO.Path]::GetFullPath($BasePath)
  if (-not $base.EndsWith([IO.Path]::DirectorySeparatorChar)) {
    $base += [IO.Path]::DirectorySeparatorChar
  }

  $target = [IO.Path]::GetFullPath($TargetPath)
  $baseUri = [Uri]::new($base)
  $targetUri = [Uri]::new($target)
  return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString()).Replace('/', [IO.Path]::DirectorySeparatorChar)
}

function Convert-ToRepoPath([string]$Path) {
  $resolved = Resolve-Path -LiteralPath $Path
  return Get-RelativePathString $Root $resolved
}

function Test-IsIgnored([string]$Path) {
  Push-Location $Root
  try {
    git check-ignore -q -- "$Path"
    return $LASTEXITCODE -eq 0
  } finally {
    Pop-Location
  }
}

Push-Location $Root
try {
  $trackedForbidden = git ls-files |
    Where-Object {
      $name = Split-Path $_ -Leaf
      $ext = [IO.Path]::GetExtension($name).ToLowerInvariant()
      ($ForbiddenNames -contains $name) -or ($ForbiddenExtensions -contains $ext)
    }

  $workingForbidden = Get-ChildItem -Path $Root -Recurse -File -Force |
    Where-Object {
      $relative = Get-RelativePathString $Root $_.FullName
      if ($relative -match '^(node_modules|\.git|\.venv|frontend\\node_modules|frontend\\dist|frontend\\test-results|release)(\\|$)') {
        return $false
      }

      ($ForbiddenNames -contains $_.Name) -or ($ForbiddenExtensions -contains $_.Extension.ToLowerInvariant())
    } |
    ForEach-Object {
      $repoPath = Convert-ToRepoPath $_.FullName
      [pscustomobject]@{
        path = $repoPath
        ignored = Test-IsIgnored $repoPath
      }
    }

  $unignoredForbidden = @($workingForbidden | Where-Object { -not $_.ignored })
  $ok = (@($trackedForbidden).Count -eq 0) -and ($unignoredForbidden.Count -eq 0)

  $result = [ordered]@{
    ok = $ok
    scannedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    policy = "Secrets are checked by path and Git status only; file contents are never read."
    trackedForbiddenCount = @($trackedForbidden).Count
    unignoredForbiddenCount = $unignoredForbidden.Count
    trackedForbiddenPaths = @($trackedForbidden)
    unignoredForbiddenPaths = @($unignoredForbidden | ForEach-Object { $_.path })
  }

  $json = $result | ConvertTo-Json -Depth 5
  Write-Output $json

  if ($WriteReport) {
    $releaseDir = Join-Path $Root "release"
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null
    $reportPath = Join-Path $releaseDir "SECRET_HYGIENE_REPORT.md"
    $status = if ($ok) { "PASS" } else { "FAIL" }
    $body = @"
# Secret Hygiene Report

- Status: $status
- Generated: $($result.scannedAt)
- Policy: $($result.policy)
- Tracked forbidden files: $($result.trackedForbiddenCount)
- Unignored forbidden files: $($result.unignoredForbiddenCount)

## Tracked Forbidden Paths

$(if (@($trackedForbidden).Count) { ($trackedForbidden | ForEach-Object { "- $_" }) -join "`n" } else { "- None" })

## Unignored Forbidden Paths

$(if ($unignoredForbidden.Count) { ($unignoredForbidden | ForEach-Object { "- $($_.path)" }) -join "`n" } else { "- None" })

## Notes

- This check never reads, prints, copies, or exports secret values.
- auth.json is treated like a password and must stay outside Git, logs, ZIP packages, and frontend code.
- Real runtime credentials must be stored through DPAPI, Vault/KMS, or an approved secret manager.
"@
    Set-Content -LiteralPath $reportPath -Value $body -Encoding UTF8
  }

  if (-not $ok) {
    exit 1
  }
} finally {
  Pop-Location
}
