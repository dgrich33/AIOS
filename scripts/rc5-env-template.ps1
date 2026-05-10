$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$ReleaseDir = Join-Path $Root "release"
New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
$Output = Join-Path $ReleaseDir "RC5_SECURE_ENV_TEMPLATE.md"

$Content = @'
# AIOS Codex Unlimited RC5 - Secure Environment Template

Use este modelo apenas como guia. Nao grave segredos reais no repositorio, no frontend, em logs ou no ZIP publico.

## PowerShell da sessao segura

```powershell
$env:AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT = "https://<endpoint-oficial-sandbox>"
$env:AIOS_OFFICIAL_CODEX_SERVICE_TOKEN = "<token-vindo-do-Vault-ou-KMS>"
$env:AIOS_OFFICIAL_CODEX_TENANT_ID = "<tenant-aprovado>"
$env:AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID = "<sandbox-aprovado>"
$env:AIOS_OFFICIAL_SANDBOX_SECRET_STORE = "vault"
$env:AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED = "true"
```

## Start seguro recomendado

Use este comando em vez de gravar segredo em arquivo:

```powershell
$token = Read-Host "Service token oficial" -AsSecureString
.\scripts\rc5-start-secure-sandbox.ps1 `
  -RuntimeEndpoint "https://<endpoint-oficial-sandbox>" `
  -ServiceToken $token `
  -TenantId "<tenant-aprovado>" `
  -SandboxEnvironmentId "<sandbox-aprovado>" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

## Start seguro com OpenAI API direta

```powershell
$key = Read-Host "OpenAI API key oficial" -AsSecureString
$env:OPENAI_MODEL = "gpt-5.2-codex"
.\scripts\rc5-start-openai-api-sandbox.ps1 `
  -OpenAIApiKey $key `
  -BaseUrl "https://api.openai.com/v1" `
  -ProjectId "proj_..." `
  -SandboxEnvironmentId "aios-rc5-openai-api-sandbox" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

Depois, para validar uma chamada real:

```powershell
.\scripts\rc6-validate-openai-runtime.ps1
```

## Start seguro com Azure OpenAI / Foundry

```powershell
$key = Read-Host "Azure OpenAI API key oficial" -AsSecureString
.\scripts\rc5-start-azure-foundry-sandbox.ps1 `
  -AzureOpenAIEndpoint "https://<resource>.openai.azure.com/openai/v1" `
  -AzureOpenAIApiKey $key `
  -Deployment "<deployment-codex>" `
  -SandboxEnvironmentId "<sandbox-aprovado>" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

## Regras

- O token deve ser emitido e rotacionado pelo responsavel aprovado.
- O token deve existir apenas no processo seguro ou no secret store.
- O frontend nunca recebe credencial oficial.
- Logs e export bundles continuam com redaction.
- Se qualquer variavel faltar, `/official-sandbox/activate` deve permanecer bloqueado.
'@

Set-Content -Path $Output -Value $Content -Encoding UTF8
Write-Host "Template RC5 gerado em: $Output"
Get-Content -Path $Output
