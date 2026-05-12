param(
  [string]$Namespace = "aios-prod",
  [string]$ExpectedContext = "aios-prod",
  [switch]$SkipPreflight,
  [switch]$CreateClusterSecrets,
  [string]$RegistryServer = "registry.aios.internal:5443",
  [string]$VaultBucket = $env:VAULT_BUCKET,
  [string]$RegistryDockerConfigJson = $env:AIOS_REGISTRY_DOCKERCONFIGJSON
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function ConvertTo-Base64Value {
  param([Parameter(Mandatory=$true)][string]$Value)
  return [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Value))
}

function ConvertTo-SecretDataYaml {
  param([Parameter(Mandatory=$true)][hashtable]$Values)
  $lines = New-Object System.Collections.Generic.List[string]
  foreach ($key in ($Values.Keys | Sort-Object)) {
    $value = [string]$Values[$key]
    if (-not [string]::IsNullOrWhiteSpace($value)) {
      $lines.Add("  ${key}: $(ConvertTo-Base64Value $value)")
    }
  }
  if ($lines.Count -eq 0) {
    throw "Secret data cannot be empty."
  }
  return ($lines -join "`n")
}

function Apply-OpaqueSecret {
  param(
    [Parameter(Mandatory=$true)][string]$Name,
    [Parameter(Mandatory=$true)][string]$Namespace,
    [Parameter(Mandatory=$true)][hashtable]$Values
  )

  $dataYaml = ConvertTo-SecretDataYaml -Values $Values
  $yaml = @"
apiVersion: v1
kind: Secret
metadata:
  name: $Name
  namespace: $Namespace
type: Opaque
data:
$dataYaml
"@
  $yaml | kubectl apply -f -
}

function Get-RegistryDockerConfigJson {
  param(
    [Parameter(Mandatory=$true)][string]$RegistryServer,
    [string]$ExplicitValue
  )

  if (-not [string]::IsNullOrWhiteSpace($ExplicitValue)) {
    return $ExplicitValue
  }

  $dockerConfigPath = Join-Path $HOME ".docker\config.json"
  if ((Test-Path $dockerConfigPath) -and ((Get-Content -Raw $dockerConfigPath) -match [regex]::Escape($RegistryServer))) {
    return (Get-Content -Raw $dockerConfigPath)
  }

  throw "Registry docker config is missing. Run docker login $RegistryServer or set AIOS_REGISTRY_DOCKERCONFIGJSON to the approved docker config JSON."
}

function Apply-DockerConfigSecret {
  param(
    [Parameter(Mandatory=$true)][string]$Name,
    [Parameter(Mandatory=$true)][string]$Namespace,
    [Parameter(Mandatory=$true)][string]$DockerConfigJson
  )

  $encoded = ConvertTo-Base64Value $DockerConfigJson
  $yaml = @"
apiVersion: v1
kind: Secret
metadata:
  name: $Name
  namespace: $Namespace
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: $encoded
"@
  $yaml | kubectl apply -f -
}

$repoRoot = Split-Path $PSScriptRoot -Parent
Push-Location $repoRoot
try {
  if ($CreateClusterSecrets) {
    if ([string]::IsNullOrWhiteSpace($VaultBucket)) {
      throw "VAULT_BUCKET is required to create vault-creds."
    }

    $vaultValues = @{
      VAULT_BUCKET = $VaultBucket
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AWS_ACCESS_KEY_ID)) {
      $vaultValues["AWS_ACCESS_KEY_ID"] = $env:AWS_ACCESS_KEY_ID
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AWS_SECRET_ACCESS_KEY)) {
      $vaultValues["AWS_SECRET_ACCESS_KEY"] = $env:AWS_SECRET_ACCESS_KEY
    }
    if (-not [string]::IsNullOrWhiteSpace($env:AWS_SESSION_TOKEN)) {
      $vaultValues["AWS_SESSION_TOKEN"] = $env:AWS_SESSION_TOKEN
    }

    Apply-OpaqueSecret -Name "vault-creds" -Namespace $Namespace -Values $vaultValues
    $dockerConfigJson = Get-RegistryDockerConfigJson -RegistryServer $RegistryServer -ExplicitValue $RegistryDockerConfigJson
    Apply-DockerConfigSecret -Name "aios-registry-pull-secret" -Namespace $Namespace -DockerConfigJson $dockerConfigJson
  }

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
