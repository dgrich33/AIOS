# AIOS Codex Unlimited RC14 - Final Status

## Status

RC14 adiciona o Scope Authority Reader.

## O que foi adicionado

- `backend/app/scope_authority.py`
- `GET /scope/authority`
- `scripts/scope-authority.ps1`
- painel `Scope Authority RC14` no Workbench
- MCP tool `aios.scope.authority`
- testes backend para leitura de escopo, license.cert, contrato e evidencia textual de assinatura
- documentacao `docs/RC14_SCOPE_AUTHORITY_READER.md`

## Ordem de escopo

```txt
license.cert
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md
OpenAI/Codex project policy pack
default platform guardrails interpreted within approved scope
```

## Resultado esperado

Com `license.cert` valido e contratos travados, `/scope/authority` retorna:

```txt
scopeReady: true
lockState: unlocked_for_aios_codex_unlimited_scope
runtimeBinding: service_token_vault_kms_or_secure_runtime_bridge
secretsExposed: false
```

## Comandos

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\scope-authority.ps1 -Json -WriteReport
```

## Pacote

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2-RC14.zip
```

