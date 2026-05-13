# RC35 Production Operations

## Current Goal

Move AIOS Codex OS v1.1 Sovereign + Codex Plan Bridge from merged code to internal production operation.

The production sequence is gated. Do not tag `v1.1.0` until cluster deploy, Evidence Vault smoke, and mission smoke have all passed.

## First Install

Use this sequence on the first rollout machine or any cluster where `vault-creds` and `aios-registry-pull-secret` do not exist yet.

1. Install local tools: `kubectl`, `kustomize`, `aws`, `make`, and `aiosctl`.
2. Configure `KUBECONFIG` with context `aios-prod`.
3. Configure S3 access through IRSA/web identity or restricted credentials.
4. Authenticate to `registry.aios.internal:5443` with Docker, or export `AIOS_REGISTRY_DOCKERCONFIGJSON`.
5. Create/update cluster secrets and apply the production overlay:

```powershell
$env:VAULT_BUCKET = "s3://aios-vault"
# Optional when Docker login state is not already present.
# $env:AIOS_REGISTRY_DOCKERCONFIGJSON = Get-Content -Raw "$HOME\.docker\config.json"
.\scripts\rc35-prod-deploy.ps1 -CreateClusterSecrets
```

The deploy script pipes generated Kubernetes Secret YAML to `kubectl apply -f -`. It does not persist the secret payload in the repository.

6. Confirm the environment is now all-green:

```powershell
.\scripts\rc35-prod-preflight.ps1
```

7. Run Evidence Vault smoke:

```powershell
.\scripts\rc35-evidence-vault-smoke.ps1
```

8. Run mission smoke:

```bash
aiosctl mission new --repo https://github.com/openai/sample-auth --goal "Refatorar auth e corrigir rotas duplicadas"
```

9. Tag release:

```powershell
.\scripts\rc35-release-tag.ps1 -IConfirmProdSmokePassed
```

## For later deployments

After the required cluster secrets exist, start with preflight:

```powershell
.\scripts\rc35-prod-preflight.ps1
.\scripts\rc35-prod-deploy.ps1
.\scripts\rc35-evidence-vault-smoke.ps1
.\scripts\rc35-release-tag.ps1 -IConfirmProdSmokePassed
```

If preflight reports `MISSING SECRETS`, rerun:

```powershell
.\scripts\rc35-prod-deploy.ps1 -CreateClusterSecrets
```

## Beta Organ Publication

Build and publish beta organs from a GPU machine:

```bash
cd aios-codex-foundry
make build-beta-organs
aiosctl organ push out/*.organ
```

## Production Readiness Checks

- Pods `edge-gateway`, `fabric-router`, and `aios-ui` are Ready `1/1`.
- Reality Panel shows `codex_plan_bridge` when Codex Plan Core is available.
- Hot-swap fallback to `aios_code.beta.organ` works when Codex Plan Core is unavailable or rate-limited.
- Evidence Vault writes files to `s3://aios-vault/<MISSION_ID>/`.
- Ledger records sha256 for uploaded evidence.
- Sentinel DSL v0.3 contains:

```text
allow organ:codex.plan.core role:*
deny  tool:TerminalRunner cmd:rm-recursive
limit rate codex.plan.core per_minute 30
```

## Security Sign-Off Packet

Before internal pilot expansion, export:

- first three mission IDs
- `sentinel_audit.csv`
- Evidence Vault object list
- Ledger records for each evidence item
- Reality Panel screenshot showing bridge and fallback states

Security/risk owner records `security_review_passed=true` in the project Memory Ledger after review.

## Honest Status Rules

- `codex_plan_bridge` is a delegated organ, not an embedded model.
- `beta_open_weight` bootstrap artifacts are operational placeholders until secured Foundry training output replaces them.
- `official-capsule` remains future-ready and must not be claimed live until a real capsule is provisioned.
