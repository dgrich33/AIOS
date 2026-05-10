param(
  [Parameter(Mandatory=$true)][securestring]$OpenAIApiKey,
  [string]$BaseUrl = "https://api.openai.com/v1",
  [string]$ProjectId = "",
  [string]$OrganizationId = "",
  [string]$SandboxEnvironmentId = "aios-rc5-openai-api-sandbox",
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
    throw "$Name parece placeholder. Use apenas valor real da OpenAI API Platform."
  }
}

Assert-RealValue "BaseUrl" $BaseUrl
Assert-RealValue "SandboxEnvironmentId" $SandboxEnvironmentId

if (-not $BaseUrl.StartsWith("https://")) {
  throw "BaseUrl deve usar https://"
}

if (-not $ConfirmExternalSecretStore) {
  throw "Confirme que a API key veio de armazenamento seguro/aprovado usando -ConfirmExternalSecretStore."
}

$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($OpenAIApiKey)
try {
  $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

Assert-RealValue "OpenAIApiKey" $plainKey
if ($plainKey.Length -lt 20) {
  throw "OpenAIApiKey curta demais para ser aceita como credencial real."
}

Write-Host "Verificando contrato soberano..."
& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$env:AIOS_OFFICIAL_SANDBOX_PROVIDER = "openai_api"
$env:OPENAI_BASE_URL = $BaseUrl.Trim()
$env:OPENAI_API_KEY = $plainKey
$env:OPENAI_PROJECT_ID = $ProjectId.Trim()
$env:OPENAI_ORG_ID = $OrganizationId.Trim()
$env:AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID = $SandboxEnvironmentId.Trim()
$env:AIOS_OFFICIAL_SANDBOX_SECRET_STORE = $SecretStore
$env:AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED = "true"

Write-Host "Perfil OpenAI API RC5 carregado somente nesta sessao e nos processos filhos."
Write-Host "Base URL: $BaseUrl"
Write-Host "Project: $(if ($ProjectId) { $ProjectId } else { 'opcional/nao configurado' })"
Write-Host "Organization: $(if ($OrganizationId) { $OrganizationId } else { 'opcional/nao configurado' })"
Write-Host "Sandbox: $SandboxEnvironmentId"
Write-Host "Secret store: $SecretStore"
Write-Host "API key: [REDACTED]"

& "$PSScriptRoot\rc1-start-local.ps1"
& "$PSScriptRoot\rc5-validate.ps1"

Write-Host "RC5 OpenAI API sandbox iniciado com gates carregados. A chave nao foi gravada no repositorio."
