# AIOS Livre / Codex Unlimited - Sintese de Pesquisa

Data da pesquisa: 2026-05-10.

## Principios de uso das fontes

- Para OpenAI/Codex, priorizar documentacao oficial e repositorios oficiais.
- Para concorrentes/projetos open-source, priorizar repositorios e docs oficiais.
- Para Reddit, usar apenas como leitura de dor de usuario, nao como verdade tecnica.
- Nao copiar codigo de terceiros sem revisar licenca e compatibilidade.

## Fontes OpenAI/Codex

| Fonte | O que importa para AIOS |
|---|---|
| OpenAI API docs - GPT-5.5: `https://developers.openai.com/api/docs/guides/latest-model` | GPT-5.5 e indicado para workflows complexos de producao, coding, agentes com tools, recuperacao de contexto e product-spec-to-plan. |
| OpenAI Codex docs - App features: `https://developers.openai.com/codex/app/features` | Codex App combina chat, local, cloud tasks, skills, automations, artifacts, IDE extension, MCP/web search e approvals/sandboxing. |
| OpenAI Codex docs - Agent approvals and security: `https://developers.openai.com/codex/agent-approvals-security` | Aprovals e sandbox sao parte central do modelo seguro: o agente pede permissao quando sai das fronteiras aprovadas. |
| OpenAI Codex auth docs: `https://developers.openai.com/codex/auth` | Codex possui caminhos de autenticacao por ChatGPT sign-in e API key; AIOS deve delegar login ao Codex quando usar `codex_delegated`. |
| OpenAI Codex app-server README: `https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md` | `codex app-server` usa JSON-RPC, expoe account/login, model/list, threads, turns, eventos, approvals, MCP e skills; e a melhor base para adapter delegado. |
| OpenAI Codex MCP interface: `https://github.com/openai/codex/blob/main/codex-rs/docs/codex_mcp_interface.md` | Interface experimental para controlar Codex local via MCP/JSON-RPC, com threads, turns, modelos, eventos e approvals. |
| OpenAI API docs - GPT-5.2-Codex model page: `https://developers.openai.com/api/docs/models/gpt-5.2-codex` | `gpt-5.2-codex` aparece documentado como modelo Codex para tarefas agenticas longas, mas a pagina tambem mostra alias/snapshot deprecated. Usar como compatibilidade, nao como pino unico. |
| OpenAI Codex blog - long horizon tasks: `https://developers.openai.com/blog/run-long-horizon-tasks-with-codex` | Reforca a direcao de tarefas longas: plan, edit, test, repair, worktrees, Git, diffs, logs e memoria em arquivos. |
| OpenAI Codex repo: `https://github.com/openai/codex` | Referencia de direcao oficial para CLI, app, IDE extension, sandbox, MCP, skills e automations. |

Leitura para o AIOS:

- O produto precisa se alinhar a sessoes longas e nao a chats curtos.
- Skills, automations, approvals, sandbox, Git/diff e task logs devem ser recursos de primeira classe.
- Modelos precisam entrar por uma camada adaptativa, porque nomes e disponibilidade mudam.
- A rota recomendada de modelo deve ser adaptativa: priorizar o modelo atual aprovado para coding/agentes, como `gpt-5.5` quando disponivel, e manter `gpt-5.2-codex` apenas como compatibilidade/provisionamento especifico.
- O produto deve mostrar estado, risco e atividade, nao tokens/creditos.

## Projetos de referencia

| Projeto | Fonte | Ideia aproveitavel |
|---|---|---|
| OpenAI Codex CLI/App | `https://github.com/openai/codex` | CLI por tras do app, permissao/sandbox, MCP, app desktop, IDE, tasks cloud, model picker e logs. |
| Cline | `https://github.com/cline/cline` | Human-in-the-loop para comandos, alteracoes em arquivos, navegador, terminal e MCP; base para AIOS Approval Gate. |
| Roo Code | `https://github.com/RooVetGit/Roo-Code` | Modos/agentes especializados; base para AIOS Agent Room. |
| Aider | `https://github.com/Aider-AI/aider` | Repo map, Git, commits, testes e edicao orientada por diff; base para AIOS Repo Memory. |
| OpenHands | `https://github.com/All-Hands-AI/OpenHands` | Agente de software com workspace/sandbox e operacao mais cloud; base para AIOS Cloud Workspace. |
| Continue | `https://github.com/continuedev/continue` | Assistente/agent em IDE e automacoes de review; base para AIOS Policy Checks. |
| SWE-agent / mini-swe-agent | `https://github.com/SWE-agent/SWE-agent` e `https://github.com/SWE-agent/mini-swe-agent` | Fluxo issue-to-patch: ler issue, editar repo, rodar testes, gerar diff/PR. |
| GitHub Models | `https://github.com/marketplace/models` | Provider demo/experimento com API e billing fora do usuario final do AIOS, conforme permissao. |
| Puter.js | `https://docs.puter.com/AI/` | User-pays/no-developer-cost para demo browser; nao substitui runtime oficial. |
| Ollama Cloud/Local | `https://ollama.com/search?c=cloud` | Fallback local/cloud para desenvolvimento e demonstracoes, sem declarar modelo oficial Codex. |

## Dores de usuario observadas em comunidades

Reddit deve entrar como fonte qualitativa para entender frustracoes, nao como base de arquitetura.

Buscas recomendadas:

- `"Codex limits" reddit`;
- `"Claude Code vs Codex" reddit`;
- `"Cline vs Roo Code" reddit`;
- `"AI coding agent long tasks" reddit`;
- `"Codex app bugs" reddit`;
- `"coding agent workflow" reddit`.

Dores que o AIOS deve atacar:

- limites visiveis interrompendo fluxo;
- perda de contexto em tarefas longas;
- agente quebrando projeto sem rollback;
- custo imprevisivel;
- falta de controle de diff;
- falta de aprovacao clara antes de comando perigoso;
- falta de historico/handoff entre sessoes;
- falta de "equipe de agentes" com papeis claros;
- dificuldade de transformar issue em patch testado.

## O que copiar como ideia, nao como codigo

### OpenAI Codex

- separacao entre app, CLI, IDE e cloud;
- sandbox e approvals como default seguro;
- skills e automations;
- trabalho em worktree;
- logs e diffs.

### Cline

- Approval Gate com diff, risco e confirmacao;
- ferramenta de navegador e terminal com permissao humana;
- MCP como extensao segura.

### Roo Code

- Agent Room com modos;
- cada modo com ferramentas permitidas e limites.

### Aider

- Repo Memory;
- commits por checkpoint;
- execucao de testes e lint antes de finalizar.

### OpenHands

- Cloud Workspace isolado;
- replay/logs de tarefa;
- execucao remota segura.

### Continue

- checks de policy por PR;
- regras versionadas no repo.

### SWE-agent

- Issue-to-Patch;
- medicao por testes e diff, nao por chat.

## Decisoes para o produto

1. A arquitetura deve ser model-adaptive.
2. A UI deve esconder tokens e mostrar saude/sessao/atividade.
3. O broker deve ser honesto sobre o provider ativo: oficial, demo, fallback ou simulado.
4. O Plano B pode existir, mas sempre como adapter local controlado.
5. Qualquer provider sem chave do usuario deve ter auditoria e rotulo de modo.
6. Runtime oficial continua dependente de binding real: endpoint, credencial, tenant, sandbox, Vault/KMS e live flag.
