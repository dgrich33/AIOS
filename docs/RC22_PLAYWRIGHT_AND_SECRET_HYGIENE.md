# RC22 — Playwright Runner e Secret Hygiene

## Estado Corrigido
- O travamento local do Playwright foi isolado no encerramento do `webServer` com Vite no Windows.
- `frontend/playwright.config.js` agora usa `globalSetup` e `globalTeardown`.
- `frontend/tests/global-setup.mjs` sobe backend e frontend somente quando necessario.
- `frontend/tests/global-teardown.mjs` encerra os processos iniciados pelo teste com `taskkill /T /F` no Windows.
- A suite E2E passou e encerrou sem runner pendurado.

## Segredos e `auth.json`
- `auth.json` permanece classificado como segredo.
- O projeto nao le, copia, imprime, versiona ou empacota o conteudo de `auth.json`.
- `scripts/secret-hygiene-check.ps1` verifica apenas caminhos e estado Git, sem abrir o conteudo de arquivos sensiveis.
- `.gitignore` ja bloqueia `auth.json`, `.env`, stores DPAPI e formatos comuns de chave/certificado.

## Validacoes
```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2\frontend
npm run test:e2e -- --reporter=line

cd C:\AIOS\aios-codex-unlimited-enterprise-v2
.\scripts\secret-hygiene-check.ps1 -WriteReport
```

## Resultado Esperado
- Playwright: 2 passed, processo encerrado.
- Secret hygiene: `ok=true`, `trackedForbiddenCount=0`, `unignoredForbiddenCount=0`.
