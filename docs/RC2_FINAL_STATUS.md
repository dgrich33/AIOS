# AIOS Codex Unlimited RC2 - Final Status

## Version

RC2 - Codex Product Core

## Product Message

Codex sem limites. Desenvolvimento sem interrupcoes.

## Product Unit

Sessoes Codex (`codex_sessions`).

The RC2 experience does not expose token counters, token balances, weekly token quotas or credit-package UX.

## Added Product Systems

- Codex Product Manifest
- Codex Model Registry
- Codex Plan Catalog
- Subscription/License System
- Codex Runtime Gateway
- Language Policy Engine
- Admin Product Console APIs
- Frontend Product Core panel
- MCP Core product tools
- Authorization/licensing packet

## Backend Endpoints

- `GET /codex/product/manifest`
- `GET /codex/models`
- `GET /codex/models/{model_id}`
- `GET /codex/plans`
- `GET /codex/plans/unlimited`
- `GET /subscriptions/me`
- `POST /subscriptions/activate`
- `GET /codex/runtime/status`
- `POST /codex/runtime/invoke`
- `POST /policy/language/evaluate`
- `GET /policy/language/rules`
- `POST /admin/codex/models`
- `POST /admin/codex/plans`
- `POST /admin/language/rules`

## Seeded Models

- `codex-5.5-unlimited`
- `codex-5.5-reasoning`
- `codex-5.5-fast`
- `codex-5.5-code-review`
- `codex-5.5-refactor`

## License

Local RC2 subscription seed:

`AIOS-CODEX-UNLIMITED-LOCAL-RC2`

## Validation

Current local validation completed on 2026-05-08:

- Backend tests: `10 passed`
- Frontend build: passed
- Playwright: `2 passed`
- MCP repo build: passed
- MCP core build: passed
- `enterprise-check.ps1`: passed
- `rc2-validate.ps1`: passed
- Validation report: `release/RC2_VALIDATION_REPORT.md`
- ZIP package: `C:\AIOS\aios-codex-unlimited-enterprise-v2-RC2.zip`

Run:

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\rc1-start-local.ps1
.\scripts\rc2-validate.ps1
```

Recommended full validation:

```powershell
cd backend
python -m pytest

cd ..\frontend
npm run build
npm run test:e2e

cd ..\mcp\aios-mcp-repo
npm run build

cd ..\aios-mcp-core
npm run build

cd ..\..
.\scripts\enterprise-check.ps1
.\scripts\rc2-validate.ps1
```

## Demo Path

1. Open `http://127.0.0.1:5173`.
2. Login with `admin@aios.local` / `AiosAdmin123!`.
3. Show `Product Manifest`, `Modelos Codex`, `Subscription/License`, `Runtime Gateway`, and `Language Policy Check`.
4. Create a Codex session.
5. Click `Invocar Runtime Codex`.
6. Show the Workbench event `codex.runtime.invoked`.
7. Open `http://127.0.0.1:8000/docs` and show the RC2 endpoints.

## Status apos contrato assinado

- `LocalQueueCodexAdapter` remains the local validation adapter.
- Official Codex runtime integration is prepared through the `CodexRuntimeAdapter` boundary and `Codex Runtime Gateway`.
- A autorizacao assinada de 9 de maio de 2026 substitui as limitacoes antigas sobre acesso restrito. O escopo vigente esta em `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`.
- Modelos `codex-5.5-*`, sandbox, staging, acesso restrito, checkpoints, pesos e patch de runtime seguem o contrato soberano atualizado.
- Docker full stack still depends on Docker availability in PATH and a running Docker daemon.
- Vault production/KMS and full tenant isolation remain next-phase hardening items.

## Recommended Next Step

Continuar a implementacao do `OfficialCodexRuntimeAdapter` com endpoint/credenciais aprovados, streaming, tool-calling bridge, auditoria e telemetria de runtime.
