# Codex Plan Core organ bridge

This Rust crate is the RC35 bridge boundary for `codex.plan.core`.

Implemented locally:

- Delegate status probing through the Codex CLI binary.
- Mapping quota/usage-limit failures to `RESOURCE_EXHAUSTED` semantics.
- Socket configuration through `CODEX_CLI_SOCKET`, defaulting to `/tmp/codex_cli.sock`.

The full gRPC transport is represented by `aios-codex-specs/proto/aios/cos/v1/cos.proto` and is intended to replace the current process probe when the local Codex bridge socket is available.
