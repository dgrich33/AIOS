# AIOS Codex Unlimited - Briefing de Reuniao (Atualizado: RC16 + RC17)

## Objetivo

Obter da equipe OpenAI/Codex um caminho tecnico concreto para levar o AIOS Codex Unlimited da validacao local RC16/RC17 para uma integracao oficial com runtime Codex, com `canInvokeLiveRuntime: true` e `bindingState: active`.

## Pedido Principal

O AIOS precisa de um contrato tecnico oficial de integracao contendo endpoint/base URL, service credential com escopos minimos, tenant, sandbox environment id, configuracao de Vault/KMS, live flag igual a true, modelos aprovados, comportamento do entitlement `aios_codex_unlimited`, contrato de streaming/tool calling, schema de telemetria/auditoria com redaction e regras de distribuicao Windows.

## Por Que Isso E Necessario - Estado Atual Real

- RC16 Runtime Binding Gate: implementado com endpoint real `GET /runtime/binding/status` e MCP tool `aios.runtime_binding.status`, sem simular credenciais ou segredos.
- RC17 Secure Runtime Binding Store: cofre local por DPAPI do Windows para salvar endpoint, service credential, tenant, sandbox environment id, Vault/KMS e live flag quando entregues oficialmente, sem gravar no repo, ZIP publico ou frontend.
- Resultado atual desta maquina: `scopeReady: true`, `bindingState: awaiting_secure_runtime_binding`, `provider: openai_codex`, `canInvokeLiveRuntime: false`, `secretsExposed: false`.
- Dados reais ainda nao encontrados nesta maquina: endpoint oficial, service credential, tenant ID, sandbox environment ID, Vault/KMS ativo e live flag.
- Evidencias consolidadas: backend tests 29 passed, frontend build OK, MCP core build OK, MCP repo build OK, Playwright 2 passed, enterprise check OK, contract authority OK, contract docs audit OK, DPAPI save/load test OK e package scan OK.
- Pacote RC17: `C:\AIOS\aios-codex-unlimited-enterprise-v2-RC17.zip`.
- SHA256 RC17: `B7B80E48A6B8217D4239D547D6AA3B70BB7F855277DE5C1F950A2AC219B6DFD5`.
- Ambientes locais: frontend `http://127.0.0.1:5173`; backend `http://127.0.0.1:8000/docs`.

## Posicionamento Recomendado

O RC16/RC17 nao inventa runtime, nao cria credencial falsa e nao deixa simulacao como real. O sistema aguarda e protege credenciais reais quando forem entregues oficialmente.

Usar:

- OfficialCodexRuntimeAdapter;
- Secure Runtime Bridge;
- service tokens com escopos minimos;
- SSO/OIDC e identidade enterprise;
- entitlement aprovado `aios_codex_unlimited`;
- telemetria e auditoria com redaction obrigatoria;
- Vault/KMS obrigatorio;
- rotacao de credenciais a cada 90 dias;
- revogacao centralizada imediata;
- hash/version tracking;
- gates de sandbox e staging;
- distribuicao Windows assinada;
- exclusao de artefatos restritos de qualquer pacote publico.

## Decisoes Ja Alinhadas

- Caminho de runtime: Official Codex Runtime API / OfficialCodexRuntimeAdapter + Secure Runtime Bridge.
- Ambientes: sandbox e staging aprovados; producao condicionada a revisao de seguranca, telemetria, assinatura e signoff final.
- Streaming, tool calling, ciclo de vida de sessao e hooks de snapshot/handoff: aprovados.
- Modelos aprovados solicitados: `codex-5.5-unlimited`, `codex-5.5-reasoning`, `codex-5.5-fast`, `codex-5.5-code-review`, `codex-5.5-refactor`.
- Confirmacao tecnica necessaria: acesso ao `gpt-5.2-codex` ou variante aprovada para o projeto/credencial autorizado.
- Entitlement: `aios_codex_unlimited`.
- Prioridade: `premium_unlimited`.
- Unidade do produto: Sessoes Codex.
- Experiencia do usuario: sem contador de tokens, sem saldo e sem quota semanal; mostrar apenas saude, sessao e atividade.
- Politicas de abuso/degradacao: obrigatorias e sem expor quota ao usuario.
- Credenciais: emitidas pela OpenAI/Codex, armazenadas em Vault/KMS, com rotacao, revogacao e auditoria.
- Escopos obrigatorios: `runtime.invoke`, `runtime.stream`, `model.read`, `session.manage`, `tool.call`, `telemetry.write`, `audit.write`, `entitlement.read`.
- Distribuicao Windows: ZIP portatil para beta/RC; EXE assinado, MSI e launcher OpenAI aprovado para release oficial; auto-update e canal aprovado.
- Runtime privado, credenciais internas e artefatos restritos nao entram em ZIP, EXE, MSI, repo publico ou build publico de usuario final.
- Acesso restrito, quando usado, exige pessoas nomeadas, maquina/caminho aprovado, prazo inicial de 90 dias renovavel, auditoria completa, hash/version tracking, proibicao de upload externo e revogacao imediata.
- Inicio de integracao aprovado para 9 de maio de 2026.

## Checklist de Decisao Para Ativar Runtime Vivo

1. Credenciais e ambientes reais fornecidos oficialmente:
   - `OPENAI_BASE_URL` ou `AIOS_OFFICIAL_CODEX_RUNTIME_ENDPOINT`;
   - `OPENAI_API_KEY` ou `AIOS_OFFICIAL_CODEX_SERVICE_TOKEN`;
   - `OPENAI_PROJECT_ID` ou `OPENAI_ORG_ID`;
   - `AIOS_OFFICIAL_CODEX_TENANT_ID`;
   - `AIOS_OFFICIAL_SANDBOX_ENVIRONMENT_ID`;
   - Vault/KMS configurado;
   - `AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED=true`.
2. Validacao local pos-injecao:
   - `runtime-binding-save-local.ps1`;
   - `start.ps1 -Mode Local`;
   - `runtime-binding-status.ps1 -WriteReport`;
   - resultado esperado: `scopeReady: true`, `bindingState: active`, `canInvokeLiveRuntime: true`, `secretsExposed: false`.
3. Modelo aprovado habilitado:
   - confirmar acesso ao `gpt-5.2-codex` ou variante aprovada para o projeto/credencial autorizado.
4. Billing e limites:
   - creditos/billing aprovados, spend limits e rate limits por sandbox, staging e producao.
5. Telemetria, auditoria e redaction:
   - campos e eventos obrigatorios funcionando;
   - redaction validada em logs, exports e PDFs;
   - destino de auditoria definido;
   - runbook de incidente anexado.
6. Distribuicao:
   - pacotes assinados, auto-update, rollback e canal oficial/aprovado.
7. Seguranca:
   - red-team review antes de producao;
   - gates de sandbox/staging;
   - acesso restrito documentado e aprovado quando aplicavel.

## Proximo Passo Acionavel

Enviar este briefing e `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md` pelos canais oficiais da OpenAI/Codex, incluindo parcerias, engenharia Codex, seguranca/compliance, partner manager ou support portal.

Agendar kick-off tecnico, seguranca e compliance antes de qualquer go-production.

Enquanto os dados reais nao forem entregues oficialmente, operar somente em sandbox/staging autorizado, com dados sinteticos ou autorizados, rodando readiness/binding e validando auditoria e redaction.

## Documento Principal

Usar este documento na reuniao:

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

## Frase de Fechamento

O AIOS Codex Unlimited ja possui o gate tecnico local para receber runtime real com seguranca. A pendencia atual nao e de arquitetura: e o provisionamento oficial de endpoint, credencial, tenant, sandbox, Vault/KMS e live flag para transformar `awaiting_secure_runtime_binding` em `active`.
