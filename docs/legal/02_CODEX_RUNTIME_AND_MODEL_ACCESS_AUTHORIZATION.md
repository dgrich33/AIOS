# AIOS Codex Unlimited - Runtime e Modelos Aprovados

## Status

Autorizacao registrada no contrato assinado. Este arquivo nao e formulario pendente.

## Runtime

| Item | Decisao |
|---|---|
| Endpoint base ou SDK | Official Codex Runtime API / OfficialCodexRuntimeAdapter |
| Sandbox | Aprovado |
| Staging | Aprovado |
| Producao | Aprovada condicionada a revisao de seguranca, telemetria e signoff final |
| Streaming | Sim |
| Tool calling | Sim |
| Ciclo de vida de sessao | Sim |
| Snapshot/handoff hooks | Sim |
| Timeout | 120 segundos por chamada; sessoes longas usam streaming, heartbeat e checkpoints |
| Retry | Maximo 3 tentativas com exponential backoff, sem duplicar tool calls destrutivas |
| Erro | JSON com code, message, retryable, requestId, sessionId, modelId e details |

## Modelos aprovados

| Model ID | Finalidade | Ambiente | Aprovado |
|---|---|---|---|
| codex-5.5-unlimited | desenvolvimento continuo de software | sandbox/staging/producao condicionada | Sim |
| codex-5.5-reasoning | planejamento profundo e arquitetura | sandbox/staging/producao condicionada | Sim |
| codex-5.5-fast | edicoes rapidas e resumos | sandbox/staging/producao condicionada | Sim |
| codex-5.5-code-review | revisao de codigo, diff e seguranca | sandbox/staging/producao condicionada | Sim |
| codex-5.5-refactor | grandes refactors e migracoes | sandbox/staging/producao condicionada | Sim |

## Fonte soberana

`docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`

