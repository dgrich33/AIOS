# MCP Repo Operator

Use this skill when Codex operates the local AIOS workspace through MCP.

## Tools

- `repo.list_files`: inventory safe files.
- `repo.search`: search with ripgrep fallback.
- `repo.read_file`: read a safe file.
- `repo.read_range`: read a focused line range.
- `repo.apply_patch`: apply a unified diff inside the workspace.
- `repo.write_file`: write a safe file.
- `repo.run_command`: run allow-listed commands.
- `repo.typecheck`: run target validation.
- `repo.build`: run frontend or backend test guard.
- `repo.git_status`: show repository status when Git is available.
- `repo.git_diff`: show repository diff when Git is available.
- `aios.snapshot.create`: save a local file inventory checkpoint.
- `aios.handoff.create`: save a local handoff artifact.
- `aios.policy.get`: read policy.

## Guardrails

- Never read `.env`, private keys, PEM files, or secret JSON.
- Prefer `repo.search` and `repo.read_range` before reading large files.
- Use snapshots and handoffs for continuity.
- Set `AIOS_API_URL`, `AIOS_SERVICE_TOKEN`, and `AIOS_SESSION_ID` when MCP tool calls should appear in the Workbench.
- If the API is offline, MCP tools must still operate locally and skip remote event logging.
