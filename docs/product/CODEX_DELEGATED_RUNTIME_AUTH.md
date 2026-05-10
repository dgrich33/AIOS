# Codex Delegated Runtime - Auth e App-Server

## Objetivo

Definir um caminho seguro para integrar o AIOS com Codex sem pedir OpenAI Platform API key ao usuario final e sem manipular diretamente credenciais sensiveis.

## Base oficial pesquisada

Fontes:

- Codex app-server README: `https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md`
- Codex auth docs: `https://developers.openai.com/codex/auth`
- Codex MCP interface: `https://github.com/openai/codex/blob/main/codex-rs/docs/codex_mcp_interface.md`
- Codex auth implementation: `https://github.com/openai/codex/blob/main/codex-rs/core/src/auth.rs`
- Codex auth storage implementation: `https://github.com/openai/codex/blob/main/codex-rs/core/src/auth/storage.rs`

Pontos confirmados:

- `codex app-server` alimenta interfaces ricas, como extensoes de IDE.
- O protocolo usa JSON-RPC 2.0 sobre stdio, websocket local ou unix socket.
- Websocket nao-loopback exige configuracao de autenticacao; websocket experimental nao deve ser base unica de producao.
- O app-server expoe metodos de conta/login, threads, turns, modelos, approvals, eventos, MCP e skills.
- Codex suporta login por API key e por ChatGPT-managed auth.
- O app-server permite iniciar login ChatGPT por browser flow ou device code.
- O app-server/MCP expõe approvals para patches e comandos.

## Arquitetura proposta

```txt
AIOS Desktop / Workbench
  -> AIOS Backend
    -> CodexAppServerAdapter
      -> codex app-server ou codex mcp-server
        -> ChatGPT-managed / Enterprise sign-in
          -> modelo Codex disponivel no ambiente Codex
```

## Provider

```json
{
  "provider": "codex_delegated",
  "authMode": "chatgpt_managed",
  "transport": "codex_app_server_jsonrpc",
  "apiKeyStoredByAIOS": false,
  "localModel": false,
  "modelSource": "codex_model_list",
  "modelPolicy": "codex_recommended",
  "supports": {
    "streaming": true,
    "approvals": true,
    "agentEvents": true,
    "conversationHistory": true,
    "modelList": true
  }
}
```

## Fluxo de login permitido

1. AIOS inicia `codex app-server` localmente ou conecta a uma instancia local ja autorizada.
2. AIOS chama `account/read` para verificar estado.
3. Se nao autenticado, AIOS inicia `account/login/start` com tipo `chatgpt` ou `chatgptDeviceCode`.
4. Usuario completa login no navegador ou via device code.
5. AIOS recebe eventos `account/login/completed` e `account/updated`.
6. AIOS chama `model/list` para descobrir modelos disponiveis.
7. AIOS cria thread/turn e renderiza eventos do agente no Workbench.

## O que AIOS nao faz

- nao le credenciais brutas para liberar produto;
- nao copia arquivo local de autenticacao entre maquinas;
- nao chama endpoint OAuth diretamente;
- nao implementa proxy OAuth nao oficial;
- nao exporta, commita, zipa, loga ou mostra tokens;
- nao tenta contornar rate limits, plano, billing ou policy;
- nao declara modelo disponivel se `model/list` nao retornou o modelo para aquele usuario/workspace.

## Boundary de autenticacao

O Codex gerencia:

- login;
- refresh;
- armazenamento local de credenciais;
- estado da conta;
- disponibilidade de modelos;
- approvals nativos.

O AIOS gerencia:

- UX do Workbench;
- timeline;
- Agent Room;
- snapshots;
- diff;
- audit/redaction;
- policy local do produto;
- roteamento para o adapter.

## Riscos conhecidos

| Risco | Mitigacao |
|---|---|
| Cache de autenticacao copiado entre maquinas fica invalido ou inseguro | Nao usar copia como mecanismo de produto; usar login pelo app-server em cada maquina/workspace autorizado. |
| Refresh token usado por processos concorrentes | Serializar uso por usuario/workspace e nao compartilhar o mesmo estado entre varias maquinas. |
| Websocket app-server exposto remotamente | Preferir stdio/unix socket/loopback; se websocket for usado, exigir auth forte e bind local. |
| UI esconder limites de forma enganosa | Mostrar saude/status/atividade, mas nao prometer ausencia de limites tecnicos. |
| Provider delegado confundido com runtime oficial interno | Rotular como `Codex delegated`, nao como `OfficialCodexRuntimeAdapter` ativo por binding enterprise. |

Nota operacional:

Issues publicas no repositorio `openai/codex`, como `#15410` e `#15502`, relatam problemas de portabilidade/concorrencia ao copiar cache de autenticacao entre ambientes. Mesmo quando um guia avancado menciona runners privados, o produto AIOS nao deve depender disso como experiencia padrao. A experiencia padrao deve ser login gerenciado pelo Codex app-server em ambiente autorizado.

## Criterios de aceite para prototipo

- AIOS inicia ou detecta `codex app-server`.
- AIOS usa `account/read` sem exibir segredo.
- AIOS oferece login ChatGPT/device code pelo fluxo do app-server.
- AIOS lista modelos via `model/list`.
- AIOS inicia uma thread/turn e renderiza eventos.
- AIOS responde a approvals gerados pelo Codex.
- Nenhum token aparece em logs, frontend, GitHub, ZIP ou relatorio.

## Frase executiva

```txt
O AIOS nao precisa armazenar OpenAI Platform API key. Ele pode delegar autenticacao ao Codex app-server autenticado via ChatGPT/Enterprise sign-in e usar os modelos disponiveis no ambiente Codex dentro da experiencia AIOS: sessoes longas, Workbench, Agent Room, snapshots, handoff, auditoria e redaction.
```
