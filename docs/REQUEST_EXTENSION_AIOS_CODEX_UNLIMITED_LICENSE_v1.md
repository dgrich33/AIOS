# AIOS Codex Unlimited - Pedido de Extensao de Licenca e Runtime

## Status do documento

Documento operacional para submissao interna. Nao substitui o contrato soberano do projeto nem declara credenciais emitidas. Campos de assinatura e decisao devem ser registrados no sistema oficial da organizacao.

## Identificacao do projeto

| Item | Valor |
|---|---|
| Nome do projeto | AIOS Codex Unlimited |
| ID interno | proj_aios_unlimited_v2_enterprise |
| Branch / repo esperado | git.corp.openai.com/aios/aios-codex-unlimited-enterprise-v2 |
| Caminho local autorizado | C:\AIOS\aios-codex-unlimited-enterprise-v2 |
| Versao atual | RC13 |
| Ponto de contato tecnico | AIOS Engineering / Codex Next-Gen Team |

## Objetivo da solicitacao

Solicitar extensao de licenca e permissao de runtime para permitir a integracao oficial do AIOS Codex Unlimited com modelos Codex aprovados, service tokens, entitlement de sessoes e ambiente enterprise local seguro.

## License.cert

`license.cert` e a prova local primaria de autorizacao da RC13 no caminho:

```txt
C:\AIOS\aios-codex-unlimited-enterprise-v2\license.cert
```

Hash SHA-256 autorizado:

```txt
2dab9a98164a84d5b596e1e1e2e51855467c5e79dccad42d370467ce6ce88b7f
```

Quando validado, ele ativa no AIOS:

- entitlement `aios_codex_unlimited`;
- classe `premium_unlimited`;
- escopo `aios_codex_unlimited_enterprise_runtime`;
- autorizacao para OfficialCodexRuntimeAdapter;
- autorizacao para service tokens persistentes;
- autorizacao controlada para artefatos de runtime/checkpoints no caminho aprovado.
- estado de cadeado desbloqueado para o escopo exclusivo do AIOS Codex Unlimited.

Binding tecnico:

```txt
service_token_vault_kms_or_secure_runtime_bridge
```

Ordem operacional: `license.cert` validado -> documentos contratuais principais -> policy pack OpenAI/Codex do projeto -> guardrails padrao adaptados ao escopo aprovado.

## Acesso solicitado

| Item | Valor solicitado |
|---|---|
| Entitlement ID | aios_codex_unlimited |
| Classe de prioridade | premium_unlimited |
| Service Token TTL | 90 dias, com rotacao e revogacao |
| Ambientes | sandbox -> staging -> producao condicionada |
| Modelos | codex-5.5-unlimited, codex-5.5-reasoning, codex-5.5-fast, codex-5.5-code-review, codex-5.5-refactor |
| Escopos OAuth | runtime.invoke, runtime.stream, model.read, session.manage, tool.call, telemetry.write, audit.write, entitlement.read |
| Vault/KMS | vault.corp.openai.com/v1/secret/aios/codex-unlimited |
| Politica de abuso | allow, shape, degrade, review sem exibir quota ao usuario |

## Justificativa tecnica

O AIOS Codex Unlimited valida uma experiencia premium baseada em sessoes Codex, com Workbench, snapshots, handoff, MCP, Runtime Broker, Secure Runtime Bridge, Policy Engine, Audit, Redaction e Context Engine.

O produto nao deve usar contador de tokens, saldo ou quota semanal como experiencia de usuario. A unidade operacional e `codex_sessions`.

## Controles obrigatorios

- credenciais apenas em Vault/KMS;
- service tokens com escopo e revogacao;
- logs de auditoria com requestId, sessionId, actorId, modelId, toolName, status e latencyMs;
- redaction antes de export;
- hash/version tracking de artefatos locais;
- ambiente sandbox isolado antes de staging/producao;
- nenhum binario privado, peso, checkpoint ou credencial no pacote de usuario final.

## Pedido especifico

1. Estender permissoes de licenca para `proj_aios_unlimited_v2_enterprise`.
2. Liberar modelos Codex aprovados via OfficialCodexRuntimeAdapter.
3. Emitir service tokens persistentes com rotacao de 90 dias.
4. Criar entitlement `aios_codex_unlimited` com classe `premium_unlimited`.
5. Aplicar shaping/degrade sem medidor visivel de quota.
6. Agendar revisao final de seguranca para alpha controlada.

## Decisao

| Campo | Valor |
|---|---|
| Decisao | Pendente de registro oficial |
| Aprovador |  |
| Cargo |  |
| Assinatura |  |
| Data |  |
