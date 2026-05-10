param(
  [ValidateSet("openai_codex", "openai_api", "azure_openai")]
  [string]$Provider = "openai_codex",
  [string]$RuntimeEndpoint = "",
  [securestring]$ServiceToken,
  [string]$TenantId = "",
  [string]$SandboxEnvironmentId = "",
  [ValidateSet("vault", "kms", "vault/kms", "openai-managed-kms")]
  [string]$SecretStore = "vault",
  [securestring]$OpenAIApiKey,
  [string]$OpenAIBaseUrl = "https://api.openai.com/v1",
  [string]$OpenAIProjectId = "",
  [string]$OpenAIOrganizationId = "",
  [string]$OpenAIModel = "gpt-5.2-codex",
  [string]$AzureOpenAIEndpoint = "",
  [securestring]$AzureOpenAIApiKey,
  [string]$AzureDeployment = "",
  [switch]$Prompt,
  [switch]$ConfirmExternalSecretStore,
  [string]$StorePath = ""
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $StorePath) {
  $StorePath = Join-Path $Root ".aios-secure\runtime-binding.dpapi.json"
}

function Assert-RealValue($Name, $Value, [switch]$AllowEmpty) {
  if ([string]::IsNullOrWhiteSpace($Value)) {
    if ($AllowEmpty) { return }
    throw "$Name ausente."
  }
  $lower = $Value.Trim().ToLowerInvariant()
  if ($lower.Contains("<") -or $lower.Contains(">") -or $lower.Contains("placeholder") -or $lower.Contains("example") -or $lower.Contains("fake")) {
    throw "$Name parece placeholder. Use apenas valor real emitido para este projeto."
  }
}

function Protect-Secret($Name, [securestring]$Secret) {
  if ($null -eq $Secret) {
    throw "$Name ausente. Passe o parametro seguro ou use -Prompt."
  }
  return $Secret | ConvertFrom-SecureString
}

if (-not $ConfirmExternalSecretStore) {
  throw "Confirme que a credencial veio de Vault/KMS/ponte segura usando -ConfirmExternalSecretStore."
}

if ($Prompt) {
  if ($Provider -eq "openai_codex") {
    if (-not $RuntimeEndpoint) { $RuntimeEndpoint = Read-Host "Endpoint oficial do runtime Codex" }
    if (-not $TenantId) { $TenantId = Read-Host "Tenant ID aprovado" }
    if (-not $SandboxEnvironmentId) { $SandboxEnvironmentId = Read-Host "Sandbox Environment ID aprovado" }
    if ($null -eq $ServiceToken) { $ServiceToken = Read-Host "Service token oficial" -AsSecureString }
  } elseif ($Provider -eq "openai_api") {
    if (-not $OpenAIBaseUrl) { $OpenAIBaseUrl = Read-Host "OpenAI Base URL" }
    if (-not $SandboxEnvironmentId) { $SandboxEnvironmentId = Read-Host "Sandbox Environment ID aprovado" }
    if ($null -eq $OpenAIApiKey) { $OpenAIApiKey = Read-Host "OpenAI API key" -AsSecureString }
  } elseif ($Provider -eq "azure_openai") {
    if (-not $AzureOpenAIEndpoint) { $AzureOpenAIEndpoint = Read-Host "Azure OpenAI endpoint" }
    if (-not $AzureDeployment) { $AzureDeployment = Read-Host "Azure deployment" }
    if (-not $SandboxEnvironmentId) { $SandboxEnvironmentId = Read-Host "Sandbox Environment ID aprovado" }
    if ($null -eq $AzureOpenAIApiKey) { $AzureOpenAIApiKey = Read-Host "Azure OpenAI API key" -AsSecureString }
  }
}

& "$PSScriptRoot\contract-authority.ps1" verify | Out-Host

$payload = [ordered]@{
  version = 1
  createdAt = (Get-Date -Format o)
  provider = $Provider
  secretStore = $SecretStore
  sandboxEnvironmentId = $SandboxEnvironmentId.Trim()
  liveEnabled = $true
  secrets = [ordered]@{}
}

if ($Provider -eq "openai_codex") {
  Assert-RealValue "RuntimeEndpoint" $RuntimeEndpoint
  Assert-RealValue "TenantId" $TenantId
  Assert-RealValue "SandboxEnvironmentId" $SandboxEnvironmentId
  if (-not $RuntimeEndpoint.StartsWith("https://")) { throw "RuntimeEndpoint deve usar https://" }
  $payload.runtimeEndpoint = $RuntimeEndpoint.Trim()
  $payload.tenantId = $TenantId.Trim()
  $payload.secrets.serviceToken = Protect-Secret "ServiceToken" $ServiceToken
} elseif ($Provider -eq "openai_api") {
  Assert-RealValue "OpenAIBaseUrl" $OpenAIBaseUrl
  Assert-RealValue "SandboxEnvironmentId" $SandboxEnvironmentId
  Assert-RealValue "OpenAIProjectId" $OpenAIProjectId -AllowEmpty
  Assert-RealValue "OpenAIOrganizationId" $OpenAIOrganizationId -AllowEmpty
  if (-not $OpenAIBaseUrl.StartsWith("https://")) { throw "OpenAIBaseUrl deve usar https://" }
  $payload.openaiBaseUrl = $OpenAIBaseUrl.Trim()
  $payload.openaiProjectId = $OpenAIProjectId.Trim()
  $payload.openaiOrganizationId = $OpenAIOrganizationId.Trim()
  $payload.openaiModel = $OpenAIModel.Trim()
  $payload.secrets.openaiApiKey = Protect-Secret "OpenAIApiKey" $OpenAIApiKey
} elseif ($Provider -eq "azure_openai") {
  Assert-RealValue "AzureOpenAIEndpoint" $AzureOpenAIEndpoint
  Assert-RealValue "AzureDeployment" $AzureDeployment
  Assert-RealValue "SandboxEnvironmentId" $SandboxEnvironmentId
  if (-not $AzureOpenAIEndpoint.StartsWith("https://")) { throw "AzureOpenAIEndpoint deve usar https://" }
  $payload.azureOpenAIEndpoint = $AzureOpenAIEndpoint.Trim()
  $payload.azureDeployment = $AzureDeployment.Trim()
  $payload.secrets.azureOpenAIApiKey = Protect-Secret "AzureOpenAIApiKey" $AzureOpenAIApiKey
}

$storeDir = Split-Path -Parent $StorePath
New-Item -ItemType Directory -Force -Path $storeDir | Out-Null
try {
  (Get-Item -LiteralPath $storeDir).Attributes = (Get-Item -LiteralPath $storeDir).Attributes -bor [IO.FileAttributes]::Hidden
} catch {
  # Best effort only.
}

$payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $StorePath -Encoding UTF8

Write-Host "Binding seguro salvo com DPAPI local." -ForegroundColor Green
Write-Host "Arquivo: $StorePath" -ForegroundColor Cyan
Write-Host "Provider: $Provider" -ForegroundColor Cyan
Write-Host "Sandbox: $SandboxEnvironmentId" -ForegroundColor Cyan
Write-Host "Secret store: $SecretStore" -ForegroundColor Cyan
Write-Host "Segredo: [REDACTED]" -ForegroundColor Cyan
