# AIOS Codex Unlimited RC15 - Scope Preflight

## Objetivo

A RC15 transforma a leitura de escopo da RC14 em uma decisao operacional antes de executar acoes sensiveis.

O preflight responde:

- o `license.cert` esta valido?
- os contratos protegidos conferem com o lock?
- ha evidencia textual de assinatura nos documentos?
- a operacao solicitada esta dentro do escopo aprovado?
- o modelo solicitado esta aprovado?
- o ambiente esta aprovado?
- ja existe binding tecnico para runtime live?
- a UX continua sem contador de token/quota?

## Endpoint

```txt
POST /scope/preflight
```

Payload:

```json
{
  "operation": "codex.runtime.invoke",
  "environment": "sandbox",
  "modelId": "codex-5.5-unlimited",
  "requiresLiveRuntime": true,
  "requiresRestrictedArtifacts": false,
  "reason": "validacao de runtime"
}
```

Resultado esperado quando o escopo esta correto:

```json
{
  "phase": "RC15_SCOPE_PREFLIGHT",
  "scopeReady": true,
  "scopeDecision": "allow",
  "executionState": "awaiting_technical_binding",
  "runtimeBinding": "service_token_vault_kms_or_secure_runtime_bridge",
  "userVisibleMeter": "none",
  "secretsExposed": false
}
```

`executionState` pode ser:

- `scope_authorized`
- `awaiting_technical_binding`
- `ready_for_live_runtime`
- `blocked`

## Script

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\scope-preflight.ps1 -RequiresLiveRuntime -WriteReport
```

Relatorio:

```txt
release/RC15_SCOPE_PREFLIGHT_REPORT.md
```

## MCP

Tool adicionada:

```txt
aios.scope.preflight
```

## Frontend

Painel:

```txt
Scope Preflight RC15
```

Botao:

```txt
Rodar Preflight de Escopo
```

## Regra

O preflight nao faz chamada externa de runtime e nao imprime segredos. Ele decide escopo e readiness antes da execucao.

