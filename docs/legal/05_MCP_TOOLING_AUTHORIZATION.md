# AIOS Codex Unlimited - Autorizacao MCP e Tooling

## Status

Autorizacao consolidada pelo contrato assinado. Este arquivo nao solicita assinatura.

## Ferramentas e eventos operacionais

MCP e tool calling fazem parte da integracao aprovada por:

- OfficialCodexRuntimeAdapter;
- Secure Runtime Bridge;
- service tokens;
- auditoria;
- policy engine;
- redaction;
- logs de acesso.

## Eventos obrigatorios relacionados

- `mcp.tool_call`
- `repo.patch_applied`
- `repo.build_started`
- `repo.build_passed`
- `repo.build_failed`
- `codex.runtime.invoked`
- `codex.secure_runtime.requested`
- `policy.guardrail.blocked`

## Controles

- Service tokens com escopo.
- Auditoria com requestId, actorId, tenantId, sessionId, modelId, toolName, action, status, timestamp, sourceIp, userAgent, errorCode e latencyMs.
- Redaction obrigatoria antes de export.

## Fonte soberana

`docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`

