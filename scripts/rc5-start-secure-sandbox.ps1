param(
  [Parameter(Mandatory=$true)][string]$RuntimeEndpoint,
  [Parameter(Mandatory=$true)][securestring]$ServiceToken,
  [Parameter(Mandatory=$true)][string]$TenantId,
  [Parameter(Mandatory=$true)][string]$SandboxEnvironmentId,
  [ValidateSet("vault", "kms", "vault/kms", "openai-managed-kms")]
  [string]$SecretStore = "vault",
  [switch]$ConfirmExternalSecretStore
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Assert-RealValue($Name, $Value) {
  if ([string]::IsNullOrWhiteSpace($Value)) {
    throw "$Name ausente."
  }
  $lower = $Value.Trim().ToLowerInvariant()
  if ($lower.Contains("<") -or $lower.Contains(">") -or $lower.Contains("placeholder") -or $lower.Contains("example") -or $lower.Contains("fake")) {
    throw "$Name parece placeholder. Use apenas valor real emitido para o sandbox oficial."
  }
}

Assert-RealValue "RuntimeEndpoint" $RuntimeEndpoint
Assert-RealValue "TenantId" $TenantId
Assert-RealValue "SandboxEnvironmentId" $SandboxEnvironmentId

if (-not $RuntimeEndpoint.StartsWith("https://")) {
  throw "RuntimeEndpoint deve usar https://"
}

if (-not $ConfirmExternalSecretStore) {
  throw "Confirme que o token veio de Vault/KMS aprovado usando -ConfirmExternalSecretStore."
}

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($ServiceToken)
try {
  $plainToken = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

Assert-RealValue "ServiceToken" $plainToken
if ($plainToken.Length -lt 20) {
  throw "ServiceToken curto demais para ser aceito como credencial oficial."
}

Write-Host "Verificando contrato soberano..."
& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$env:AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT = $RuntimeEndpoint.Trim()
$env:AIOS_OFFICIAL_CODEX_SERVICE_TOKEN = $plainToken
$env:AIOS_OFFICIAL_CODEX_TENANT_ID = $TenantId.Trim()
$env:AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID = $SandboxEnvironmentId.Trim()
$env:AIOS_OFFICIAL_SANDBOX_SECRET_STORE = $SecretStore
$env:AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED = "true"

Write-Host "Ambiente oficial RC5 carregado somente nesta sessao e nos processos filhos."
Write-Host "Endpoint: $RuntimeEndpoint"
Write-Host "Tenant: $TenantId"
Write-Host "Sandbox: $SandboxEnvironmentId"
Write-Host "Secret store: $SecretStore"
Write-Host "Service token: [REDACTED]"

& "$PSScriptRoot\rc1-start-local.ps1"
& "$PSScriptRoot\rc5-validate.ps1"

Write-Host "RC5 sandbox oficial iniciado com gates carregados. O token nao foi gravado no repositorio."
