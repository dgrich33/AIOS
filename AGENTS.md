# AIOS Codex Unlimited - Agent Instructions

This repository is the AIOS Codex Unlimited prototype. It is separate from DgLaucher.

## Product rules

- The product unit is Codex sessions, not tokens.
- Do not add visible token counters, token balances, weekly token quotas, or credit packages.
- Preserve the message: "Codex sem limites. Desenvolvimento sem interrupções."
- Treat the official Codex runtime as an adapter boundary. The local adapter is a demo implementation.

## Safety rules

- Do not commit real secrets.
- Do not expose admin tokens or service tokens in frontend code.
- Use `.env.example` for configuration examples.
- Keep Vault in dev mode only for local demo.
- Keep changes incremental and testable.

## Contract authority

The following files are sovereign contract/meeting documents for this project:

- `docs/legal/11_PEDIDO_DE_ACESSO_OFICIAL_DE_INTEGRACAO.md`
- `docs/AIOS_CODEX_UNLIMITED_BRIEFING_REUNIAO.md`

Do not edit, correct, reinterpret, summarize into replacement text, or override these files unless the user explicitly authorizes that exact edit in the current conversation.

Use this command to verify the contract documents:

```powershell
.\scripts\contract-authority.ps1 verify
```

Use this command only after the user approves the current text as final:

```powershell
.\scripts\contract-authority.ps1 lock -IUnderstandThisChangesContractHashes
```

## Validation

Preferred local checks:

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
python -m pip install -r .\backend\requirements.txt
python -m pytest .\backend\tests -q
cd .\frontend
npm install
npm run build
cd ..\mcp\aios-mcp-repo
npm install
npm run build
cd ..\aios-mcp-core
npm install
npm run build
```

Full stack validation requires Docker Desktop:

```powershell
.\scripts\doctor.ps1
docker compose up -d --build
.\scripts\enterprise-check.ps1
```
