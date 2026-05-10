# AIOS Codex Unlimited RC10 - Guardrails Contratuais no Produto

## Objetivo

Alinhar o produto executavel com o contrato assinado, nao apenas os documentos.

## Implementado

- `GET /policy/integration/guardrails` agora separa:
  - operacoes permitidas;
  - operacoes bloqueadas por bypass/evasao;
  - operacoes condicionais aprovadas no contrato.
- Operacoes condicionais exigem `restrictedAccessRequestId` aprovado e ativo.
- `RestrictedAccessRequest` agora retorna `activeApproval` e `expired`.
- Novo log auditavel:
  - `POST /restricted-access/requests/{id}/access-log`
  - `GET /restricted-access/requests/{id}/access-log`
- Script de scan de pacote publico:
  - `scripts/restricted-package-scan.ps1`

## Operacoes condicionais

```txt
inspect_protected_runtime_binary
runtime_patch
internal_runtime_source_read
model_artifact_metadata_read
copy_model_checkpoints
copy_model_weights
internal_eval_sandbox_tool
security_exception_test
```

## Operacoes bloqueadas

```txt
alter_codex_auth_json
multi_account_limit_bypass
embed_private_codex_binaries
export_private_codex_artifacts
disable_public_build_safety
```

## Regra

O contrato permite acesso restrito sob controles. O produto agora representa isso como fluxo auditavel e condicional, em vez de deixar tudo como bloqueio absoluto antigo.

