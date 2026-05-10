# AIOS Livre / Codex Unlimited - Roadmap de Implementacao

## Objetivo

Transformar a base RC atual em um produto separado com experiencia ilimitada por sessao, Workbench premium, governanca, agentes especializados e demo sem chave de API do usuario.

## RC20 - Product Shell e Posicionamento

Entregas:

- [ ] Criar identidade de produto `AIOS Livre / Codex Unlimited`.
- [ ] Adicionar tela inicial com unidade `Sessoes Codex`.
- [ ] Remover qualquer texto de UI que pareca token/saldo/quota.
- [ ] Adicionar indicador de modo: oficial, demo, fallback ou simulacao controlada.
- [ ] Adicionar link para docs de governanca.

Validacoes:

- [ ] Frontend build OK.
- [ ] Playwright smoke test da tela inicial.
- [ ] Busca textual por `token balance`, `quota`, `creditos` na UI.

## RC21 - Runtime Broker 2.0

Entregas:

- [ ] Normalizar providers com capabilities.
- [ ] Separar `official_codex_runtime`, `openai_api_authorized`, `puter_user_pays_browser`, `github_models_demo`, `ollama_local_cloud` e `controlled_simulator`.
- [ ] Impedir `canInvokeLiveRuntime: true` fora de official binding ativo.
- [ ] Registrar `aios.runtime_broker.provider_selected`.
- [ ] Adicionar endpoint de explainability do provider escolhido.

Validacoes:

- [ ] Teste unitario por provider.
- [ ] Teste de bloqueio para falso runtime live.
- [ ] `runtime-binding-status.ps1 -WriteReport` continua correto.

## RC22 - Agent Room

Entregas:

- [ ] Criar schema de agentes.
- [ ] Adicionar Architect, Builder, Debugger, Reviewer, Security, Release, Docs e UI/UX.
- [ ] Definir ferramentas permitidas por agente.
- [ ] Adicionar timeline de agentes no Workbench.
- [ ] Adicionar handoff entre agentes.

Validacoes:

- [ ] Teste de criacao de Agent Room.
- [ ] Teste de limite de ferramenta por agente.
- [ ] Workbench mostra agente ativo e eventos.

## RC23 - Approval Gate

Entregas:

- [ ] Classificar acoes por risco.
- [ ] Mostrar diff/impacto antes de patch sensivel.
- [ ] Bloquear docs soberanos sem autorizacao explicita.
- [ ] Registrar `aios.approval.requested/granted/denied`.
- [ ] Integrar com MCP/tools.

Validacoes:

- [ ] Teste de bloqueio para docs soberanos.
- [ ] Teste de aprovacao para patch normal.
- [ ] Teste de redaction em log de approval.

## RC24 - Repo Memory e Snapshots Premium

Entregas:

- [ ] Criar repo map.
- [ ] Marcar arquivos importantes.
- [ ] Criar checkpoint por sessao.
- [ ] Associar checkpoint a commit/diff.
- [ ] Adicionar rollback visual.

Validacoes:

- [ ] Teste de indexacao de repo.
- [ ] Teste de checkpoint.
- [ ] Teste de rollback metadata.

## RC25 - Workbench Premium

Entregas:

- [ ] Timeline de sessao.
- [ ] Painel de arquivos alterados.
- [ ] Diff visual.
- [ ] Status de build/testes.
- [ ] Risk score.
- [ ] Relatorio executivo redigido.

Validacoes:

- [ ] Playwright desktop viewport.
- [ ] Sem sobreposicao de texto.
- [ ] Relatorio nao contem segredo.

## RC26 - No-Key Demo Pack

Entregas:

- [ ] Puter User-Pays demo.
- [ ] GitHub Models demo, se credencial autorizada estiver disponivel.
- [ ] Ollama fallback.
- [ ] Controlled Simulator com rotulo explicito.
- [ ] Painel de comparacao de providers.

Validacoes:

- [ ] Nenhuma chave no frontend.
- [ ] Nenhum provider demo declara official runtime.
- [ ] Eventos de auditoria gerados por demo.

## RC27 - Marketplace de Tools

Entregas:

- [ ] Catalogo de MCP/tools/skills.
- [ ] Escopos por tool.
- [ ] Risco por tool.
- [ ] Permissao por tenant/workspace.
- [ ] Logs por chamada.

Validacoes:

- [ ] Tool sem permissao nao executa.
- [ ] Tool sensivel exige approval.
- [ ] Auditoria registra toolName/action/status.

## RC28 - Package e Go/No-Go

Entregas:

- [ ] ZIP beta.
- [ ] EXE/MSI preparado para assinatura.
- [ ] Package scan.
- [ ] Public repo safety gate.
- [ ] Changelog.
- [ ] Go/No-Go checklist.

Validacoes:

- [ ] Contract authority OK.
- [ ] Contract docs audit OK.
- [ ] Public repo safety audit revisado.
- [ ] Build/testes principais OK.

## Definicao de pronto

A fase do produto separado esta pronta para demonstracao executiva quando:

- `AIOS Livre / Codex Unlimited` abre como produto separado;
- a UI apresenta Sessoes Codex;
- Workbench Premium mostra timeline, agentes, diffs, build e snapshots;
- Runtime Broker seleciona provider sem falso claim;
- No-Key demo funciona ou fica bloqueada com diagnostico honesto;
- Approval Gate e audit/redaction cobrem acoes sensiveis;
- pacote nao inclui segredo, chave, auth, binario privado, peso ou checkpoint.
