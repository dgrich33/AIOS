# RC27 AIOS Native Runtime Fabric Design

## Goal

RC27 makes AIOS a runtime product in its own right, not a thin dependency on an official Codex binding. AIOS can be alive, functional, and presentable when any real runtime is validated, while `officialProduction=true` remains reserved for a complete official production binding.

## Product Narrative

AIOS is the new Codex-like execution layer for sessions, agents, governance, and pluggable runtimes. The official Codex/OpenAI runtime is a premium provider when provisioned, not a structural dependency.

## Runtime Status Rules

- `canInvokeLiveRuntime=true` may come from any validated real runtime: `codex_cli_local_developer`, `openai_api_authorized`, `aios_native_runtime`, `aios_cloud_runtime`, or `self_hosted_runtime`.
- `officialProduction=true` only comes from `official_codex_runtime` when the complete official binding is present and validated.
- `productionBlocked=true` can coexist with `canInvokeLiveRuntime=true`; this means AIOS is live for demo/local/authorized runtime, but not official production.
- `secretsExposed=false` is mandatory in every status payload.

## Providers

RC27 exposes these providers as a status map:

- `controlled_simulator`: always available for controlled demos, not live.
- `codex_cli_local_developer`: live only when the local Codex CLI path is explicitly allowed and validated.
- `openai_api_authorized`: live only when local environment validation confirms an API runtime is available.
- `aios_native_runtime`: AIOS-owned session runtime; live when session engine, agent room, governance, and runtime fabric are enabled.
- `aios_cloud_runtime`: ready when cloud workspace configuration exists; live only after explicit provider validation.
- `self_hosted_runtime`: ready when a self-hosted inference base URL and model id are configured.
- `official_codex_runtime`: official production only when full binding requirements are present.

## Model Policy Registry

The registry is policy metadata, not a promise that a model is active. It must include:

- `gpt-5.2-codex`: provider-discovered Codex programming model, inactive until exposed by a validated provider.
- `gpt-4o`: legacy/provider-discovery model entry, inactive until a validated provider exposes it again.

The UI and API must not claim either model is usable unless a provider validates availability.

## API Surface

- `GET /runtime/fabric/status`: returns runtime fabric status, providers, active runtime, live booleans, production block reason, and secrets safety.
- `GET /runtime/fabric/model-policy`: returns the model policy registry.
- Existing control-plane status includes `aios_runtime_fabric`, `aios_native_runtime`, `provider_discovery`, and `model_policy_registry` capabilities.

## UI Surface

Workbench adds a panel titled `RC27 AIOS Native Runtime Fabric` that shows:

- Whether AIOS can invoke a live runtime.
- Whether official production is active or blocked.
- The active runtime provider.
- Provider status chips.
- Model policy registry, including `gpt-5.2-codex` and `gpt-4o` as provider-discovered entries.

## Safety Constraints

- No `auth.json` reads.
- No `.env` or key values displayed.
- No production official live flag without full official binding.
- No file deletion or replacement of legacy adapters.
- No GitHub push or ZIP generation in RC27.
