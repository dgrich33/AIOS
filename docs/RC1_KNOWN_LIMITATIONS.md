# AIOS Codex Unlimited RC1 - Status Historico

RC1 e uma fase historica anterior ao contrato assinado de 9 de maio de 2026. O estado vigente do projeto segue `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`.

## Codex Runtime

The current runtime implementation is:

```txt
LocalQueueCodexAdapter
```

The official runtime integration point is:

```txt
CodexRuntimeAdapter
```

Apos o contrato assinado de 9 de maio de 2026, acesso restrito, sandbox, checkpoints, pesos, codigo-fonte interno e patch de runtime seguem o documento soberano atualizado:

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

RC1 continua sendo uma fase historica local; a regra vigente do projeto esta no contrato soberano.

## Docker

Docker Full Stack depends on:

- Docker Desktop installed
- Docker daemon running
- Docker CLI available in PATH

If Docker is not available, RC1 local mode remains the official fallback.

## Vault

Vault is dev-mode when using Docker. Production Vault/KMS policies, storage, unseal and rotation are not part of RC1.

## Tenant Isolation

Tenant models and endpoints exist, but tenant isolation is not yet enforced across every entity and query.

## SSO

SSO/OIDC is mocked for local demonstration.

## Database

Local mode uses SQLite with WAL and busy timeout for demo stability. Docker mode uses Postgres.

## Compliance

RC1 includes redaction, RBAC, service tokens and policy boundaries, but it is not a final compliance-certified release.
