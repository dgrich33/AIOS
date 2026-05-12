# AIOS Codex OS v1.1 - Production Kustomize Overlay

This overlay declares the production namespace, backend/frontend services, Router config, and Sentinel DSL v0.3 policy for the internal AIOS production cluster.

Apply only from a machine authenticated to the approved production cluster:

```powershell
kubectl apply -k deploy/kustomize/prod
```

Expected external prerequisites:

- `registry.aios.internal:5443/aios/backend:v1.1.0`
- `registry.aios.internal:5443/aios/frontend:v1.1.0`
- S3-compatible Evidence Vault access for `s3://aios-vault`
- Cluster-side secret management for database and runtime credentials
