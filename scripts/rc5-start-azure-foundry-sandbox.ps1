param(
  [Parameter(Mandatory=$true)][string]$AzureOpenAIEndpoint,
  [Parameter(Mandatory=$true)][securestring]$AzureOpenAIApiKey,
  [Parameter(Mandatory=$true)][string]$Deployment,
  [Parameter(Mandatory=$true)][string]$SandboxEnvironmentId,
  [ValidateSet("vault", "kms", "vault/kms", "openai-managed-kms")]
  [string]$SecretStore = "vault",
  [switch]$ConfirmExternalSecretStore
)

$ErrorActionPreference = "Stop"

function Assert-RealValue($Name, $Value) {
  if ([string]::IsNullOrWhiteSpace($Value)) {
    throw "$Name ausente."
  }
  $lower = $Value.Trim().ToLowerInvariant()
  if ($lower.Contains("<") -or $lower.Contains(">") -or $lower.Contains("placeholder") -or $lower.Contains("example") -or $lower.Contains("fake")) {
    throw "$Name parece placeholder. Use apenas valor real emitido para Azure Foundry/OpenAI."
  }
}

Assert-RealValue "AzureOpenAIEndpoint" $AzureOpenAIEndpoint
Assert-RealValue "Deployment" $Deployment
Assert-RealValue "SandboxEnvironmentId" $SandboxEnvironmentId

if (-not $AzureOpenAIEndpoint.StartsWith("https://")) {
  throw "AzureOpenAIEndpoint deve usar https://"
}

if (-not $ConfirmExternalSecretStore) {
  throw "Confirme que a chave veio de Vault/KMS aprovado usando -ConfirmExternalSecretStore."
}

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($AzureOpenAIApiKey)
try {
  $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

Assert-RealValue "AzureOpenAIApiKey" $plainKey
if ($plainKey.Length -lt 20) {
  throw "AzureOpenAIApiKey curta demais para ser aceita como credencial real."
}

Write-Host "Verificando contrato soberano..."
& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$env:AIOS_OFFICIAL_SANDBOX_PROVIDER = "azure_openai"
$env:AZURE_OPENAI_ENDPOINT = $AzureOpenAIEndpoint.Trim()
$env:AZURE_OPENAI_API_KEY = $plainKey
$env:AZURE_OPENAI_DEPLOYMENT = $Deployment.Trim()
$env:AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID = $SandboxEnvironmentId.Trim()
$env:AIOS_OFFICIAL_SANDBOX_SECRET_STORE = $SecretStore
$env:AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED = "true"

Write-Host "Perfil Azure OpenAI/Foundry RC5 carregado somente nesta sessao e nos processos filhos."
Write-Host "Endpoint: $AzureOpenAIEndpoint"
Write-Host "Deployment: $Deployment"
Write-Host "Sandbox: $SandboxEnvironmentId"
Write-Host "Secret store: $SecretStore"
Write-Host "API key: [REDACTED]"

& "$PSScriptRoot\rc1-start-local.ps1"
& "$PSScriptRoot\rc5-validate.ps1"

Write-Host "RC5 Azure Foundry sandbox iniciado com gates carregados. A chave nao foi gravada no repositorio."
