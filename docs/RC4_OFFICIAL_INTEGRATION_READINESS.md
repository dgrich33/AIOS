# AIOS Codex Unlimited RC4 - Official Integration Readiness

## Objetivo

Transformar as decisoes de integracao oficial em uma camada verificavel no produto, sem alterar os documentos soberanos do contrato.

## Componentes

- `OfficialCodexRuntimeAdapter` com contrato de request, response, streaming, tool call e erro.
- Readiness endpoint para runtime oficial, credenciais, contrato travado e ambientes.
- Status de credenciais sem expor secrets.
- Registry de acesso restrito com solicitacao, aprovacao, expiracao, hash e auditoria.
- Painel frontend `Official Integration`.
- Tools MCP core para readiness, adapter contract, dry run e restricted access.
- Scripts `rc4-validate.ps1` e `rc4-package.ps1`.

## Endpoints

- `GET /official-integration/readiness`
- `GET /official-integration/adapter/contract`
- `GET /official-integration/credentials/status`
- `POST /official-integration/adapter/dry-run`
- `POST /restricted-access/requests`
- `GET /restricted-access/requests`
- `PATCH /restricted-access/requests/{request_id}/decision`

## Variaveis de ambiente do adapter

- `AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT`
- `AIOS_OFFICIAL_CODEX_SERVICE_TOKEN`
- `AIOS_OFFICIAL_CODEX_TENANT_ID`

Essas variaveis devem ser carregadas por ambiente seguro/Vault/KMS. Elas nao devem ir para frontend, logs, ZIP publico ou repositorio.

## Validacao

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\contract-authority.ps1 verify
.\scripts\rc1-start-local.ps1
.\scripts\rc4-validate.ps1
```

## Demo

1. Abrir `http://127.0.0.1:5173`.
2. Mostrar `Official Integration`.
3. Mostrar contrato travado.
4. Abrir Adapter Contract.
5. Executar Dry Run Oficial.
6. Registrar Patch Aprovado em Restricted Access.
7. Mostrar `http://127.0.0.1:8000/docs`.

## Proxima etapa

Com o contrato assinado, a etapa correta e configurar o ambiente seguro local/sandbox com credenciais aprovadas e rotear a invocacao pelo `OfficialCodexRuntimeAdapter`.
