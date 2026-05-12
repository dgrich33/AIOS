param(
  [string]$Version = "v1.1.0",
  [switch]$IConfirmProdSmokePassed
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if (-not $IConfirmProdSmokePassed) {
  throw "Release tag blocked. Run prod deploy + mission smoke first, then rerun with -IConfirmProdSmokePassed."
}

$branch = (& git rev-parse --abbrev-ref HEAD).Trim()
if ($branch -ne "main") {
  throw "Release tag must be created from main. Current branch: $branch"
}

$status = (& git status --porcelain)
if (-not [string]::IsNullOrWhiteSpace($status)) {
  throw "Working tree is not clean. Commit or revert local changes before tagging."
}

git fetch origin main --tags
$local = (& git rev-parse HEAD).Trim()
$remote = (& git rev-parse origin/main).Trim()
if ($local -ne $remote) {
  throw "Local main does not match origin/main. Pull/rebase before tagging."
}

git tag $Version -m "AIOS Codex OS Sovereign + Codex Plan Bridge"
git push origin $Version
Write-Host "Release tag pushed: $Version" -ForegroundColor Green
