# RC24 - Approval Gate

## Objetivo

O RC24 adiciona um gate auditavel para acoes sensiveis do AIOS Workbench antes de qualquer execucao. Ele cobre comandos shell, patches, escrita em workspace, instalacao de dependencias, chamadas MCP sensiveis, patches de runtime e operacoes destrutivas.

## Contrato de seguranca

- O AIOS registra a solicitacao, risco, alvo, motivo e preview redigido.
- O preview passa por redaction antes de ser persistido ou exibido.
- A decisao humana pode aprovar, rejeitar ou cancelar a solicitacao.
- Mesmo apos aprovacao, o endpoint nao executa o comando automaticamente.
- `executionPerformed` sempre permanece `false` neste gate; a execucao real deve ocorrer por fluxo separado e auditado.
- Operacoes proibidas continuam bloqueadas: leitura de `auth.json`, copia de `auth.json` entre maquinas, exposicao de token ao frontend, commit de segredo e auto-execucao sem aprovacao humana.

## Endpoints

- `GET /approval-gate/policy` - retorna a politica RC24, operacoes sensiveis, operacoes bloqueadas e contador de pendencias.
- `POST /approval-gate/requests` - cria uma solicitacao pendente com risco calculado e preview redigido.
- `GET /approval-gate/requests` - lista as ultimas solicitacoes do usuario autenticado.
- `PATCH /approval-gate/requests/{id}/decision` - grava decisao humana sem executar a acao.

## Workbench

O painel `Approval Gate RC24` mostra:

- estado de auto-execucao bloqueada;
- obrigatoriedade de aprovacao humana;
- ultimas solicitacoes com risco e status;
- botoes de demo para criar, aprovar ou rejeitar uma solicitacao local.

## Validacao esperada

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2\backend
..\.venv\Scripts\python.exe -m pytest .\tests\test_api.py -q -k rc24
```

O teste garante que a solicitacao e a decisao sao auditadas, que segredos no preview sao redigidos e que nenhuma execucao automatica e realizada.
