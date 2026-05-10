# AIOS Codex Unlimited RC9 - Limpeza de Documentos Contratuais

## Objetivo

Remover contradicoes documentais depois do contrato assinado de 9 de maio de 2026.

## Resultado

- Arquivos legais `00` a `10` foram convertidos em registros vigentes, sem campos de assinatura pendentes.
- Arquivos antigos com sufixo `TEMPLATE` foram renomeados.
- Status RC antigos foram ajustados para indicar que sao historicos quando tratam de escopo superado pelo contrato.
- README, guia executivo e planos historicos agora apontam para o contrato soberano.
- Criada auditoria central em `docs/CONTRACT_DOCS_AUDIT.md`.
- Criado script `scripts/contract-docs-audit.ps1`.

## Documento soberano

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

## Validacao

```powershell
.\scripts\contract-authority.ps1 verify
.\scripts\contract-docs-audit.ps1
```

## Observacao

As opcoes nao marcadas que ainda aparecem dentro do documento `11` fazem parte do registro assinado e nao sao tratadas como pendencias fora do contrato.

