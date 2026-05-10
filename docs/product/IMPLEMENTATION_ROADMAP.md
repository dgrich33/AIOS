# AIOS Livre / Codex Unlimited - Roadmap de Implementacao

## Objetivo

Transformar a base RC atual em um produto separado com experiencia ilimitada por sessao, Workbench premium, governanca, agentes especializados e demo sem chave de API do usuario.

## RC20 - Product Shell e Posicionamento

Entregas:

- [x] Criar identidade de produto `AIOS Livre / Codex Unlimited`.
- [x] Adicionar tela inicial com unidade `Sessoes Codex`.
- [x] Remover qualquer texto de UI que pareca token/saldo/quota.
- [x] Adicionar indicador de modo: oficial, demo, fallback ou simulacao controlada.
- [x] Adicionar link para docs de governanca.

Validacoes:

- [x] Frontend build OK.
- [x] Playwright smoke test da tela inicial.
- [x] Busca textual por `token balance`, `quota`, `creditos` na UI.

Evidencia: `docs/RC20_PRODUCT_SHELL.md`.

## RC21 - Runtime Broker 2.0

Entregas:

- [x] Normalizar providers com capabilities.
- [x] Separar `official_codex_runtime`, `codex_delegated`, `aios_cloud_runtime`, `openai_api_authorized`, `puter_user_pays_browser`, `github_models_demo`, `ollama_local_cloud`, `vllm_self_hosted`, `tgi_self_hosted`, `llamafile_server` e `controlled_simulator`.
- [x] Impedir `canInvokeLiveRuntime: true` fora de official binding ativo.
- [x] Registrar `aios.runtime_broker.provider_selected`.
- [x] Adicionar endpoint de explainability do provider escolhido.

Validacoes:

- [x] Teste unitario por provider.
- [x] Teste de bloqueio para falso runtime live.
- [x] `runtime-binding-status.ps1 -WriteReport` continua correto.

Evidencia: `docs/RC21_RUNTIME_BROKER_2.md`.

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

## RC29 - Codex Delegated Runtime Adapter

Entregas:

- [ ] Criar `CodexAppServerAdapter` como provider `codex_delegated`.
- [ ] Detectar/iniciar `codex app-server` em transporte local seguro.
- [ ] Chamar `account/read` sem expor credenciais.
- [ ] Oferecer login ChatGPT/device code via `account/login/start`.
- [ ] Listar modelos via `model/list`.
- [ ] Iniciar thread/turn e renderizar eventos no Workbench.
- [ ] Encaminhar approvals do Codex para o AIOS Approval Gate.

Validacoes:

- [ ] Nenhum token aparece em log/frontend/relatorio.
- [ ] Provider `codex_delegated` nao altera `canInvokeLiveRuntime`.
- [ ] Falha de autenticacao mostra acao segura: fazer login novamente.
- [ ] Websocket remoto fica desativado ou autenticado por capability token.

## RC30 - AIOS Delegated Cloud Runtime MVP

Entregas:

- [ ] Criar provider `aios_cloud_runtime`.
- [ ] Criar provider `vllm_self_hosted` ou `tgi_self_hosted` para staging.
- [ ] Criar workspace efemero por sessao.
- [ ] Guardar credenciais apenas em secret store do backend.
- [ ] Expor stream por WebSocket autenticado.
- [ ] Registrar OpenTelemetry/audit/redaction por sessao.

Validacoes:

- [ ] Usuario final nao fornece API key.
- [ ] Workspace e destruido/arquivado conforme retencao.
- [ ] Provider self-hosted aparece como self-hosted, nao como Codex oficial.
- [ ] Package scan nao encontra segredo nem modelo privado.

## RC31 - Account-Linked AIOS Plan

Entregas:

- [ ] Criar modelo de entitlement `account_linked_aios`.
- [ ] Adicionar fluxo de download por conta elegivel.
- [ ] Adicionar login "Entrar com a mesma conta do Codex/AIOS".
- [ ] Adicionar status de plano no Workbench sem tokens/saldo/quota.
- [ ] Separar copy de ChatGPT/Codex plan e API Platform.
- [ ] Registrar eventos `aios.account_link.started`, `aios.entitlement.checked`, `aios.download_link.issued` e `aios.plan.revoked`.

Validacoes:

- [ ] Usuario sem entitlement nao ativa Workbench Premium.
- [ ] Usuario com entitlement ativa Sessoes Codex.
- [ ] AIOS nao pede API key do usuario.
- [ ] Cancelamento/revogacao remove acesso.
- [ ] Logs nao contem access token, refresh token ou API key.

## Definicao de pronto

A fase do produto separado esta pronta para demonstracao executiva quando:

- `AIOS Livre / Codex Unlimited` abre como produto separado;
- a UI apresenta Sessoes Codex;
- Workbench Premium mostra timeline, agentes, diffs, build e snapshots;
- Runtime Broker seleciona provider sem falso claim;
- No-Key demo funciona ou fica bloqueada com diagnostico honesto;
- Approval Gate e audit/redaction cobrem acoes sensiveis;
- pacote nao inclui segredo, chave, auth, binario privado, peso ou checkpoint.
