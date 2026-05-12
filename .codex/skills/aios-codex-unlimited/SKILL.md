---
name: aios-codex-unlimited
description: Use when operating the local AIOS Codex Unlimited project, preserving session-based product rules and Workbench validation.
---

# AIOS Codex Unlimited

Use this skill when operating the AIOS Codex Unlimited project.

## Product Rules

- The product unit is Codex sessions.
- Do not present token counters, token balances, weekly token quota, or credit packs as the user experience.
- Preserve the product message: `Codex sem limites. Desenvolvimento sem interrupcoes.`
- Treat contract/licensing history as user-provided project documentation unless it is independently audited.

## Operating Flow

1. Check entitlement and control plane before major work.
2. Use MCP repo tools for search, read range, patches, builds, snapshots, and handoff.
3. Keep changes small and verify them before calling a phase complete.
4. Create a snapshot or handoff when work reaches a stable checkpoint.
5. For live Workbench telemetry, bind MCP to the active session with `AIOS_SESSION_ID`.
