# RC35 Production Operations

## Current Goal

Move AIOS Codex OS v1.1 Sovereign + Codex Plan Bridge from merged code to internal production operation.

The production sequence is gated. Do not tag `v1.1.0` until cluster deploy, Evidence Vault smoke, and mission smoke have all passed.

## Sequence

1. Install local tools: `kubectl`, `kustomize`, `aws`, `make`, and `aiosctl`.
2. Configure `KUBECONFIG` with context `aios-prod`.
3. Configure S3 access through IRSA/web identity or restricted credentials.
4. Create `aios-registry-pull-secret` and `vault-creds` in namespace `aios-prod`, either out-of-band or with `.\scripts\rc35-prod-deploy.ps1 -CreateClusterSecrets`.
5. Run:

```powershell
.\scripts\rc35-prod-preflight.ps1
```

6. Deploy. If the cluster secrets already exist:

```powershell
.\scripts\rc35-prod-deploy.ps1
```

If the rollout machine should create/update the cluster secrets first:

```powershell
$env:VAULT_BUCKET = "s3://aios-vault"
# Optional when Docker login state is not already present.
# $env:AIOS_REGISTRY_DOCKERCONFIGJSON = Get-Content -Raw "$HOME\.docker\config.json"
.\scripts\rc35-prod-deploy.ps1 -CreateClusterSecrets
```

The script pipes generated Kubernetes Secret YAML to `kubectl apply -f -`. It does not persist the secret payload in the repository.

7. Build and publish beta organs from a GPU machine:

```bash
cd aios-codex-foundry
make build-beta-organs
aiosctl organ push out/*.organ
```

8. Run Evidence Vault smoke:

```powershell
.\scripts\rc35-evidence-vault-smoke.ps1
```

9. Run mission smoke:

```bash
aiosctl mission new --repo https://github.com/openai/sample-auth --goal "Refatorar auth e corrigir rotas duplicadas"
```

10. Tag release:

```powershell
.\scripts\rc35-release-tag.ps1 -IConfirmProdSmokePassed
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
