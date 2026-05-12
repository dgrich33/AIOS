# Como testar o AIOS RC29

RC29 e a versao que registra todos os 112 links enviados no catalogo de pesquisa do AIOS.

## Abrir

De dois cliques em:

```text
AIOS_RC29_ABRIR_DEMO.bat
```

Esta versao usa portas alternativas para evitar processos antigos presos:

```text
Frontend: http://127.0.0.1:5174
Backend:  http://127.0.0.1:8010/docs
```

Login:

```text
Email: admin@aios.local
Senha: AiosAdmin123!
```

## O que testar

1. Abra o painel `AIOS Chat`.
2. Escolha `gpt-4o` ou `gpt-5.2-codex`.
3. Escolha um agente em `Agent Room`.
4. Envie uma mensagem.
5. Veja a resposta do AIOS Native Runtime.
6. No painel `RC27 AIOS Native Runtime Fabric`, confirme:
   - `Links recebidos`: `112 de 112`
   - `Ideias adotadas`
   - `Estudo futuro`
- `Adapters e SDKs`
- `Licao de seguranca`
- `community_wrapper_runtime` em `/runtime/fabric/status`

## Endpoints uteis

```text
http://127.0.0.1:8010/runtime/fabric/source-research
http://127.0.0.1:8010/runtime/fabric/agent-room/catalog
http://127.0.0.1:8010/runtime/fabric/model-policy
http://127.0.0.1:8010/docs
```

## Testar wrapper de comunidade como runtime real

Se voce tiver um wrapper/servidor autorizado rodando na sua maquina com API estilo OpenAI, configure:

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
$env:AIOS_CHAT_PROVIDER="community_wrapper_runtime"
$env:AIOS_ALLOW_COMMUNITY_RUNTIME="true"
$env:AIOS_COMMUNITY_RUNTIME_BASE_URL="http://127.0.0.1:9999"
$env:AIOS_COMMUNITY_RUNTIME_MODEL_ID="modelo-do-wrapper"
.\scripts\rc27-start-local-demo.ps1 -BackendPort 8010 -FrontendPort 5174
```

Depois use o painel `AIOS Chat`.

## Parar

De dois cliques em:

```text
AIOS_RC29_PARAR_DEMO.bat
```

Se algum processo antigo do Windows negar encerramento, continue usando o RC29 nas portas `5174/8010`.
