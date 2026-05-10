# AIOS Codex Unlimited RC6 - OpenAI Runtime Invoke Real

## Objetivo

A RC6 liga `/codex/runtime/invoke` ao caminho real da OpenAI API quando o provider `openai_api` esta ativo e os gates RC5 estao prontos.

## Endpoint usado

O AIOS chama:

```txt
POST https://api.openai.com/v1/responses
```

O endpoint e a API key ficam apenas no backend/processo seguro.

## Modelo

Por padrao:

```txt
OPENAI_MODEL=gpt-5.2-codex
```

Pode ser alterado antes de iniciar o backend:

```powershell
$env:OPENAI_MODEL = "gpt-5.2-codex"
$env:OPENAI_MAX_OUTPUT_TOKENS = "800"
$env:OPENAI_REASONING_EFFORT = "medium"
```

## Como iniciar com OpenAI API

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

$key = Read-Host "OpenAI API key oficial" -AsSecureString

.\scripts\rc5-start-openai-api-sandbox.ps1 `
  -OpenAIApiKey $key `
  -BaseUrl "https://api.openai.com/v1" `
  -SandboxEnvironmentId "aios-rc5-openai-api-sandbox" `
  -SecretStore "vault" `
  -ConfirmExternalSecretStore
```

## Como validar chamada real

Depois do backend reiniciado com a API key:

```powershell
.\scripts\rc6-validate-openai-runtime.ps1
```

Esse script faz uma chamada real curta ao modelo, registra evento `codex.runtime.completed`, atualiza job e grava relatorio em:

```txt
release/RC6_OPENAI_RUNTIME_REPORT.md
```

## Seguranca

- API key nao aparece no frontend.
- API key nao e gravada no ZIP.
- API key nao e impressa nos scripts.
- O output e registrado no Workbench.
- Uso/custo e capturado apenas como flag interna `usageCaptured`, sem contador de tokens na UX.
