param(
  [string]$StorePath = "",
  [switch]$Quiet,
  [switch]$AsJson,
  [switch]$WriteReport
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $StorePath) {
  $StorePath = Join-Path $Root ".aios-secure\runtime-binding.dpapi.json"
}

function Unprotect-Secret($Protected) {
  if ([string]::IsNullOrWhiteSpace($Protected)) {
    return ""
  }
  $secure = $Protected | ConvertTo-SecureString
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  try {
    return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
  } finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
}

if (-not (Test-Path -LiteralPath $StorePath)) {
  $result = [ordered]@{
    loaded = $false
    storePath = $StorePath
    reason = "secure binding store not found"
    secretsExposed = $false
  }
  if ($AsJson) { $result | ConvertTo-Json -Depth 6 }
  elseif (-not $Quiet) { Write-Host "Binding local nao encontrado: $StorePath" -ForegroundColor Yellow }
  return
}

$binding = Get-Content -LiteralPath $StorePath -Raw | ConvertFrom-Json
$provider = [string]$binding.provider

$env:AIOS_OFFICIAL_SANDBOX_PROVIDER = $provider
$env:AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID = [string]$binding.sandboxEnvironmentId
$env:AIOS_OFFICIAL_SANDBOX_SECRET_STORE = [string]$binding.secretStore
$env:AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED = if ($binding.liveEnabled) { "true" } else { "false" }

if ($provider -eq "openai_codex") {
  $env:AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT = [string]$binding.runtimeEndpoint
  $env:AIOS_OFFICIAL_CODEX_TENANT_ID = [string]$binding.tenantId
  $env:AIOS_OFFICIAL_CODEX_SERVICE_TOKEN = Unprotect-Secret $binding.secrets.serviceToken
} elseif ($provider -eq "openai_api") {
  $env:OPENAI_BASE_URL = [string]$binding.openaiBaseUrl
  $env:OPENAI_PROJECT_ID = [string]$binding.openaiProjectId
  $env:OPENAI_ORG_ID = [string]$binding.openaiOrganizationId
  $env:OPENAI_MODEL = [string]$binding.openaiModel
  $env:OPENAI_API_KEY = Unprotect-Secret $binding.secrets.openaiApiKey
} elseif ($provider -eq "azure_openai") {
  $env:AZURE_OPENAI_ENDPOINT = [string]$binding.azureOpenAIEndpoint
  $env:AZURE_OPENAI_DEPLOYMENT = [string]$binding.azureDeployment
  $env:AZURE_OPENAI_API_KEY = Unprotect-Secret $binding.secrets.azureOpenAIApiKey
} else {
  throw "Provider desconhecido no binding local: $provider"
}

$result = [ordered]@{
  loaded = $true
  provider = $provider
  storePath = $StorePath
  sandboxEnvironmentConfigured = [bool]$env:AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID
  secretStore = $env:AIOS_OFFICIAL_SANDBOX_SECRET_STORE
  liveFlagEnabled = $env:AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED
  credentialConfigured = [bool](
    $env:AIOS_OFFICIAL_CODEX_SERVICE_TOKEN -or
    $env:OPENAI_API_KEY -or
    $env:AZURE_OPENAI_API_KEY
  )
  secretsExposed = $false
}

if ($WriteReport) {
  $ReleaseDir = Join-Path $Root "release"
  New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
  $ReportPath = Join-Path $ReleaseDir "RC17_SECURE_BINDING_LOAD_REPORT.md"
  @(
    "# AIOS Codex Unlimited RC17 - Secure Binding Load Report",
    "",
    "Data: $(Get-Date -Format o)",
    "",
    "| Campo | Valor |",
    "|---|---|",
    "| Loaded | $($result.loaded) |",
    "| Provider | $($result.provider) |",
    "| Sandbox configured | $($result.sandboxEnvironmentConfigured) |",
    "| Secret store | $($result.secretStore) |",
    "| Live flag | $($result.liveFlagEnabled) |",
    "| Credential configured | $($result.credentialConfigured) |",
    "| Secrets exposed | $($result.secretsExposed) |"
  ) | Set-Content -LiteralPath $ReportPath -Encoding UTF8
}

if ($AsJson) {
  $result | ConvertTo-Json -Depth 6
} elseif (-not $Quiet) {
  Write-Host "Binding local carregado no processo atual." -ForegroundColor Green
  Write-Host "Provider: $provider" -ForegroundColor Cyan
  Write-Host "Sandbox: $($result.sandboxEnvironmentConfigured)" -ForegroundColor Cyan
  Write-Host "Credencial: $(if ($result.credentialConfigured) { 'configurada' } else { 'ausente' })" -ForegroundColor Cyan
  Write-Host "Segredo: [REDACTED]" -ForegroundColor Cyan
}
