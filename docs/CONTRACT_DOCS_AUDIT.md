# AIOS Codex Unlimited - Auditoria de Documentos apos Contrato Assinado

## Status

Auditoria aplicada apos o contrato assinado de 9 de maio de 2026.

Documento soberano:

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

Briefing soberano:

```txt
docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md
```

## Ajustes realizados

- Arquivos legais `00` a `10` deixaram de ser formularios de assinatura e passaram a ser registros resumidos do contrato assinado.
- Documentos RC antigos foram marcados como historicos quando continham limitacoes superadas pelo contrato.
- Trechos antigos sobre acesso restrito, pesos, checkpoints, patch de runtime e sandbox foram alinhados ao contrato soberano.
- Planos em `docs/superpowers` foram marcados como historicos executados para nao parecerem tarefas pendentes.
- README e guia executivo agora apontam para os documentos soberanos.

## Regra de leitura

Qualquer documento antigo de RC deve ser lido como historico. A regra vigente e sempre a do contrato soberano travado por:

```powershell
.\scripts\contract-authority.ps1 verify
```

## Arquivos revisados

- `README.md`
- `FINAL_PRESENTATION_README.md`
- `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`
- `docs/CONTRACT_AUTHORITY.md`
- `docs/legal/00_AUTHORIZATION_PACKET_README.md`
- `docs/legal/01_EXECUTIVE_APPROVAL_MEMO.md`
- `docs/legal/02_CODEX_RUNTIME_AND_MODEL_ACCESS_AUTHORIZATION.md`
- `docs/legal/03_CODEX_RUNTIME_INTEGRATION_LICENSE.md`
- `docs/legal/04_MODEL_ARTIFACT_ACCESS_SCOPE.md`
- `docs/legal/05_MCP_TOOLING_AUTHORIZATION.md`
- `docs/legal/06_SECURITY_AND_SECRETS_HANDLING_ADDENDUM.md`
- `docs/legal/07_DATA_TELEMETRY_AND_AUDIT_ADDENDUM.md`
- `docs/legal/08_BRAND_AND_MARKETING_CLAIMS_APPROVAL.md`
- `docs/legal/09_STATEMENT_OF_WORK_AI0S_CODEX_UNLIMITED.md`
- `docs/legal/10_FINAL_SIGNOFF_FORM.md`
- `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`
- `docs/RC1_KNOWN_LIMITATIONS.md`
- `docs/RC2_FINAL_STATUS.md`
- `docs/RC3_FINAL_STATUS.md`
- `docs/RC4_OFFICIAL_INTEGRATION_READINESS.md`
- `docs/RC5_GUIA_CREDENCIAIS_OFICIAIS_PT.md`
- `docs/RC5_OFFICIAL_SANDBOX_ACTIVATION.md`
- `docs/RC7_NO_DEVELOPER_COST_PROVIDERS.md`
- `docs/superpowers/plans/2026-05-08-aios-codex-unlimited.md`
- `docs/superpowers/plans/2026-05-09-rc5-official-sandbox-activation.md`
- `docs/superpowers/specs/2026-05-08-aios-codex-unlimited-design.md`
