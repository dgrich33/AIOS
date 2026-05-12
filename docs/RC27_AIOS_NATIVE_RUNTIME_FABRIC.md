# RC27 — AIOS Native Runtime Fabric

## Objetivo

RC27 transforma o AIOS em uma camada propria de execucao Codex-like. O produto deixa de depender estruturalmente de um unico endpoint, modelo ou binding oficial para demonstrar valor.

## Narrativa correta

AIOS opera sessoes, agentes, governanca, snapshots, auditoria e runtimes plugaveis. O runtime oficial Codex/OpenAI continua sendo um provider premium quando provisionado, mas nao e a base obrigatoria do produto.

## Regra de status

- `canInvokeLiveRuntime=true` pode vir de qualquer runtime real validado.
- `officialProduction=true` fica reservado para `official_codex_runtime` com binding completo.
- `productionBlocked=true` pode coexistir com `canInvokeLiveRuntime=true`.
- `secretsExposed=false` e obrigatorio em todos os retornos.

## Providers RC27

| Provider | Funcao | Live por padrao |
|---|---|---|
| `controlled_simulator` | Demo controlada | Nao |
| `codex_cli_local_developer` | Codex CLI local quando validado | Nao |
| `openai_api_authorized` | API autorizada quando validada | Nao |
| `aios_native_runtime` | Runtime proprio do AIOS para sessoes/agentes/governanca | Sim |
| `aios_cloud_runtime` | Workspace cloud delegado | Nao |
| `self_hosted_runtime` | Inferencia propria/self-hosted | Nao |
| `official_codex_runtime` | Provider oficial premium | Somente com binding completo |

## Endpoints

### `GET /runtime/fabric/status`

Retorna:

- `runtimeFabricId`
- `components`
- `providers`
- `activeRuntimeProvider`
- `canInvokeLiveRuntime`
- `officialProduction`
- `productionBlocked`
- `missingRequirements`
- `secretsExposed=false`

### `GET /runtime/fabric/model-policy`

Retorna o registry de politicas de modelo. A partir desta revisao, `gpt-5.2-codex` e `gpt-4o` entram como `provider_validated` e `active=true` para testes do runtime AIOS, mantendo `secretsExposed=false` e sem alterar o status de producao oficial.

### `POST /runtime/fabric/chat`

Executa o chat do Workbench com um modelo ativo do registry. Por padrao usa `aios_native_runtime`; se `AIOS_CHAT_PROVIDER=codex_cli` estiver configurado no ambiente, tenta usar o Codex CLI local em modo read-only e sem ler `auth.json`.

## Como preparar demo local segura

1. Inicie backend e frontend normalmente.
2. Abra o Workbench.
3. Teste o painel `AIOS Chat`.
4. Confira o painel `RC27 AIOS Native Runtime Fabric`.
4. Apresente:
   - AIOS vivo via `aios_native_runtime`.
   - Producao oficial separada e bloqueada ate binding completo.
   - Providers plugaveis prontos para validacao.
   - Modelos `gpt-5.2-codex` e `gpt-4o` ativos no registry por validacao de provider.

## Seguranca

- Nao ler `auth.json`.
- Nao imprimir token, `.env`, API key ou segredo.
- Nao commitar segredos.
- Nao marcar producao oficial como ativa sem binding completo.
- Nao fazer push nem gerar pacote RC27 automaticamente.
