# AIOS Codex Unlimited RC11 - Final Status

## Status

RC11 adiciona a camada de descoberta real de modelo e readiness do runtime.

## Adicionado

- `GET /codex/runtime/model-discovery`
- `OfficialCodexRuntimeAdapter.list_models()`
- tool MCP `aios.codex.runtime_model_discovery`
- botao `Descobrir Modelo` no painel Runtime Gateway
- `scripts/rc11-runtime-readiness.ps1`
- `scripts/rc11-package.ps1`
- `docs/RC11_RUNTIME_MODEL_DISCOVERY.md`

## Comportamento

Sem ambiente seguro completo, o endpoint nao chama rede externa e retorna:

```txt
blocked_until_secure_environment
```

Com ambiente seguro completo, o endpoint chama:

```txt
GET https://api.openai.com/v1/models
```

Depois escolhe o primeiro candidato disponivel nesta ordem:

```txt
gpt-5.5
gpt-5.5-pro
gpt-5.2-codex
gpt-5.1-codex
gpt-5.1-codex-max
gpt-5.1-codex-mini
gpt-5-codex
```

Se `OPENAI_MODEL` ja estiver disponivel na conta, ele e mantido como recomendado.

## Seguranca

- A API key nao e retornada.
- O frontend nao recebe segredo.
- A chamada de rede so ocorre depois dos gates de ambiente seguro.
- A unidade do produto continua sendo `codex_sessions`.
- Nao ha contador de tokens, saldo ou quota na experiencia do usuario.
- O pacote RC11 exclui `.env`, `auth.json`, bancos locais, `node_modules`, `.venv`, artefatos privados e extensoes de pesos/checkpoints.

## Validacao

Comandos principais:

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\contract-authority.ps1 verify
.\scripts\contract-docs-audit.ps1
.\scripts\rc11-runtime-readiness.ps1
.\scripts\rc11-package.ps1
```

Testes de codigo:

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2\backend
..\.venv\Scripts\python.exe -m pytest .\tests -q

Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2\frontend
npm run build
npm run test:e2e

Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2\mcp\aios-mcp-core
npm run build
```

## Proxima etapa

Quando houver credencial/quota/modelo confirmado, iniciar o backend com:

```powershell
$env:AIOS_OFFICIAL_SANDBOX_PROVIDER = "openai_api"
$env:OPENAI_API_KEY = "..."
$env:OPENAI_MODEL = "modelo-confirmado"
$env:AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID = "openai-api-sandbox-aios"
$env:AIOS_OFFICIAL_SANDBOX_SECRET_STORE = "vault"
$env:AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED = "true"
.\scripts\start.ps1 -Mode Local
.\scripts\rc11-runtime-readiness.ps1
```

Se a resposta for `BLOCKED_BY_OPENAI_QUOTA`, o codigo esta pronto e o bloqueio esta fora do projeto local.
