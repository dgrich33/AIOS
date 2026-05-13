# RC36 Kubernetes 1.36 Upgrade

## Scope

This update prepares the RC35 internal-production rollout for Kubernetes `v1.36.1`.

## Changes

- `scripts/rc35-prod-preflight.ps1` now enforces Kubernetes client/server `>= v1.36.0`.
- Production image tags moved to `1.1-k8s1.36` for:
  - `aios/backend`
  - `aios/frontend`
  - `aios/edge-gateway`
  - `aios/fabric-router`
  - `aios/ui`
- Dockerfiles now include `org.opencontainers.image.base.name="k8s1.36"`.
- GitHub Actions now installs `kubectl v1.36.1`.
- CI records the requested Kind image as `kindest/node:v1.36.1`.

## Kind Image Availability

The Kubernetes tag `v1.36.1` exists upstream, but `kindest/node:v1.36.1` was not available on Docker Hub during implementation. CI keeps the requested value and falls back to `kindest/node:v1.35.0` only for the Kind smoke cluster if the requested image is still missing.

When `kindest/node:v1.36.1` becomes available, CI will use it automatically.

## Kustomize Compatibility Marker

The production overlay includes:

```yaml
metadata:
  annotations:
    aios.dev/kubeVersion: ">= 1.36.0"
```

This is an AIOS compatibility marker. The hard version gate remains in `rc35-prod-preflight.ps1` because top-level `kubeVersion` is not a portable Kustomize field outside Helm rendering paths.

## Rollout

```powershell
.\scripts\rc35-prod-deploy.ps1 -CreateClusterSecrets
.\scripts\rc35-prod-preflight.ps1
.\scripts\rc35-evidence-vault-smoke.ps1
.\scripts\rc35-release-tag.ps1 -IConfirmProdSmokePassed
```
