# AIOS Codex Unlimited - Escopo de Acesso Tecnico Restrito

## Status

Escopo registrado no contrato assinado.

## Itens restritos registrados

| Item Restrito | Necessario | Aprovado | Ambiente | Expiracao |
|---|---:|---:|---|---|
| Inspecao de binario protegido do runtime | Sim | Sim, com condicoes | Sandbox seguro / maquina aprovada | 90 dias, renovavel |
| Patching de compatibilidade do runtime | Sim | Sim, aprovado | Sandbox seguro / branch de integracao / maquina aprovada | 90 dias, renovavel |
| Acesso a codigo-fonte interno do runtime | Sim | Sim, com condicoes restritas | Sandbox seguro nesta maquina aprovada, limitado ao caminho C:\AIOS\aios-codex-unlimited-enterprise-v2 | 90 dias, renovavel somente por nova aprovacao |
| Metadados de artefatos de modelo | Sim | Sim | Sandbox/staging | 90 dias, renovavel |
| Checkpoints de modelo | sim | sim, aprovado | Sandbox/staging | 90 dias, renovavel |
| Pesos de modelo | sim | sim | Sandbox/staging | 90 dias, renovavel |
| Ferramentas internas de avaliacao/sandbox | Sim | Sim, aprovado | Sandbox/staging | 90 dias, renovavel |
| Testes com excecao de seguranca | Sim | Sim, aprovado | Sandbox isolado aprovado, com dados reais autorizados | 90 dias, renovavel |

## Controles obrigatorios

- Apenas pessoas nomeadas.
- Apenas maquina aprovada ou ambiente seguro.
- Sem empacotamento em release publico fora das regras do contrato soberano.
- Sem upload para armazenamento de terceiros.
- Rastreamento de hash e versao.
- Logs de acesso.
- Data de expiracao.
- Revogacao imediata pela OpenAI/Codex.

## Fonte soberana

`docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`
