# AIOS Pilot Quickstart

## Access

Your account must be mapped to the Kubernetes/Sentinel group `aios_pilot`.

The pilot role is read-only at the cluster layer. It can inspect AIOS pods, services, ConfigMaps, and logs, but it cannot deploy, delete, or mutate runtime resources.

## First Mission

Use Mission Desk in the AIOS UI:

1. Open the internal AIOS URL provided by the platform owner.
2. Choose **New Mission**.
3. Select the repository and branch approved for pilot use.
4. Enter a small engineering goal.
5. Review the Reality Panel before approval:
   - `codex_plan_bridge` means Codex Plan Core is currently available.
   - `beta_open_weight` means AIOS fell back to a beta organ.
6. Approve only non-destructive actions you understand.

## Expected Evidence

Each completed mission should produce:

- patch/diff
- runtime log
- test or verification result
- screenshot or UI evidence when relevant
- Memory Ledger entry with sha256 hashes

Evidence is stored under:

```text
s3://aios-vault/<MISSION_ID>/
```

## Pilot Rules

- Do not paste secrets into prompts.
- Use approved test repositories first.
- Stop the mission and report if the Reality Panel shows an unexpected organ.
- Report `RESOURCE_EXHAUSTED` events; they are expected during Codex Plan Core quota fallback testing.

## Useful Commands

```powershell
kubectl -n aios-prod get pods
kubectl -n aios-prod logs deployment/edge-gateway
kubectl -n aios-prod logs deployment/fabric-router
```
