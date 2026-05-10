# AIOS Livre / Codex Unlimited - Blueprint Tecnico

## Visao

O AIOS Livre / Codex Unlimited sera um app Windows/desktop separado, construido sobre a base atual do AIOS Codex Unlimited, mas com camada de produto clara:

```txt
Workbench Premium -> Unlimited Session Engine -> Runtime Broker -> Providers
                       |                         |
                       |                         +-> Official runtime / Codex delegated / AIOS cloud / Self-hosted / No-Key demo / Simulado controlado
                       |
                       +-> Account-Linked Entitlement -> Agent Room -> Approval Gate -> Repo Memory -> Audit/Redaction
```

## Componentes

### 1. AIOS Desktop Shell

Responsabilidade:

- entregar experiencia Windows;
- abrir Workbench;
- gerenciar estado visual;
- mostrar sessoes, agentes, diffs, builds e auditoria;
- nao armazenar segredo no frontend.

Entrada:

- usuario autenticado;
- projeto local selecionado;
- sessao Codex.

Saida:

- chamadas para backend local;
- eventos de UI;
- relatorios redigidos.

### 2. Workbench Premium

Responsabilidade:

- linha do tempo de sessao;
- status de build e testes;
- arquivos alterados;
- diff visual;
- snapshots;
- handoff;
- eventos MCP/tool;
- risk score;
- relatorio executivo redigido.

Regra:

```txt
Mostrar atividade e saude da sessao, nunca tokens/saldo/quota.
```

### 3. Unlimited Session Engine

Responsabilidade:

- criar e manter sessoes longas;
- gravar checkpoints;
- pausar/continuar por handoff;
- controlar heartbeat;
- manter contexto por Repo Memory;
- aplicar degradacao por risco/abuso/estabilidade.

Estados sugeridos:

| Estado | Significado |
|---|---|
| `created` | Sessao criada. |
| `planning` | Agente arquitetando plano. |
| `awaiting_approval` | Aguardando aprovacao humana para acao sensivel. |
| `running` | Agentes executando. |
| `checkpointed` | Snapshot/checkpoint gravado. |
| `handoff_ready` | Sessao pronta para continuidade. |
| `degraded` | Degradada por risco, estabilidade ou abuso. |
| `review` | Pausada para revisao humana/admin. |
| `completed` | Objetivo encerrado. |

### 4. Runtime Broker

Responsabilidade:

- descobrir providers disponiveis;
- selecionar provider por politica;
- aplicar capabilities;
- chamar adapter;
- registrar eventos;
- impedir falso runtime live.

Providers:

| Provider | Tipo | Requisito | Pode ser chamado de runtime oficial? |
|---|---|---|---|
| `official_codex_runtime` | Oficial | endpoint, service credential, tenant, sandbox, Vault/KMS, live flag | Sim, apenas quando binding estiver ativo. |
| `codex_delegated` | Codex delegado | `codex app-server` ou `codex mcp-server` autenticado via ChatGPT/Enterprise | Sim como Codex delegado, nao como binding enterprise interno. |
| `openai_api_authorized` | Oficial/API | API key/service account autorizada e billing aprovado | Sim, como OpenAI API autorizada, nao como runtime interno. |
| `aios_cloud_runtime` | Cloud AIOS | backend/workspace/inferencia operados ou contratados pelo AIOS | Nao, salvo se provider oficial assim permitir. |
| `vllm_self_hosted` | Self-hosted | runtime vLLM gerido pelo AIOS | Nao. |
| `tgi_self_hosted` | Self-hosted | runtime TGI gerido pelo AIOS | Nao. |
| `llamafile_server` | Fallback/dev | servidor llamafile controlado | Nao. |
| `github_models_demo` | Demo | credencial GitHub autorizada | Nao. |
| `puter_user_pays_browser` | Demo/user-pays | usuario autenticado no provider | Nao. |
| `ollama_local_cloud` | Fallback/dev | Ollama instalado/logado/modelo disponivel | Nao. |
| `controlled_simulator` | Demo local | nenhum segredo; rotulo de simulacao | Nao. |

Regra de binding:

```txt
Somente `official_codex_runtime` pode declarar `canInvokeLiveRuntime: true`.
Isso exige `runtime-binding-status.ps1` com binding ativo e `secretsExposed: false`.
```

`codex_delegated` deve ter status proprio, por exemplo `codexDelegatedReady`, porque usa autenticacao e disponibilidade geridas pelo Codex app-server/ChatGPT sign-in, nao o binding enterprise interno do RC16/RC17.

### 4.1 Codex Delegated Runtime

Responsabilidade:

- permitir UX sem OpenAI Platform API key armazenada no AIOS;
- iniciar/verificar login via `codex app-server`;
- listar modelos pelo catalogo retornado pelo Codex;
- renderizar eventos, approvals e historico no Workbench.

Regras:

- AIOS nao le nem copia credenciais brutas;
- AIOS nao implementa proxy OAuth;
- AIOS nao compartilha estado de autenticacao entre maquinas;
- AIOS trata `codex_delegated` como provider distinto de `official_codex_runtime`.

### 4.2 AIOS Delegated Cloud Runtime

Responsabilidade:

- operar workspace efemero por sessao;
- rotear chamadas para runtime self-hosted ou comercial contratado pelo AIOS;
- manter segredo apenas no backend/secret store;
- permitir demo sem chave de API do usuario final.

Providers iniciais:

- vLLM;
- TGI;
- Ollama Server;
- llamafile server;
- providers comerciais explicitamente opt-in.

### 5. Agent Room

Responsabilidade:

- dividir trabalho por papeis;
- registrar quem decidiu o que;
- limitar ferramentas por papel;
- gerar handoff entre agentes.

Agentes iniciais:

| Agente | Ferramentas permitidas | Gate obrigatorio |
|---|---|---|
| Architect | leitura, plano, repo map | antes de mudar escopo. |
| Builder | patch, testes, logs | antes de escrever arquivo sensivel. |
| Debugger | logs, testes, shell sandbox | antes de comandos destrutivos. |
| Reviewer | diff, testes, policy checks | antes de merge/release. |
| Security | secret scan, redaction, threat notes | antes de export/pacote. |
| Release | build, package, hash, changelog | antes de publicar. |
| Docs | docs e relatorios | antes de alterar contrato soberano. |
| UI/UX | layout, copy, visual QA | antes de mudar fluxo principal. |

### 6. Approval Gate

Responsabilidade:

- bloquear acoes sensiveis;
- mostrar diff/risco/impacto;
- pedir aprovacao humana quando necessario;
- registrar auditoria.

Tipos de acao:

| Acao | Comportamento |
|---|---|
| leitura comum | permitida dentro do workspace aprovado. |
| patch em arquivo normal | permitir com diff e rollback. |
| patch em docs soberanos | bloquear ate autorizacao explicita. |
| comando destrutivo | exigir aprovacao. |
| execucao de tool MCP sensivel | exigir permissao por tool. |
| export/relatorio | rodar redaction antes. |
| release publico | rodar package scan e safety gate. |

### 7. Repo Memory

Responsabilidade:

- mapear repo;
- identificar arquivos importantes;
- guardar checkpoints;
- associar commits a sessoes;
- permitir rollback por snapshot.

Unidades:

- `repo_map`;
- `file_importance`;
- `session_checkpoint`;
- `diff_summary`;
- `test_result`;
- `handoff_note`.

### 8. Cloud Workspace

Responsabilidade:

- isolar execucao remota;
- evitar que o app desktop carregue segredos;
- permitir replay/logs;
- separar ambiente do usuario final.

Regra:

```txt
Cloud workspace nao remove necessidade de auditoria, redaction, identidade e policy.
```

### 9. Policy Checks

Checks recomendados:

- security review;
- style guide;
- performance;
- breaking change;
- docs coverage;
- public package safety;
- contract authority;
- runtime binding.

### 10. Marketplace de Ferramentas

Responsabilidade:

- catalogar MCP/tools/skills;
- declarar escopos;
- declarar risco;
- permitir ativacao por workspace/tenant.

Cada ferramenta deve ter:

- nome;
- descricao;
- escopos;
- comandos/acoes;
- nivel de risco;
- politica de aprovacao;
- eventos de auditoria;
- redaction aplicada.

### 11. Account-Linked Entitlement

Responsabilidade:

- validar se a conta usada no Codex/ChatGPT/AIOS tem plano elegivel;
- liberar download do AIOS;
- ativar Workbench Premium e Sessoes Codex;
- revogar acesso quando plano for cancelado;
- manter API key fora do app.

Regras:

- o AIOS pode usar a mesma identidade da conta;
- o AIOS nao deve compartilhar API key da conta;
- o AIOS deve separar billing de ChatGPT/Codex e API Platform quando explicar tecnicamente;
- a UI mostra plano/entitlement, nao tokens.

## Fluxo principal

1. Usuario abre AIOS Desktop.
2. Entra com a mesma conta elegivel usada no Codex/AIOS.
3. Account-Linked Entitlement valida plano.
4. Seleciona projeto ou workspace.
5. Cria Sessao Codex.
6. Architect Agent cria plano.
7. Approval Gate pede aprovacao se necessario.
8. Runtime Broker escolhe provider disponivel.
9. Agent Room executa tarefas.
10. Repo Memory cria checkpoints.
11. Workbench mostra timeline/diff/build.
12. Reviewer/Security validam.
13. Release Agent empacota ou gera PR/diff.
14. Docs Agent gera relatorio redigido.

## Eventos obrigatorios novos

Adicionar aos eventos ja existentes:

- `aios.product_session.created`;
- `aios.agent_room.started`;
- `aios.agent.started`;
- `aios.agent.completed`;
- `aios.approval.requested`;
- `aios.approval.granted`;
- `aios.approval.denied`;
- `aios.repo_memory.indexed`;
- `aios.repo_memory.checkpointed`;
- `aios.runtime_broker.provider_selected`;
- `aios.codex_delegated.auth_state_checked`;
- `aios.codex_delegated.model_listed`;
- `aios.cloud_workspace.created`;
- `aios.cloud_workspace.destroyed`;
- `aios.no_key_demo.started`;
- `aios.no_key_demo.completed`;
- `aios.policy_check.completed`;
- `aios.release.package_scanned`.
- `aios.account_link.started`;
- `aios.entitlement.checked`;
- `aios.download_link.issued`;
- `aios.plan.revoked`.

## Criterios de aceite

### Produto

- Usuario consegue iniciar uma sessao sem ver tokens/creditos.
- Usuario ve agentes, timeline, diff, build e snapshots.
- Usuario entende quando o modo e oficial, demo, fallback ou simulado.

### Tecnico

- Runtime Broker nunca declara oficial sem binding ativo.
- No-Key demo nao exige OpenAI API key do usuario no backend.
- Approval Gate registra cada permissao sensivel.
- Repo Memory gera checkpoint rollback-ready.
- Redaction roda antes de export.

### Seguranca

- Nenhum segredo no frontend.
- Nenhum segredo em GitHub.
- Nenhum segredo em ZIP/EXE/MSI.
- Docs soberanos protegidos.
- Public safety gate executado antes de release publico.
