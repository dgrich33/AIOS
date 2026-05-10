# Runbook - Runtime e Operacoes

## Objetivo

Operar o AIOS Codex Unlimited em modo local, sandbox e staging autorizado, validando o runtime binding sem simular credenciais reais.

## Fluxo normal

1. Validar contrato:

```powershell
.\scripts\contract-authority.ps1 verify
.\scripts\contract-docs-audit.ps1
```

2. Carregar binding local se existir:

```powershell
.\scripts\runtime-binding-load-local.ps1 -WriteReport
```

3. Iniciar:

```powershell
.\scripts\stop.ps1
.\scripts\start.ps1 -Mode Local
```

4. Validar runtime binding:

```powershell
.\scripts\runtime-binding-status.ps1 -WriteReport
```

## Estados esperados

| Estado | Significado |
|---|---|
| `awaiting_secure_runtime_binding` | Escopo aprovado, mas faltam dados reais. |
| `active` | Escopo e binding tecnico prontos para runtime vivo. |
| `blocked_by_scope` | Contrato, license.cert ou lock nao conferem. |

## Readiness adicional

```powershell
.\scripts\rc11-runtime-readiness.ps1
.\scripts\rc12-runtime-broker-readiness.ps1
.\scripts\enterprise-check.ps1
```

## Rollback

1. Parar processos:

```powershell
.\scripts\stop.ps1
```

2. Remover binding local DPAPI se a credencial tiver sido revogada:

```powershell
Remove-Item -LiteralPath ".\.aios-secure\runtime-binding.dpapi.json" -Force
```

3. Reiniciar em modo local sem runtime vivo:

```powershell
.\scripts\start.ps1 -Mode Local
```

## Criterios de aceite operacional

- Frontend abre em `http://127.0.0.1:5173`.
- Backend docs abre em `http://127.0.0.1:8000/docs`.
- `/runtime/binding/status` responde sem expor segredo.
- `/entitlement/me` retorna `productUnit: codex_sessions`.
- Workbench mostra sessoes, eventos, snapshots, handoff e runtime status.
