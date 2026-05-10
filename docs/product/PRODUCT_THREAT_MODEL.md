# Threat Model do Produto AIOS Livre / Codex Unlimited

## Escopo

Este threat model cobre a camada de produto separada:

- AIOS Desktop / Workbench;
- AIOS Backend/Gateway;
- Runtime Broker;
- providers self-hosted/comerciais;
- Codex Delegated Runtime;
- Agent Room;
- Approval Gate;
- Repo Memory;
- Cloud Workspace;
- Marketplace de ferramentas/MCP.

## Ativos sensiveis

- credenciais de runtime e service accounts;
- estado de login gerenciado pelo Codex;
- codigo-fonte do usuario;
- snapshots, diffs e handoff packets;
- logs de comandos;
- relatorios executivos;
- audit events;
- workspace containers;
- artefatos de build;
- policy configs;
- segredos do projeto do usuario.

## Fronteiras de confianca

| Fronteira | Risco principal |
|---|---|
| Frontend desktop -> backend AIOS | exposicao de segredo ou bypass de autorizacao. |
| Backend -> Runtime Broker | provider errado ou falso claim de runtime oficial. |
| Backend -> codex app-server | vazamento de auth state ou transport inseguro. |
| Backend -> cloud workspace | execucao remota indevida ou exfiltracao. |
| Agent Room -> tools/MCP | tool perigosa chamada sem approval. |
| Workspace -> internet | download/exfiltracao sem policy. |
| Export/relatorio -> usuario/terceiros | vazamento de PII, segredo, path sensivel ou codigo restrito. |
| GitHub/release publico | publicacao acidental de segredo, binario privado ou artefato restrito. |

## Entradas controladas por atacante

- prompts;
- repositorios e arquivos do usuario;
- issues/links colados;
- nomes de branch/commit;
- outputs de comando;
- logs de build;
- configuracoes de tool/MCP;
- respostas de providers;
- arquivos gerados por agente;
- conteudo de relatorios importados.

## Invariantes

- AIOS nao exibe tokens/saldo/quota como unidade do produto.
- AIOS nao armazena OpenAI Platform API key no frontend.
- AIOS nao manipula diretamente cache de autenticacao Codex para liberar produto.
- Runtime oficial so e declarado quando binding real estiver ativo.
- Providers self-hosted/demo/simulados nunca sao apresentados como OpenAI/Codex oficial.
- Toda acao sensivel passa por Approval Gate.
- Todo export passa por redaction.
- Todo release publico passa por package scan e public repo safety audit.
- Docs soberanos nao sao editados sem autorizacao explicita.

## Principais falhas a evitar

1. **Auth cache como produto**: tratar arquivo de autenticacao como credencial portavel. Mitigacao: usar app-server/login gerenciado; nao copiar entre maquinas.
2. **Provider confusion**: modelo self-hosted exibido como Codex oficial. Mitigacao: capability flag `officialCodexRuntime=false`.
3. **Tool exfiltration**: agente usa shell/MCP para enviar dados. Mitigacao: allowlist, Approval Gate, NetworkPolicy e logs.
4. **Prompt injection em repo**: arquivo do usuario tenta alterar politicas do agente. Mitigacao: system policy fixa, scopes por agente e policy checks.
5. **Secret leakage em logs/relatorios**: outputs incluem chaves. Mitigacao: redaction antes de persistir/exportar.
6. **Rollback falso**: snapshot incompleto. Mitigacao: hash de arquivos, diff completo e teste de restauracao.
7. **Concorrencia de approvals/auth**: multiplas sessoes usam o mesmo estado sensivel. Mitigacao: locks por workspace/usuario e isolamento por sessao.
8. **Release contaminado**: ZIP/EXE inclui `.env`, auth, banco, logs ou artefatos privados. Mitigacao: `public-repo-safety-audit.ps1`, package scan e lista de bloqueio.

## Controles minimos

- RBAC por tenant/workspace;
- OIDC/SSO para usuarios;
- service accounts apenas no backend/secret store;
- OpenTelemetry com redaction;
- audit append-only;
- hash chain opcional para auditoria;
- workspace efemero por sessao;
- NetworkPolicy/OPA para tools;
- package scan antes de release;
- approval hash e justificativa humana para acoes sensiveis.

## Sinais de alerta

- UI dizendo "runtime oficial" com `canInvokeLiveRuntime=false`;
- qualquer token em log, frontend ou relatorio;
- provider demo sem rotulo;
- tool MCP com shell livre;
- arquivo de autenticacao em Git, ZIP ou artifact;
- workspace reutilizado entre usuarios;
- relatorio executivo com prompt completo sensivel.
