# RC35 registry bootstrap

This directory is the offline bootstrap mirror for organ manifests and signed metadata.

The configured production registry is:

```text
registry.aios.internal:5443
```

On this workstation the registry hostname is not reachable, so local validation uses this directory as the deterministic publish target. A real OCI push is performed only when registry credentials and DNS are available.

