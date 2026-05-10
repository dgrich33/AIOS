# AIOS Codex Unlimited RC3 - Final Status

## Version

RC3 - Secure Codex Integration and Windows Release Channel

## Purpose

RC3 turns the post-approval direction into safe product systems:

- Secure Runtime Bridge for official Codex runtime integration.
- Identity Profiles for licensed users and runtime access mode.
- Integration Guardrails that block unsafe/private-artifact operations.
- Local-first Context Engine interface.
- Skill Store with permissioned professional skills.
- Windows Release manifest and portable launcher.

## Status apos contrato assinado

O contrato assinado de 9 de maio de 2026 substitui a lista antiga de bloqueios absolutos da RC3.

O estado vigente e:

- Patch de runtime protegido foi aprovado nas condicoes do contrato.
- Sandbox com dados reais foi aprovado nas condicoes do contrato.
- Acesso tecnico restrito, checkpoints, pesos e codigo-fonte interno seguem o escopo e os controles do documento soberano.
- `auth.json`, troca de contas e multi-account continuam proibidos para bypass/evasao; podem existir apenas para diagnostico, migracao autorizada ou vinculacao enterprise quando cobertos pelo contrato.
- Build publico de usuario final e ambiente protegido de desenvolvedor/sandbox devem seguir as regras de distribuicao e controles do contrato.

Fonte soberana:

```txt
docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md
```

## New Endpoints

- `GET /policy/integration/guardrails`
- `GET /identity/profiles`
- `GET /codex/secure-runtime/bridge`
- `POST /codex/secure-runtime/request`
- `GET /context/index`
- `POST /context/index`
- `POST /context/query`
- `GET /skill-store`
- `GET /skill-store/{skill_id}`
- `GET /release/windows/manifest`

## Windows Launcher

Portable launcher:

```powershell
C:\AIOS\aios-codex-unlimited-enterprise-v2\AIOS-Codex-Unlimited.cmd
```

It starts the local backend/frontend and opens the app. Packaging policy follows the signed contract and the current RC packaging scripts exclude secrets, local databases, logs, virtualenvs and generated dependency folders.

## Validation

Current local validation completed:

- Backend tests: `11 passed`
- Frontend build: passed
- Playwright: `2 passed`
- MCP repo build: passed
- MCP core build: passed
- `enterprise-check.ps1`: passed
- `rc2-validate.ps1`: passed
- `rc3-validate.ps1`: passed
- Validation report: `release/RC3_VALIDATION_REPORT.md`
- ZIP package target: `C:\AIOS\aios-codex-unlimited-enterprise-v2-RC3.zip`

Run:

```powershell
Set-Location C:\AIOS\aios-codex-unlimited-enterprise-v2
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\rc1-start-local.ps1
.\scripts\rc3-validate.ps1
```

Full validation:

```powershell
python -m pytest .\backend\tests -q
cd .\frontend
npm run build
npm run test:e2e
cd ..\mcp\aios-mcp-repo
npm run build
cd ..\aios-mcp-core
npm run build
cd ..\..
.\scripts\enterprise-check.ps1
.\scripts\rc2-validate.ps1
.\scripts\rc3-validate.ps1
.\scripts\rc3-package.ps1
```

## Demo

1. Open `http://127.0.0.1:5173`.
2. Show Product Manifest, Secure Runtime Bridge, Identity Profiles, Context Engine, Skill Store and Windows Release.
3. Create a session.
4. Click `Solicitar Bridge Seguro`.
5. Show the event in Workbench.
6. Open API docs and show RC3 endpoints.

## Next Step

Build the real `OfficialCodexRuntimeAdapter` against approved runtime endpoints and credentials, then replace the local queue execution path without changing the user-facing session-based product model.
