# RC17 - Secure Runtime Binding Store

## Objetivo

Implementar um cofre local seguro para armazenar dados tecnicos reais de integracao de runtime quando entregues oficialmente:

- endpoint;
- service credential;
- tenant;
- sandbox environment id;
- configuracao de Vault/KMS;
- live flag.

O cofre nao grava segredos no repositorio, nao expoe segredo no frontend e nao entra no ZIP publico.

## Caminho

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2\.aios-secure\runtime-binding.dpapi.json
```

Os segredos sao protegidos por DPAPI do Windows para o usuario atual da maquina.

## Principios de Seguranca

- Segredos nunca no codigo, repo, ZIP ou build publico.
- Segredos nunca no frontend.
- Segredos nunca em logs, exports ou PDFs.
- O backend carrega o segredo somente em memoria de processo.
- `runtime-binding-status.ps1 -WriteReport` mostra apenas status redigido.
- Uso de live flag exige sandbox/staging autorizado.
- Producao exige revisao de seguranca, red-team, assinatura e signoff.

## Scripts

- `scripts/runtime-binding-save-local.ps1`: salva dados reais no DPAPI local usando `SecureString`.
- `scripts/runtime-binding-load-local.ps1`: carrega dados do cofre para variaveis de ambiente do processo.
- `scripts/start.ps1 -Mode Local`: carrega o cofre automaticamente antes de iniciar backend/frontend.
- `scripts/runtime-binding-status.ps1 -WriteReport`: valida estado de binding sem expor segredos.

## Fluxo Operacional

1. Receber oficialmente endpoint, service credential, tenant, sandbox environment id, Vault/KMS e live flag.
2. Salvar localmente:

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

3. Reiniciar:

```powershell
.\scripts\stop.ps1
.\scripts\start.ps1 -Mode Local
```

4. Validar:

```powershell
.\scripts\runtime-binding-status.ps1 -WriteReport
```

Resultado esperado apos provisionamento real:

```txt
scopeReady: true
bindingState: active
canInvokeLiveRuntime: true
secretsExposed: false
```

## Validacoes RC17

- DPAPI save/load test: OK.
- Package scan: OK.
- Backend tests: 29 passed.
- Frontend build: OK.
- MCP builds: OK.
- Playwright: 2 passed.
- Enterprise check: OK.
- Contract authority: OK.
- Contract docs audit: OK.

## Pacote RC17

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2-RC17.zip
SHA256: B7B80E48A6B8217D4239D547D6AA3B70BB7F855277DE5C1F950A2AC219B6DFD5
```
