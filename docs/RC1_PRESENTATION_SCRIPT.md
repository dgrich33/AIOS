# AIOS Codex Unlimited RC1 Presentation Script

## Opening

This is AIOS Codex Unlimited RC1, a release candidate for evaluating Codex as a continuous development environment inside AIOS.

The product unit is not tokens, credit packs, balances, or weekly quota. The product unit is:

```txt
Codex sessions
```

Message:

```txt
Codex sem limites. Desenvolvimento sem interrupcoes.
```

## Show Frontend

Open:

```txt
http://127.0.0.1:5173
```

Login:

```txt
admin@aios.local
AiosAdmin123!
```

Say:

```txt
This is the Codex Workbench. It turns Codex from a chat-style interaction into an operating environment with state, execution, events and continuity.
```

## Session

Click `Nova sessao`.

Say:

```txt
The session is the unit of work. It keeps objective, events, files, snapshots, handoff and runtime status together.
```

## Snapshot

Click `Snapshot`.

Say:

```txt
Snapshots preserve operational continuity and make a session resumable.
```

## Handoff

Click `Handoff`.

Say:

```txt
Handoff allows the work to continue across agents, runtimes or future sessions without restarting the context from zero.
```

## MCP Events

Click `Simular evento MCP`.

Say:

```txt
The Workbench records tool activity, files changed and build state. In the MCP integration path, repo tools post events into the active session by session_id.
```

Show:

- Eventos recentes
- MCP e logs
- Arquivos e build
- Snapshots
- Handoff
- Runtime Adapter
- Origem AIOS

## API Docs

Open:

```txt
http://127.0.0.1:8000/docs
```

Show:

- `/entitlement/me`
- `/control-plane/status`
- `/sessions/{session_id}/workbench`
- `/sessions/{session_id}/events`
- `/sessions/{session_id}/files-changed`
- `/codex/adapter/info`

Say:

```txt
The frontend is backed by a real API. The official Codex runtime integration belongs behind CodexRuntimeAdapter.
```

## Closing

```txt
AIOS Codex Unlimited RC1 demonstrates the full local flow: sessions, entitlement, Workbench, events, MCP integration path, snapshots, handoff, API, and adapter boundary. The next decision is whether to move from RC1 into official Codex runtime integration.
```

