# AIOS Codex Unlimited - Integration Readiness Scorecard

Legenda:

- OK = pronto e validado.
- PENDENTE = depende de dado, aprovacao ou credencial oficial.
- BLOQUEADO = nao deve seguir sem correcao.

| Item | Status | Responsavel | Evidencia |
|---|---|---|---|
| License.cert autorizado | OK | AIOS | Hash validado |
| Contratos soberanos travados | OK | AIOS | `contract-authority.ps1 verify` |
| Contract docs audit | OK | AIOS | `contract-docs-audit.ps1` |
| Backend tests | OK | AIOS | 29 passed |
| Frontend build | OK | AIOS | Vite build OK |
| MCP core/repo build | OK | AIOS | TypeScript build OK |
| Playwright smoke | OK | AIOS | 2 passed |
| Enterprise check | OK | AIOS | OK |
| Package scan | OK | AIOS | Sem item restrito no ZIP |
| Runtime Binding Gate | OK | AIOS | `/runtime/binding/status` |
| Secure Binding Store | OK | AIOS | DPAPI save/load OK |
| Endpoint oficial | PENDENTE | OpenAI/Codex | Necessario para runtime vivo |
| Service credential | PENDENTE | OpenAI/Codex | Escopos minimos definidos |
| Tenant/project/org | PENDENTE | OpenAI/Codex | Necessario para auditoria |
| Sandbox environment id | PENDENTE | OpenAI/Codex | Necessario para live flag |
| Vault/KMS oficial | PENDENTE | OpenAI/Codex + AIOS | Provider a confirmar |
| Live flag | PENDENTE | OpenAI/Codex | `AIOS_OFFICIAL_SANDBOX_LIVE_ENABLED=true` |
| Modelo `gpt-5.2-codex` | PENDENTE | OpenAI/Codex | Acesso a confirmar |
| Billing/spend/rate limits | PENDENTE | OpenAI/Codex | Ambiente sandbox/staging/producao |
| Auditoria oficial | PENDENTE | OpenAI/Codex | Destino e retencao |
| EXE/MSI assinado | PENDENTE | OpenAI/Codex | Release oficial |

## Criterio de Go para Sandbox Vivo

```txt
scopeReady: true
bindingState: active
canInvokeLiveRuntime: true
secretsExposed: false
```

## Criterio de Go para Producao Condicionada

- sandbox e staging aprovados;
- telemetria e redaction aprovadas;
- red-team review concluido;
- EXE/MSI/launcher assinados;
- rollback testado;
- runbook de incidente aprovado;
- contato de escalacao definido;
- signoff final da OpenAI/Codex e AIOS.
