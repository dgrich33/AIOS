# AIOS Codex Unlimited RC5 - Official Sandbox Activation

## Objetivo

A RC5 prepara a ativacao do sandbox oficial sem criar sucesso falso. O AIOS so libera invocacao real quando todos os gates de seguranca estiverem presentes no ambiente.

## Gates obrigatorios

- contrato travado por `scripts/contract-authority.ps1 verify`;
- endpoint oficial configurado em `AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT`;
- service token configurado fora do frontend em `AIOS_OFFICIAL_CODEX_SERVICE_TOKEN`;
- tenant configurado em `AIOS_OFFICIAL_CODEX_TENANT_ID`;
- ambiente sandbox configurado em `AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID`;
- secret store declarado como `vault`, `kms`, `vault/kms` ou `openai-managed-kms`;
- flag explicita `AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED=true`;
- perfis de dados reais com redaction obrigatoria e export publico bloqueado.

## Endpoints RC5

- `GET /official-sandbox/security-check`
- `GET /official-sandbox/activation`
- `POST /official-sandbox/activate`
- `GET /official-sandbox/data-profiles`
- `POST /official-sandbox/data-profiles`
- `GET /official-sandbox/provider-profile`

## Comportamento esperado

Sem ambiente seguro completo, `/official-sandbox/activate` retorna HTTP 412. Isso e intencional e confirma que o sistema nao esta inventando uma ativacao oficial.

Com ambiente seguro completo, a ativacao passa a retornar `activated: true`, mantendo `networkCallPerformed: false` no proprio endpoint de ativacao. Chamadas reais ao runtime devem passar pelo `OfficialCodexRuntimeAdapter`.

As variaveis oficiais precisam existir antes do backend iniciar. Depois de preencher o ambiente seguro, reinicie o backend local ou a stack Docker para que a configuracao seja recarregada.

## Dados reais no sandbox

Dados reais aprovados podem ser registrados apenas como perfil operacional. O AIOS exige:

- `dataClassification = real_sandbox_approved`;
- `approvalReference` preenchido;
- `redactionRequired = true`;
- `publicExportAllowed = false`.

## Validacao

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\contract-authority.ps1 verify
.\scripts\rc5-env-template.ps1
.\scripts\rc1-start-local.ps1
.\scripts\rc5-validate.ps1
.\scripts\rc5-package.ps1
```

## Start seguro com credenciais reais

Quando endpoint, service token, tenant e sandbox aprovados estiverem carregados no ambiente seguro, use:

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$token = Read-Host "Service token oficial" -AsSecureString

.\scripts\rc5-start-secure-sandbox.ps1 `
  -RuntimeEndpoint "https://endpoint-oficial-sandbox" `
  -ServiceToken $token `
  -TenantId "tenant-aprovado" `
  -SandboxEnvironmentId "sandbox-aprovado" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

O script recusa placeholders, exige `https://`, exige confirmacao de Vault/KMS, nao imprime o token e nao grava credencial no repositorio.

## Perfil Azure OpenAI / Microsoft Foundry

As fontes oficiais da Microsoft documentam um caminho pratico para Codex via Azure OpenAI/Foundry usando endpoint do recurso, chave API e nome do deployment. Para esse perfil, use:

```powershell
$key = Read-Host "Azure OpenAI API key oficial" -AsSecureString

.\scripts\rc5-start-azure-foundry-sandbox.ps1 `
  -AzureOpenAIEndpoint "https://resource.openai.azure.com/openai/v1" `
  -AzureOpenAIApiKey $key `
  -Deployment "gpt-5-codex" `
  -SandboxEnvironmentId "sandbox-aprovado" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

Nesse modo, `Tenant ID` nao e gate obrigatorio quando a autenticacao aprovada for API key. O AIOS ainda exige secret store, sandbox environment id, live flag e contrato travado.

Para uma explicacao simples de endpoint, API key, deployment e service token, leia:

`docs/RC5_GUIA_CREDENCIAIS_OFICIAIS_PT.md`

## Perfil OpenAI API direta

Para usar a API da OpenAI diretamente, nao e necessario deployment Azure. Use uma API key da OpenAI Platform:

```powershell
$key = Read-Host "OpenAI API key oficial" -AsSecureString

.\scripts\rc5-start-openai-api-sandbox.ps1 `
  -OpenAIApiKey $key `
  -BaseUrl "https://api.openai.com/v1" `
  -ProjectId "proj_..." `
  -SandboxEnvironmentId "aios-rc5-openai-api-sandbox" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

`ProjectId` e recomendado para auditoria e escopo, mas pode ficar vazio no primeiro teste local se a API key ja estiver vinculada ao projeto correto.

## Resultado de seguranca

A RC5 prioriza ambiente seguro primeiro. Se endpoint, token, tenant ou Vault/KMS nao estiverem carregados no processo do backend, o produto mostra exatamente esse estado e bloqueia ativacao real ate a configuracao local estar completa.
