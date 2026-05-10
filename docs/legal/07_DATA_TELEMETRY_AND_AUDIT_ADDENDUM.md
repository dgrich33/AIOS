# AIOS Codex Unlimited - Telemetria, Auditoria e Redaction

## Status

Schema aprovado no contrato assinado.

## Campos obrigatorios de telemetria do runtime

```txt
requestId, actorId, tenantId, sessionId, modelId, adapterId, operation, toolName, status, timestamp, latencyMs, retryCount, errorCode, policyDecision, priorityClass
```

## Campos proibidos em logs

```txt
prompts completos sensiveis, passwords, private keys, dados pessoais desnecessarios, payloads de arquivos privados sem redaction
```

## Retencao

- Eventos de sessao: 180 dias em enterprise/staging; configuravel por politica de cliente; minimo 30 dias para auditoria de alpha.
- Tool calls: 90 dias por padrao; 180 dias para eventos de seguranca, falha critica ou operacao restrita.

## Redaction

Redaction obrigatoria para secrets, credenciais, auth data, chaves, dados pessoais sensiveis, artefatos privados, codigo restrito e paths sensiveis antes de qualquer export.

## Fonte soberana

`docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`

