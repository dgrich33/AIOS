# RC17 - Final Status (Secure Runtime Binding Store)

## Estado Atual Real

```txt
scopeReady: true
bindingState: awaiting_secure_runtime_binding
provider: openai_codex
canInvokeLiveRuntime: false
secretsExposed: false
```

## Dados Reais Ainda Pendentes

- endpoint oficial;
- service credential;
- tenant ID;
- sandbox environment ID;
- Vault/KMS ativo;
- live flag;
- confirmacao de acesso ao modelo aprovado;
- billing/spend/rate limits;
- destino oficial de auditoria.

## Mecanismo Implementado

RC17 adiciona cofre local via DPAPI do Windows:

```txt
scripts/runtime-binding-save-local.ps1
scripts/runtime-binding-load-local.ps1
```

O `scripts/start.ps1 -Mode Local` carrega esse cofre automaticamente antes de iniciar backend/frontend.

## Qualidade e Validacoes

| Item | Resultado |
|---|---|
| Backend tests | 29 passed |
| Frontend build | OK |
| MCP core build | OK |
| MCP repo build | OK |
| Playwright | 2 passed |
| Enterprise check | OK |
| Contract authority | OK |
| Contract docs audit | OK |
| DPAPI save/load test | OK |
| Package scan | OK |

## Pacote Final

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2-RC17.zip
SHA256: B7B80E48A6B8217D4239D547D6AA3B70BB7F855277DE5C1F950A2AC219B6DFD5
```

## Ambientes Locais

```txt
Frontend: http://127.0.0.1:5173
Backend:  http://127.0.0.1:8000/docs
```

## Proximo Passo Obrigatorio

Receber oficialmente da OpenAI/Codex:

```txt
OPENAI_BASE_URL ou AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT
OPENAI_API_KEY ou AIOS_OFFICIAL_CODEX_SERVICE_TOKEN
OPENAI_PROJECT_ID ou OPENAI_ORG_ID
AIOS_OFFICIAL_CODEX_TENANT_ID
AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID
AIOS_OFFICIAL_SANDBOX_SECRET_STORE
AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED=true
```

Depois executar:

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

.\scripts\stop.ps1
.\scripts\start.ps1 -Mode Local
.\scripts\runtime-binding-status.ps1 -WriteReport
```

Resultado esperado:

```txt
scopeReady: true
bindingState: active
canInvokeLiveRuntime: true
secretsExposed: false
```

## Avisos de Seguranca

- Nao commitar segredos.
- Nao expor service credential no frontend.
- Nao incluir `.aios-secure` no pacote publico.
- Nao expor segredos em respostas de API, exports, PDFs ou telemetria visivel ao usuario.
- Usar live flag somente em sandbox/staging autorizado.
