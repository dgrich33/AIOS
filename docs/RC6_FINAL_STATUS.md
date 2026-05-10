# AIOS Codex Unlimited RC6 - Final Status

## Status

RC6 implementa o caminho real de runtime OpenAI API para `/codex/runtime/invoke`.

## O que foi adicionado

- Provider `openai_api` nos gates RC5.
- `OfficialCodexRuntimeAdapter.invoke_responses`.
- Chamada real para `POST /v1/responses`.
- Registro de job `codex.runtime.invoke`.
- Eventos:
  - `codex.runtime.invoked`
  - `codex.runtime.completed`
  - `codex.runtime.failed`
- Script de validacao real:
  - `scripts/rc6-validate-openai-runtime.ps1`
- Script de pacote:
  - `scripts/rc6-package.ps1`

## Como validar com API key real

O backend precisa ser reiniciado com a API key carregada:

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$key = Read-Host "OpenAI API key oficial" -AsSecureString
$env:OPENAI_MODEL = "gpt-5.2-codex"

.\scripts\rc5-start-openai-api-sandbox.ps1 `
  -OpenAIApiKey $key `
  -BaseUrl "https://api.openai.com/v1" `
  -SandboxEnvironmentId "aios-rc5-openai-api-sandbox" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore

.\scripts\rc6-validate-openai-runtime.ps1
```

## Validacoes locais executadas

- Backend tests: 17 passed.
- Frontend build: passed.
- MCP core build: passed.
- MCP repo build: passed.
- Contract authority: OK.

## Observacao

O teste automatizado de backend usa mock da OpenAI API para provar o contrato sem gastar API. A validacao `rc6-validate-openai-runtime.ps1` faz chamada real e deve ser rodada apenas quando a API key oficial estiver carregada no processo do backend.
