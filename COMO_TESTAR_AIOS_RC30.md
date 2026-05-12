# Como testar o AIOS RC30

Esta e a versao consolidada no caminho oficial:

```text
C:\AIOS\aios-codex-unlimited-enterprise-v2
```

O caminho em `C:\Users\dg71\Documents\Codex\...` foi apenas a area de trabalho/recap que o Codex abriu para esta conversa. O projeto de teste deve ser usado pelo `C:\AIOS`.

## Abrir o programa

De dois cliques em:

```text
AIOS_RC30_ABRIR_DEMO.bat
```

Ele abre:

```text
Frontend: http://127.0.0.1:5174
Backend:  http://127.0.0.1:8010/docs
```

Login:

```text
Email: admin@aios.local
Senha: AiosAdmin123!
```

## O que testar na interface

1. Entre no painel `AIOS Chat`.
2. Escolha `gpt-4o` ou `gpt-5.2-codex`.
3. Escolha um agente em `Agent Room`.
4. Envie uma mensagem curta.
5. Confirme que o chat responde usando o AIOS Native Runtime.
6. No painel `RC27 AIOS Native Runtime Fabric`, confirme:
   - `Links recebidos`: `112 de 112`
   - `community_wrapper_runtime`
   - `gpt-4o`
   - `gpt-5.2-codex`
   - `secretsExposed=false`
   - `Wrappers autorizados`

## Testar wrapper nao oficial como runtime real autorizado

Se voce tiver um wrapper/servidor autorizado pela sua equipe rodando localmente com API compativel com OpenAI, configure no PowerShell antes de abrir a demo:

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
$env:AIOS_CHAT_PROVIDER="community_wrapper_runtime"
$env:AIOS_ALLOW_COMMUNITY_RUNTIME="true"
$env:AIOS_COMMUNITY_RUNTIME_BASE_URL="http://127.0.0.1:9999"
$env:AIOS_COMMUNITY_RUNTIME_MODEL_ID="modelo-do-wrapper"
.\scripts\rc27-start-local-demo.ps1 -BackendPort 8010 -FrontendPort 5174
```

Se o wrapper exigir token, use variavel de ambiente local:

```powershell
$env:AIOS_COMMUNITY_RUNTIME_API_KEY="cole-o-token-apenas-neste-terminal"
```

Nao coloque esse valor no Git, no frontend, em zip publico ou em arquivo versionado.

## Parar

De dois cliques em:

```text
AIOS_RC30_PARAR_DEMO.bat
```

## Status honesto

- `aios_native_runtime`: funciona como demo local do AIOS.
- `community_wrapper_runtime`: funciona quando um wrapper real compativel esta configurado localmente.
- `official_codex_runtime`: continua sendo provider premium futuro quando houver binding oficial completo.
- `officialProduction`: nao e ligado por wrapper local; isso evita confundir demo local com producao oficial.
