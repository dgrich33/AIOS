param(
  [string]$Namespace = "aios-prod",
  [string]$ExpectedContext = "aios-prod",
  [switch]$SkipPreflight
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = Split-Path $PSScriptRoot -Parent
Push-Location $repoRoot
try {
  if (-not $SkipPreflight) {
    & .\scripts\rc35-prod-preflight.ps1 -Namespace $Namespace -ExpectedContext $ExpectedContext
  }

  kubectl apply -k deploy/kustomize/prod/

  foreach ($deployment in @("edge-gateway", "fabric-router", "aios-ui", "aios-backend", "aios-frontend")) {
    kubectl -n $Namespace rollout status "deployment/$deployment" --timeout=180s
  }

  kubectl -n $Namespace get pods -l app.kubernetes.io/part-of=aios
} finally {
  Pop-Location
}
