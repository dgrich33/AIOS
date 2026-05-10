# Intake de Ideias da Equipe - 2026-05-10

## Objetivo

Registrar as tres ideias recebidas da equipe e transformar o material em decisoes de produto executaveis para o AIOS Livre / Codex Unlimited.

Este arquivo nao substitui os documentos soberanos. Ele serve como consolidacao tecnica e de produto para as proximas RCs.

## Ideia 1 - Produto completo self-hosted/cloud

Resumo:

- app Windows/Desktop;
- Workbench Premium;
- Agent Room;
- Runtime Broker model-adaptive;
- runtime delegado sem chave de API do usuario no app;
- self-hosted ou cloud operado/contratado pelo AIOS;
- governanca enterprise com RBAC, auditoria, redaction e workspace isolado.

Decisao:

```txt
Aprovada como direcao principal de produto.
```

O AIOS deve suportar providers self-hosted e cloud operados pelo AIOS, como vLLM, TGI, Ollama Server e llamafile, alem de provedores comerciais explicitamente contratados pela organizacao.

Limite:

```txt
Provider self-hosted nao deve ser apresentado como OpenAI/Codex oficial.
```

## Ideia 2 - Pesquisa de projetos uteis

Resumo:

- OpenAI Codex CLI/App como referencia de UX, logs, approvals, app-server, CLI/IDE e model picker;
- Cline como referencia de Approval Gate;
- Roo Code como referencia de modos/agentes;
- Aider como referencia de Repo Memory, Git e testes;
- OpenHands como referencia de cloud workspace/sandbox;
- Continue como referencia de policy checks;
- SWE-agent como referencia de issue-to-patch.

Decisao:

```txt
Aprovada como mapa de referencias, sem copiar marca, codigo ou claims proprietarios.
```

Uso correto:

- estudar fluxos;
- adaptar padroes de UX;
- criar arquitetura propria;
- revisar licencas antes de qualquer reuso de codigo.

## Ideia 3 - Codex Delegated Runtime com ChatGPT-managed auth

Resumo:

O AIOS pode oferecer um caminho sem OpenAI Platform API key armazenada no app usando o runtime delegado do Codex:

```txt
AIOS Workbench
-> Codex App-Server Adapter
-> codex app-server / codex mcp-server
-> ChatGPT-managed sign-in / Enterprise sign-in
-> modelo Codex disponivel no ambiente Codex
```

Decisao:

```txt
Aprovada como caminho tecnico seguro de pesquisa e prototipo.
```

Esse caminho e diferente de "sem autenticacao". Ele significa:

- AIOS nao armazena API key OpenAI do usuario;
- Codex gerencia login, refresh, modelos e approvals;
- AIOS conversa com a interface local suportada do Codex;
- o usuario/workspace continua autenticado por ChatGPT/Codex/Enterprise.

## Pontos bloqueados

Os seguintes pontos nao entram no produto padrao:

- ler manualmente arquivo local de autenticacao em producao;
- copiar cache de autenticacao entre maquinas como mecanismo de produto;
- commitar, exportar, zipar ou logar credenciais;
- usar proxy OAuth nao oficial;
- usar refresh token do usuario fora do fluxo gerido pelo Codex;
- apresentar provider self-hosted, demo ou simulado como runtime oficial OpenAI/Codex;
- trocar endpoint/token/tenant/live flag por autoativacao local.

## Decisao final consolidada

O produto deve ter dois trilhos seguros:

| Trilha | Finalidade | Status |
|---|---|---|
| AIOS Delegated Cloud Runtime | Runtime self-hosted/comercial operado pelo AIOS, sem chave do usuario no app | Direcao principal para MVP comercial independente |
| Codex Delegated Runtime | Integracao com Codex app-server/CLI autenticado por ChatGPT/Enterprise | Direcao de pesquisa/prototipo oficial Codex |

Ambas as trilhas passam pelo mesmo Workbench Premium, Agent Room, Approval Gate, Repo Memory, auditoria e redaction.
