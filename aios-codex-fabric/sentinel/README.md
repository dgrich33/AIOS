# Policy Sentinel v0.3

The parser accepts the RC35 default rules:

```text
allow organ:codex.plan.core role:*
deny tool:TerminalRunner cmd:rm-recursive
limit rate codex.plan.core per_minute 30
```

`sentinel_dsl.py` compiles DSL into a signed-manifest-ready JSON file. The eBPF loader is intentionally represented as `manifest_only_until_kernel_loader_available` in this workstation build because no kernel eBPF toolchain is available locally.

