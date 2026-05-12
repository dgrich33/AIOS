# RC35 Production Overlay

This overlay is the internal-production target for AIOS Codex OS v1.1.

It declares the production surface expected by the RC35 rollout:

- `edge-gateway`
- `fabric-router`
- `aios-ui`
- compatibility deployments `aios-backend` and `aios-frontend`
- Router config and Sentinel DSL v0.3 ConfigMaps
- pilot read-only RBAC group `aios_pilot`

## Prerequisites

- Kubernetes context `aios-prod`.
- Registry access to `registry.aios.internal:5443`.
- Pull secret `aios-registry-pull-secret` created in namespace `aios-prod`.
- Secret `vault-creds` created in namespace `aios-prod` with `VAULT_BUCKET=s3://aios-vault`.
- AWS access via IRSA/web identity or restricted S3 credentials in `vault-creds`.
- Sentinel policy reviewed and loaded from `sentinel-policy.yaml`.

Secret templates are examples only:

```powershell
kubectl apply -f deploy/kustomize/prod/registry-pull-secret.example.yaml
kubectl apply -f deploy/kustomize/prod/vault-creds.example.yaml
```

Replace placeholder values before applying those templates to a real cluster.

## Preflight

```powershell
.\scripts\rc35-prod-preflight.ps1
```

The preflight checks tools, kube context, namespace reachability, S3/Vault config, and manifest rendering. It does not print secrets.

## Apply

```powershell
.\scripts\rc35-prod-deploy.ps1
```

Manual equivalent:

```bash
kubectl apply -k deploy/kustomize/prod/
kubectl -n aios-prod rollout status deployment/edge-gateway
kubectl -n aios-prod rollout status deployment/fabric-router
kubectl -n aios-prod rollout status deployment/aios-ui
```

Expected pods:

- `edge-gateway` Ready `1/1`
- `fabric-router` Ready `1/1`
- `aios-ui` Ready `1/1`

## Evidence Vault Smoke

Dry-run, local file vault:

```powershell
.\scripts\rc35-evidence-vault-smoke.ps1 -DryRun
```

Real S3 smoke, after `VAULT_BUCKET=s3://aios-vault` and AWS auth are configured:

```powershell
.\scripts\rc35-evidence-vault-smoke.ps1
```

## Release Tag

Only after production deploy and mission smoke pass:

```powershell
.\scripts\rc35-release-tag.ps1 -IConfirmProdSmokePassed
```
