# RC26 - Private Runtime Demo

## Objetivo

Este modo prepara uma demonstracao privada local para o desenvolvedor oficial do AIOS. Ele permite runtime vivo local/API quando validado, mas mantem a separacao honesta:

- `controlled_simulator`: demo sem runtime vivo.
- `codex_cli_local_developer`: runtime vivo local via Codex CLI autenticado pelo proprio Codex.
- `openai_api_authorized`: runtime vivo via OpenAI API key autorizada no ambiente local.
- `official_codex_runtime`: producao oficial somente com binding oficial completo.

## Arquivo privado local

Crie na raiz do projeto:

```powershell
notepad .env.local.private
```

Conteudo sugerido:

```dotenv
AIOS_ENV=local_developer
AIOS_PRESENTATION_MODE=true
AIOS_LOCAL_ONLY=true
AIOS_ALLOW_GITHUB_PUSH=false
AIOS_PUBLIC_RELEASE=false
AIOS_DATABASE_URL=sqlite:///./aios_local_private.db
AIOS_RUNTIME_PROVIDER=auto
AIOS_ALLOW_CODEX_CLI_RUNTIME=true
AIOS_ALLOW_OPENAI_API_RUNTIME=true
AIOS_REQUIRE_APPROVAL_GATE=true
AIOS_SECRET_STORAGE=env_or_os_keychain
AIOS_SECRETS_EXPOSED=false
AIOS_LOCAL_DEVELOPER_LIVE=true
```

O backend carrega `.env.local.private` somente em `local_developer` ou `presentation`. Em `production`, o arquivo e ignorado.

## Segredos

Regras do modo privado:

- `auth.json` nao e lido pelo AIOS.
- `auth.json` nao e copiado.
- `auth.json` nao e versionado.
- API key nao deve entrar em arquivo versionado.
- Credencial nao e gravada em texto puro no backend.
- Secret hygiene continua obrigatorio.

Se usar OpenAI API local:

```powershell
$env:OPENAI_API_KEY = "<key autorizada>"
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"
$env:OPENAI_MODEL = "gpt-5.2-codex"
```

Se usar Codex CLI:

```powershell
codex login
$env:AIOS_LOCAL_DEVELOPER_LIVE = "true"
$env:AIOS_ALLOW_CODEX_CLI_RUNTIME = "true"
$env:AIOS_ENV = "presentation"
```

## Demo local

```powershell
.\scripts\start.ps1 -Mode Local
```

Abra:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000/docs`

No Workbench, use o painel `RC26 Private Runtime Demo`:

1. `Validate Private Runtime`
2. `Create Approval`
3. Aprovar no `Approval Gate`
4. `Run Safe Live Smoke Test`

## Verificacao

```powershell
.\scripts\rc26-private-runtime-demo-check.ps1
```

Smoke test opcional:

```powershell
$env:AIOS_RUN_LIVE_SMOKE = "true"
$env:AIOS_LIVE_SMOKE_PROVIDER = "codex_cli_local_developer"
$env:AIOS_LIVE_SMOKE_APPROVAL_ID = "<approval aprovado>"
.\scripts\rc26-private-runtime-demo-check.ps1
```

## Modelos

O AIOS registra `gpt-5.2-codex` como perfil de runtime documentado e dependente de provider/model discovery.

`gpt-4o` fica como perfil legado desabilitado por padrao. Ele so pode ser tratado como ativo quando o provider selecionado o retornar em model discovery ou quando houver configuracao explicita aprovada. O AIOS nao deve prometer retorno oficial de modelo sem evidencia do provider.

## Limites

Este modo nao faz push, nao gera pacote publico, nao remove bloqueio de producao oficial e nao substitui binding real de producao.
