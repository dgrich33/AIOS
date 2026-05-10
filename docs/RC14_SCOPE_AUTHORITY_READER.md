# AIOS Codex Unlimited RC14 - Scope Authority Reader

## Objetivo

A RC14 adiciona um sistema de leitura de escopo para o AIOS Codex Unlimited.

Ele verifica, em ordem:

1. `license.cert`;
2. `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`;
3. `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`;
4. `docs/CONTRACT_AUTHORITY.lock.json`;
5. evidencia textual de assinatura registrada nos documentos.

## Endpoint

```txt
GET /scope/authority
```

Resposta principal:

```json
{
  "phase": "RC14_SCOPE_AUTHORITY_READER",
  "scopeReady": true,
  "lockState": "unlocked_for_aios_codex_unlimited_scope",
  "runtimeBinding": "service_token_vault_kms_or_secure_runtime_bridge",
  "secretsExposed": false
}
```

## Script

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\scope-authority.ps1 -Json -WriteReport
```

Relatorio:

```txt
release/RC14_SCOPE_AUTHORITY_REPORT.md
```

## MCP

Tool adicionada:

```txt
aios.scope.authority
```

## Frontend

O Workbench mostra o painel:

```txt
Scope Authority RC14
```

Ele exibe precedencia, lock contratual, evidencia textual de assinatura e binding tecnico.

## Seguranca

Este leitor nao imprime segredos, service tokens, API keys, payloads privados ou conteudo completo dos documentos. Ele retorna hashes, flags de verificacao e caminhos necessarios para auditoria.

