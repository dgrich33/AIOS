# AIOS Foundry

`foundry.py` creates deterministic RC35 bootstrap organ artifacts in:

```text
deploy/registry/bootstrap/organs/
```

These artifacts let the router and Reality Panel exercise the signed `.organ` flow offline. They are marked `replaceBeforeProduction=true` and must be replaced by secured Foundry output before any production release.

