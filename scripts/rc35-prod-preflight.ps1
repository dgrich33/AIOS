param(
  [string]$Namespace = "aios-prod",
  [string]$ExpectedContext = "aios-prod",
  [switch]$SkipClusterCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Test-Tool {
  param([Parameter(Mandatory=$true)][string]$Name)
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -eq $cmd) {
    return $false
  }
  return $true
}

function Add-Result {
  param(
    [Parameter(Mandatory=$true)][string]$Name,
    [Parameter(Mandatory=$true)][bool]$Ok,
    [Parameter(Mandatory=$true)][string]$Detail
  )
  [pscustomobject]@{ name = $Name; ok = $Ok; detail = $Detail }
}

$results = New-Object System.Collections.Generic.List[object]

foreach ($tool in @("git", "kubectl", "kustomize", "aws")) {
  $results.Add((Add-Result "tool:$tool" (Test-Tool $tool) ($(if (Test-Tool $tool) { "found" } else { "missing" }))))
}

$makePresent = Test-Tool "make"
$aiosctlPresent = Test-Tool "aiosctl"
$results.Add((Add-Result "optional:make" $makePresent ($(if ($makePresent) { "found" } else { "missing; beta organ training command will not run here" }))))
$results.Add((Add-Result "optional:aiosctl" $aiosctlPresent ($(if ($aiosctlPresent) { "found" } else { "missing; organ push and mission smoke need this tool" }))))

$kubeConfig = $env:KUBECONFIG
if ([string]::IsNullOrWhiteSpace($kubeConfig)) {
  $defaultKubeConfig = Join-Path $HOME ".kube\config"
  $results.Add((Add-Result "kubeconfig" (Test-Path $defaultKubeConfig) "KUBECONFIG unset; default path checked"))
} else {
  $results.Add((Add-Result "kubeconfig" (Test-Path $kubeConfig) "KUBECONFIG is set"))
}

$vaultBucketOk = ($env:VAULT_BUCKET -eq "s3://aios-vault")
$results.Add((Add-Result "env:VAULT_BUCKET" $vaultBucketOk ($(if ($vaultBucketOk) { "set to s3://aios-vault" } else { "must be s3://aios-vault" }))))

$awsAuthOk = -not [string]::IsNullOrWhiteSpace($env:AWS_ACCESS_KEY_ID) -or
  -not [string]::IsNullOrWhiteSpace($env:AWS_PROFILE) -or
  -not [string]::IsNullOrWhiteSpace($env:AWS_WEB_IDENTITY_TOKEN_FILE)
$results.Add((Add-Result "aws-auth" $awsAuthOk "AWS key, profile, or IRSA/web-identity expected; values are never printed"))

if (Test-Tool "kustomize") {
  Push-Location (Split-Path $PSScriptRoot -Parent)
  try {
    $null = & kustomize build deploy/kustomize/prod 2>$null
    $results.Add((Add-Result "kustomize-build" $true "deploy/kustomize/prod renders"))
  } catch {
    $results.Add((Add-Result "kustomize-build" $false "deploy/kustomize/prod failed to render"))
  } finally {
    Pop-Location
  }
} else {
  $results.Add((Add-Result "kustomize-build" $false "kustomize missing"))
}

if (-not $SkipClusterCheck -and (Test-Tool "kubectl")) {
  try {
    $currentContext = (& kubectl config current-context 2>$null).Trim()
    $contextOk = $currentContext -eq $ExpectedContext
    $results.Add((Add-Result "kubectl-context" $contextOk "current context: $currentContext"))
  } catch {
    $results.Add((Add-Result "kubectl-context" $false "unable to read current context"))
  }

  try {
    $null = & kubectl get namespace $Namespace 2>$null
    $results.Add((Add-Result "cluster-namespace" $true "namespace $Namespace reachable"))
  } catch {
    $results.Add((Add-Result "cluster-namespace" $false "namespace $Namespace not reachable yet"))
  }
} elseif ($SkipClusterCheck) {
  $results.Add((Add-Result "cluster-check" $true "skipped by operator"))
}

$failed = @($results | Where-Object { -not $_.ok })
$results | Format-Table -AutoSize

if ($failed.Count -gt 0) {
  Write-Host ""
  Write-Host "RC35 prod preflight blocked. Corrija os itens acima antes de deploy/tag." -ForegroundColor Yellow
  exit 1
}

Write-Host ""
Write-Host "RC35 prod preflight passed. Deploy pode continuar." -ForegroundColor Green
