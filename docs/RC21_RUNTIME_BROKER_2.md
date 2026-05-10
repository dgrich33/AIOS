# RC21 - Runtime Broker 2.0

## Objetivo

Criar um Runtime Broker model-adaptive e auditavel para o produto separado `AIOS Livre / Codex Unlimited`, com provider catalog completo, explicacao de decisao e bloqueio contra qualquer falso claim de runtime oficial vivo.

## Providers registrados

O catalogo RC21 expoe, em ordem de produto:

1. `official_codex_runtime`
2. `codex_delegated`
3. `aios_cloud_runtime`
4. `openai_api_authorized`
5. `puter_user_pays_browser`
6. `github_models_demo`
7. `ollama_local_cloud`
8. `vllm_self_hosted`
9. `tgi_self_hosted`
10. `llamafile_server`
11. `controlled_simulator`

## Regras de claim

- Somente `official_codex_runtime` pode declarar `canInvokeLiveRuntime: true`.
- `official_codex_runtime` so fica live quando o binding RC16/RC17 estiver ativo com endpoint, credencial, tenant quando exigido, sandbox environment id, Vault/KMS e live flag.
- `codex_delegated` pode representar Codex via auth delegada, mas nao altera `canInvokeLiveRuntime` do binding enterprise.
- `controlled_simulator` pode apoiar demo, auditoria e testes, mas nunca declara runtime live.
- Providers self-hosted/comerciais podem ser fallback ou demo, sem se apresentarem como runtime oficial Codex.

## Endpoints

- `GET /runtime/broker/providers`
  - retorna catalogo RC21 e politicas de seguranca.
- `GET /runtime/broker/status`
  - retorna disponibilidade por provider, provider recomendado, `liveRuntimeProvider` e `selection.reasonCode`.
- `GET /runtime/broker/explain?provider=...`
  - explica por que um provider pode ou nao declarar live runtime e se serve para demo sem chave.
- `POST /runtime/broker/invoke`
  - preserva o fluxo backend-invokable existente para `ollama_local_cloud`.

## Auditoria

`GET /runtime/broker/status` agora registra:

- `runtime_broker.status`
- `aios.runtime_broker.provider_selected`

O evento de selecao inclui `reasonCode`, `canInvokeLiveRuntime`, `liveRuntimeProvider` e `secretsExposed=false`.

## UI

O Workbench mostra `Runtime Broker RC21`, provider selecionado, explicacao de claim, estado de live enterprise e a lista completa de providers.

## Validacoes executadas

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2\backend
..\.venv\Scripts\python.exe -m pytest .\tests -q

cd C:\AIOS\aios-codex-unlimited-enterprise-v2\frontend
npm run build

cd C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\runtime-binding-status.ps1 -WriteReport
```

Resultados observados:

- Backend tests: 30 passed.
- Frontend build: OK.
- Runtime binding report: `bindingState=awaiting_secure_runtime_binding`, `canInvokeLiveRuntime=false`, `secretsExposed=false`.

## Observacao sobre Playwright

Durante a validacao interativa, o processo Playwright/Vite ficou preso no runner local antes de concluir a suite, mesmo em teste simples de login. O build TypeScript e os testes backend foram executados com sucesso. A suite Playwright deve ser reexecutada apos limpar processos de browser/runner do ambiente local.
