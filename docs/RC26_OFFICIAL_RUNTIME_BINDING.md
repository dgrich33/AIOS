# RC26 - Official Runtime Binding

## Objetivo

RC26 separa tres formas de runtime vivo sem misturar credenciais, simulacao e producao oficial:

- `codex_cli_local_developer`: runtime vivo local para desenvolvedor/apresentacao usando o Codex CLI autenticado na maquina.
- `openai_api_authorized`: runtime vivo via OpenAI Platform API key autorizada localmente.
- `official_codex_runtime`: runtime oficial de producao, liberado somente quando o binding oficial completo estiver presente.

O `controlled_simulator` continua disponivel para UX, testes e demonstracao controlada, mas nunca deve ser apresentado como runtime vivo.

## Credencial oficial nao e o mesmo que runtime oficial

Uma credencial autorizada pode habilitar um caminho local/API para teste real, mas isso nao transforma o ambiente em producao oficial. A producao oficial exige todos os itens abaixo:

- `AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT`
- `AIOS_OFFICIAL_CODEX_TENANT_ID`
- `AIOS_OFFICIAL_CODEX_SANDBOX_ENV_ID`
- `AIOS_OFFICIAL_CODEX_CREDENTIAL_REF`
- `AIOS_OFFICIAL_CODEX_VAULT_OR_KMS_REF`
- `AIOS_OFFICIAL_CODEX_LIVE_FLAG=true`

Sem todos esses itens, `official_codex_runtime` permanece bloqueado para producao. Isso evita falso positivo de runtime oficial.

## Usar OpenAI API key autorizada sem expor segredo

Configure apenas no ambiente local do processo:

```powershell
$env:OPENAI_API_KEY = "<sua key autorizada>"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = "gpt-5.2-codex"
```

Depois valide pelo Workbench em `Official Runtime Binding RC26` ou pela API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/runtime/official-binding/validate `
  -Method Post `
  -Headers @{ Authorization = "Bearer <token local de login AIOS>" } `
  -ContentType "application/json" `
  -Body '{"providerId":"openai_api_authorized"}'
```

Controles:

- a key nao e salva no banco;
- a key nao e retornada no frontend;
- a key nao deve ser escrita em `.env` versionado;
- logs e respostas passam por redaction.

Por padrao `officialProduction=false`. Use `AIOS_OFFICIAL_API_RUNTIME_APPROVED=true` somente se houver aprovacao formal para tratar esse caminho como aprovado em seu ambiente, ainda separado de `official_codex_runtime`.

## Usar Codex CLI local

Este e o caminho recomendado para demo local viva sem armazenar API key no AIOS:

```powershell
codex login
$env:AIOS_LOCAL_DEVELOPER_LIVE = "true"
$env:AIOS_ALLOW_CODEX_CLI_RUNTIME = "true"
$env:AIOS_ENV = "presentation"
```

O RC26 valida:

- `codex` disponivel no PATH;
- `codex --version`;
- `codex exec --json` com prompt seguro;
- `AIOS_ENV` em `local_developer` ou `presentation`;
- ambiente nao `production`.

O AIOS nao le, copia, exporta, imprime nem versiona `%CODEX_HOME%\auth.json`. O Codex CLI continua dono da autenticacao.

## Ativar official_codex_runtime

Configure os valores oficiais como referencias seguras:

```powershell
$env:AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT = "https://endpoint-oficial"
$env:AIOS_OFFICIAL_CODEX_TENANT_ID = "tenant-aprovado"
$env:AIOS_OFFICIAL_CODEX_SANDBOX_ENV_ID = "sandbox-aprovado"
$env:AIOS_OFFICIAL_CODEX_CREDENTIAL_REF = "vault://aios/codex/service-token"
$env:AIOS_OFFICIAL_CODEX_VAULT_OR_KMS_REF = "vault://aios/codex"
$env:AIOS_OFFICIAL_CODEX_LIVE_FLAG = "true"
```

O valor real do token deve ficar no Vault/KMS ou no mecanismo de segredo aprovado. O endpoint `/runtime/official-binding/status` mostra apenas referencias e estados redigidos.

## Endpoints RC26

- `GET /runtime/official-binding/status`
- `POST /runtime/official-binding/validate`
- `GET /runtime/codex-cli/status`
- `POST /runtime/codex-cli/exec`
- `POST /runtime/live/smoke-test`

Smoke tests reais exigem `approvalRequestId` aprovado no Approval Gate. Eles nao escrevem arquivos, nao fazem `git push`, nao acessam `.env` e nao leem `auth.json`.

## Demo local segura

1. Abra um PowerShell local.
2. Faça login no Codex CLI com `codex login`.
3. Configure:

```powershell
$env:AIOS_LOCAL_DEVELOPER_LIVE = "true"
$env:AIOS_ALLOW_CODEX_CLI_RUNTIME = "true"
$env:AIOS_ENV = "presentation"
```

4. Inicie o backend/frontend.
5. No Workbench, abra `Official Runtime Binding RC26`.
6. Clique em `Validate Local Credentials`.
7. Para smoke real, crie/aprove uma solicitacao do Approval Gate e depois clique em `Run Safe Live Smoke Test`.

## Validacao local

```powershell
.\scripts\rc26-official-runtime-binding.ps1
```

O script executa testes backend, build frontend, Playwright, builds MCP, higiene de segredo e status RC26 se a API estiver rodando. O smoke test vivo e opcional:

```powershell
$env:AIOS_RUN_LIVE_SMOKE = "true"
$env:AIOS_LIVE_SMOKE_PROVIDER = "codex_cli_local_developer"
$env:AIOS_LIVE_SMOKE_APPROVAL_ID = "<approval aprovado>"
.\scripts\rc26-official-runtime-binding.ps1
```

## Limites intencionais

- Nao faz push para GitHub.
- Nao gera ZIP.
- Nao transforma simulador em runtime vivo.
- Nao remove bloqueio de producao oficial sem binding oficial completo.
- Nao ignora secret hygiene.
