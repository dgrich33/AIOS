# Runbook - Segredos, Vault/KMS e Credenciais de Runtime

## Objetivo

Definir como endpoint, service credential, tenant, sandbox environment id, Vault/KMS e live flag devem ser recebidos, armazenados, rotacionados e revogados no AIOS Codex Unlimited.

## Escopo

Este runbook cobre:

- credenciais do OfficialCodexRuntimeAdapter;
- service tokens por tenant;
- chaves OpenAI API ou Azure OpenAI quando usadas como provider aprovado;
- binding local DPAPI RC17;
- Vault/KMS oficial;
- revogacao e rotacao.

## Principios

- Segredos nao entram no frontend.
- Segredos nao entram em logs.
- Segredos nao entram em ZIP, EXE, MSI ou repo.
- Segredos nao entram em exports, PDFs ou telemetria visivel ao usuario.
- O usuario final ve sessoes, atividade e saude do sistema, nao saldo ou quota.

## Armazenamento

| Ambiente | Armazenamento |
|---|---|
| Desenvolvimento autorizado | DPAPI local RC17 + Vault/KMS quando disponivel |
| Sandbox oficial | Vault/KMS ou Secure Runtime Bridge |
| Staging | Vault/KMS obrigatorio |
| Producao condicionada | Vault/KMS oficial + revogacao centralizada |

## Variaveis esperadas

```txt
AIOS_OFFICIAL_SANDBOX_PROVIDER
AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT
AIOS_OFFICIAL_CODEX_SERVICE_TOKEN
AIOS_OFFICIAL_CODEX_TENANT_ID
AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID
AIOS_OFFICIAL_SANDBOX_SECRET_STORE
AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED
OPENAI_BASE_URL
OPENAI_API_KEY
OPENAI_PROJECT_ID
OPENAI_ORG_ID
OPENAI_MODEL
```

## Rotacao

- Periodicidade: 90 dias.
- Rotacao imediata em incidente, troca de responsavel, suspeita de exposicao, desligamento de acesso ou mudanca de escopo.
- A rotacao deve registrar requestId, actorId, tenantId, data, provider, ambiente e resultado.

## Revogacao

1. Pausar novas sessoes de runtime vivo.
2. Revogar service token/API key no provider oficial.
3. Invalidar identity profile e tenant binding afetado.
4. Remover binding DPAPI local quando aplicavel.
5. Rodar `runtime-binding-status.ps1 -WriteReport`.
6. Confirmar `canInvokeLiveRuntime: false` se a revogacao foi total.
7. Registrar auditoria e abrir incidente se necessario.

## Comandos

Salvar binding local:

```powershell
$token = Read-Host "Service token oficial" -AsSecureString

.\scripts\runtime-binding-save-local.ps1 `
  -Provider openai_codex `
  -RuntimeEndpoint "https://endpoint-oficial" `
  -ServiceToken $token `
  -TenantId "tenant-aprovado" `
  -SandboxEnvironmentId "sandbox-aprovado" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

Validar:

```powershell
.\scripts\stop.ps1
.\scripts\start.ps1 -Mode Local
.\scripts\runtime-binding-status.ps1 -WriteReport
```

## Evidencia

Guardar somente relatorios redigidos em `release/`.

Nunca anexar valor bruto de token, API key, cookie, auth file ou private key.
