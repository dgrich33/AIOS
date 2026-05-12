# RC31 - Private Community Runtime

## Objetivo

Expandir o `community_wrapper_runtime` para funcionar com duas fontes locais:

1. variaveis de ambiente do PowerShell;
2. arquivo privado `.env.local.private`, ignorado pelo Git e removido do ZIP.

Esse modo permite testar um runtime real de wrapper/gateway autorizado na maquina do desenvolvedor sem colocar endpoint, token, `auth.json` ou API key dentro do codigo do repositorio.

## Arquivo privado local

Crie o arquivo abaixo apenas na sua maquina:

```text
C:\AIOS\aios-codex-unlimited-enterprise-v2\.env.local.private
```

Use o modelo:

```text
.env.local.private.example
```

Conteudo minimo:

```env
AIOS_ENV=local_developer
AIOS_CHAT_PROVIDER=community_wrapper_runtime
AIOS_ALLOW_COMMUNITY_RUNTIME=true
AIOS_COMMUNITY_RUNTIME_BASE_URL=http://127.0.0.1:11434/v1
AIOS_COMMUNITY_RUNTIME_MODEL_ID=gpt-oss:20b
AIOS_COMMUNITY_RUNTIME_API_KEY=opcional-se-o-wrapper-exigir
```

O backend so carrega esse arquivo quando o modo declarado for:

- `local_developer`
- `presentation`

Em modo `production` ou `prod`, o arquivo privado nao e carregado.

## Endpoints novos

```text
GET /runtime/community-wrapper/status
POST /runtime/community-wrapper/validate
```

O status retorna apenas informacoes redigidas:

- `baseUrlRedacted`: endpoint sem usuario/senha e com path sensivel reduzido
- `modelId`
- `supportedModelProfiles`: inclui `gpt-oss-20b`
- `providerModelAliases`: inclui `openai/gpt-oss-20b` e `gpt-oss:20b`
- `credentialPresent`: booleano
- `missingRequirements`
- `secretsExposed=false`

O token nunca e retornado.

## Validacao

Validacao sem smoke real:

```powershell
$login = Invoke-RestMethod `
  -Uri http://127.0.0.1:8010/auth/login `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"email":"admin@aios.local","password":"AiosAdmin123!"}'

Invoke-RestMethod `
  -Uri http://127.0.0.1:8010/runtime/community-wrapper/status `
  -Headers @{ Authorization = "Bearer $($login.accessToken)" }
```

Smoke real, usando o wrapper configurado:

```powershell
$login = Invoke-RestMethod `
  -Uri http://127.0.0.1:8010/auth/login `
  -Method Post `
  -ContentType 'application/json' `
  -Body '{"email":"admin@aios.local","password":"AiosAdmin123!"}'

Invoke-RestMethod `
  -Uri http://127.0.0.1:8010/runtime/community-wrapper/validate `
  -Method Post `
  -ContentType 'application/json' `
  -Headers @{ Authorization = "Bearer $($login.accessToken)" } `
  -Body '{"runSmokeTest":true,"prompt":"Responda apenas OK.","timeoutSeconds":20}'
```

## UI

O Workbench mostra o card `RC31 Private Community Runtime` ao lado do Runtime Broker:

- status live/not-live;
- endpoint redigido;
- modelo configurado;
- botao `Validar Wrapper`;
- botao `Smoke Test Vivo`.

## Garantias

- `.env.local.private` esta no `.gitignore`.
- `auth.json`, `.env`, `*.token`, `*.secret`, DBs e logs continuam fora do ZIP.
- A API nunca serializa o valor de `AIOS_COMMUNITY_RUNTIME_API_KEY`.
- O modo wrapper local pode ficar live, mas `officialProduction` continua reservado para binding oficial completo.

## GPT OSS 20B

O perfil `gpt-oss-20b` foi adicionado como modelo real self-hosted/private-runtime. Aliases operacionais:

- `gpt-oss:20b` para Ollama/OpenAI-compatible local server;
- `openai/gpt-oss-20b` para vLLM/Hugging Face/OpenAI-compatible private wrapper;
- `gpt-oss-20b` como identificador interno do AIOS.

Com Ollama, prepare o runtime antes de abrir a demo:

```powershell
ollama pull gpt-oss:20b
ollama run gpt-oss:20b
```
