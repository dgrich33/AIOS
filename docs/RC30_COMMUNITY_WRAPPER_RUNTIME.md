# RC30 - Community Wrapper Runtime

## Objetivo

Permitir que o AIOS use um runtime real de comunidade/wrapper quando ele for explicitamente configurado pelo desenvolvedor local ou pela equipe autorizada.

Esse modo existe para inovar com todos os projetos enviados pela equipe, inclusive wrappers e gateways nao oficiais, sem colocar endpoint publico, token, `auth.json` ou credencial no repositorio.

## Provider

```text
providerId: community_wrapper_runtime
runtimeKind: openai_compatible_community_runtime
category: community_runtime_adapter
officialProduction: false
```

## Variaveis locais

Configure apenas na sua maquina, em `.env.local.private` ou no ambiente do PowerShell:

```powershell
$env:AIOS_CHAT_PROVIDER="community_wrapper_runtime"
$env:AIOS_ALLOW_COMMUNITY_RUNTIME="true"
$env:AIOS_COMMUNITY_RUNTIME_BASE_URL="http://127.0.0.1:9999"
$env:AIOS_COMMUNITY_RUNTIME_MODEL_ID="modelo-do-wrapper"
$env:AIOS_COMMUNITY_RUNTIME_API_KEY="opcional-se-o-wrapper-exigir"
```

O backend aceita base URL em formato compatível com OpenAI:

```text
http://host:porta
http://host:porta/v1
http://host:porta/v1/chat/completions
```

## Como funciona

Quando `AIOS_CHAT_PROVIDER=community_wrapper_runtime`, o endpoint:

```text
POST /runtime/fabric/chat
```

encaminha a conversa para:

```text
{AIOS_COMMUNITY_RUNTIME_BASE_URL}/v1/chat/completions
```

com payload:

```json
{
  "model": "AIOS_COMMUNITY_RUNTIME_MODEL_ID",
  "messages": [],
  "stream": false,
  "temperature": 0.2
}
```

## Regras

- Nada e hardcoded.
- Nenhum token e retornado pela API.
- Nenhuma credencial entra no frontend.
- Nenhuma credencial entra no ZIP.
- Wrappers enviados pela equipe podem ser usados quando expuserem endpoint local/privado compativel e autorizado.
- O modo e local/developer e nao marca `officialProduction=true`.
- O status pode marcar `canInvokeLiveRuntime=true` quando as variaveis locais estao completas.

## Teste rapido

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
$env:AIOS_CHAT_PROVIDER="community_wrapper_runtime"
$env:AIOS_ALLOW_COMMUNITY_RUNTIME="true"
$env:AIOS_COMMUNITY_RUNTIME_BASE_URL="http://127.0.0.1:9999"
$env:AIOS_COMMUNITY_RUNTIME_MODEL_ID="modelo-do-wrapper"
.\scripts\rc27-start-local-demo.ps1 -BackendPort 8010 -FrontendPort 5174
```

Abra:

```text
http://127.0.0.1:5174
```

Se o wrapper estiver ativo e responder no formato esperado, o chat do AIOS usara esse runtime real.
