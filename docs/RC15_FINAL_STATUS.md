# AIOS Codex Unlimited RC15 - Final Status

## Status

RC15 adiciona o Scope Preflight operacional.

## O que foi adicionado

- `POST /scope/preflight`
- `ScopePreflightRequest`
- `scripts/scope-preflight.ps1`
- MCP tool `aios.scope.preflight`
- painel `Scope Preflight RC15`
- testes backend para allow/block
- Playwright cobrindo o painel e botao
- documentacao `docs/RC15_SCOPE_PREFLIGHT.md`

## Decisao operacional

O preflight retorna:

```txt
scope decision = allow | block
execution state = scope_authorized | awaiting_technical_binding | ready_for_live_runtime | blocked
```

## Garantias

- usa `license.cert` primeiro;
- valida lock dos contratos;
- valida evidencia textual de assinatura;
- valida modelo/operacao/ambiente;
- nao faz chamada externa;
- nao expõe segredos;
- nao cria contador de tokens.

## Comandos

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\scope-preflight.ps1 -RequiresLiveRuntime -WriteReport
```

## Pacote

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2-RC15.zip
```
