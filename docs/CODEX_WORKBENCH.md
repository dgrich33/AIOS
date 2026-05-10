# Codex Workbench

The Workbench is the first practical next phase beyond the enterprise base.

It includes:

- authenticated API provider;
- entitlement and control-plane panels;
- session creation;
- Codex run request through the local adapter;
- snapshot creation;
- handoff creation and session handoff history;
- changed-file view from the latest snapshot;
- build status from QoS jobs tied to the session;
- recent MCP/skill call log view;
- recent session events from `session_events`;
- AIOS original project lineage and migration map;
- QoS build job enqueue;
- skill execution;
- abuse evaluation sample.

This is not the final official Codex runtime. It is the UI and API integration layer that makes the future adapter boundary visible and testable.

## Backend endpoints

- `GET /aios/heritage/summary`
- `POST /handoffs`
- `GET /sessions/{session_id}/handoffs`
- `POST /sessions/{session_id}/events`
- `GET /sessions/{session_id}/events`
- `POST /sessions/{session_id}/files-changed`
- `GET /sessions/{session_id}/workbench`

## Event types

- `mcp.tool_call`
- `repo.patch_applied`
- `repo.file_changed`
- `repo.build_started`
- `repo.build_passed`
- `repo.build_failed`
- `snapshot.created`
- `handoff.created`
- `skill.executed`

## Demo flow

1. Create a session in the Workbench.
2. Create a snapshot or click `Simular evento MCP`.
3. Mint a service token and set `AIOS_SERVICE_TOKEN` plus `AIOS_SESSION_ID` for MCP repo.
4. Run `repo.build` through MCP.
5. Refresh the Workbench and show events, files changed and build status.
