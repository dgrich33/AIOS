param(
  [string]$Namespace = "aios-prod",
  [string]$ExpectedContext = "aios-prod",
  [switch]$SkipClusterCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$minKubectlMajor = 1
$minKubectlMinor = 36

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

function Test-KubeGitVersion {
  param([Parameter(Mandatory=$true)][string]$GitVersion)
  $match = [regex]::Match($GitVersion, "^v(?<maj>\d+)\.(?<min>\d+)")
  if (-not $match.Success) {
    return $false
  }
  $maj = [int]$match.Groups["maj"].Value
  $min = [int]$match.Groups["min"].Value
  return ($maj -gt $minKubectlMajor) -or ($maj -eq $minKubectlMajor -and $min -ge $minKubectlMinor)
}

function Get-KubeClientVersion {
  $json = (& kubectl version --client -o json | ConvertFrom-Json)
  return [string]$json.clientVersion.gitVersion
}

function Get-KubeServerVersion {
  $json = (& kubectl version -o json | ConvertFrom-Json)
  return [string]$json.serverVersion.gitVersion
}

$results = New-Object System.Collections.Generic.List[object]
$requiredClusterSecrets = @("vault-creds", "aios-registry-pull-secret")

foreach ($tool in @("git", "kubectl", "kustomize", "aws")) {
  $results.Add((Add-Result "tool:$tool" (Test-Tool $tool) ($(if (Test-Tool $tool) { "found" } else { "missing" }))))
}

$makePresent = Test-Tool "make"
$aiosctlPresent = Test-Tool "aiosctl"
$results.Add((Add-Result "optional:make" $makePresent ($(if ($makePresent) { "found" } else { "missing; beta organ training command will not run here" }))))
$results.Add((Add-Result "optional:aiosctl" $aiosctlPresent ($(if ($aiosctlPresent) { "found" } else { "missing; organ push and mission smoke need this tool" }))))

if (Test-Tool "kubectl") {
  try {
    $clientVersion = Get-KubeClientVersion
    $results.Add((Add-Result "kubectl-client-version" (Test-KubeGitVersion $clientVersion) "client $clientVersion; requires >= v1.36.0"))
  } catch {
    $results.Add((Add-Result "kubectl-client-version" $false "unable to determine kubectl client version"))
  }
}

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

  try {
    $serverVersion = Get-KubeServerVersion
    $results.Add((Add-Result "cluster-version" (Test-KubeGitVersion $serverVersion) "server $serverVersion; cluster needs Kubernetes 1.36.x or newer"))
  } catch {
    $results.Add((Add-Result "cluster-version" $false "unable to determine server version; cluster needs Kubernetes 1.36.x or newer"))
  }

  foreach ($secretName in $requiredClusterSecrets) {
    try {
      $null = & kubectl -n $Namespace get secret $secretName 2>$null
      $results.Add((Add-Result "cluster-secret:$secretName" $true "present"))
    } catch {
      $results.Add((Add-Result "cluster-secret:$secretName" $false "missing; create with rc35-prod-deploy.ps1 -CreateClusterSecrets or apply the approved secret out-of-band"))
    }
  }
} elseif ($SkipClusterCheck) {
  $results.Add((Add-Result "cluster-check" $true "skipped by operator"))
}

$failed = @($results | Where-Object { -not $_.ok })
$missingSecrets = @($failed | Where-Object { $_.name -like "cluster-secret:*" })
$versionFailures = @($failed | Where-Object { $_.name -in @("kubectl-client-version", "cluster-version") })
$results | Format-Table -AutoSize

if ($failed.Count -gt 0) {
  Write-Host ""
  if ($versionFailures.Count -gt 0) {
    Write-Host "KUBERNETES VERSION BLOCKED - cluster needs Kubernetes 1.36.x or newer." -ForegroundColor Yellow
    exit 3
  }
  if ($missingSecrets.Count -gt 0) {
    Write-Host "MISSING SECRETS - run rc35-prod-deploy.ps1 -CreateClusterSecrets first." -ForegroundColor Yellow
    exit 2
  }
  Write-Host "RC35 prod preflight blocked. Corrija os itens acima antes de deploy/tag." -ForegroundColor Yellow
  exit 1
}

Write-Host ""
Write-Host "RC35 prod preflight passed. Deploy pode continuar." -ForegroundColor Green
