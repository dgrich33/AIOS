# AIOS Codex Unlimited - Seguranca e Segredos

## Status

Addendum consolidado pelo contrato assinado.

## Regras vigentes

- Guardrails atuais do AIOS mantidos como baseline.
- Policy pack obrigatorio da OpenAI.
- Gate de revisao de seguranca antes da alpha.
- Red-team review antes de producao.
- Vault/KMS obrigatorio para credenciais.
- Credenciais proibidas em frontend, logs, ZIP publico ou repositorio.
- Rotacao de token a cada 90 dias ou imediata em incidente.
- Revogacao centralizada pela OpenAI/Codex.

## Guardrails registrados

- `auth.json` nao deve ser usado para liberar Unlimited por bypass.
- Multiplas contas nao devem ser usadas para evasao de controle.
- Patch de runtime foi registrado como aprovado nas condicoes do contrato.
- Teste restrito em sandbox foi aprovado com dados reais autorizados.
- Excecoes de seguranca ficam restritas a sandbox isolado, pedido, logs e signoff de seguranca.

## Fonte soberana

`docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`

