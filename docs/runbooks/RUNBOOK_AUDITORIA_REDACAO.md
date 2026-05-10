# Runbook - Auditoria, Retencao e Redaction

## Objetivo

Garantir que auditoria e telemetria sejam uteis para operacao, seguranca e compliance sem expor segredos, dados pessoais desnecessarios ou artefatos restritos.

## Campos obrigatorios

```txt
requestId
actorId
tenantId
sessionId
modelId
adapterId
operation
toolName
status
timestamp
latencyMs
retryCount
errorCode
policyDecision
priorityClass
```

## Campos proibidos em logs

- API keys;
- service tokens;
- passwords;
- private keys;
- auth files;
- cookies;
- prompts completos sensiveis;
- conteudo de arquivos privados sem redaction;
- dados pessoais sem necessidade operacional;
- caminhos de artefatos restritos quando exportados publicamente.

## Retencao sugerida

| Evento | Retencao |
|---|---|
| Sessao | 180 dias em enterprise/staging; minimo 30 dias em alpha |
| Tool call | 90 dias |
| Evento de seguranca | 180 dias |
| Operacao restrita | 180 dias ou conforme politica oficial |
| Export redigido | Conforme contrato do tenant |

## Redaction obrigatoria

Executar redaction antes de:

- export bundle;
- PDF executivo;
- relatorio externo;
- envio ao suporte;
- telemetria fora da maquina;
- pacote de release.

## Eventos obrigatorios

```txt
session.created
session.status
codex.runtime.invoked
codex.secure_runtime.requested
mcp.tool_call
repo.patch_applied
repo.build_started
repo.build_passed
repo.build_failed
snapshot.created
handoff.created
service_token.created
restricted_access.requested
restricted_access.approved
restricted_access.denied
restricted_access.revoked
redaction.export.created
policy.guardrail.blocked
```

## Validacao

```powershell
.\scripts\enterprise-check.ps1
.\scripts\restricted-package-scan.ps1 -Path "."
```

O resultado esperado e ausencia de segredo bruto e artefato restrito no pacote publico.
