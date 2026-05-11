# RC23 — Codex Delegated Auth Boundary

## Objetivo
Adicionar um estado operacional para o caminho `codex_delegated`, permitindo validar a fronteira de autenticacao Codex/ChatGPT sem pedir API key ao usuario e sem ler o conteudo de `auth.json`.

## Endpoint
```http
GET /codex/delegated-auth/status
```

## Garantias
- `auth.json` nao e lido pelo AIOS.
- Valores de token nao sao impressos, copiados, retornados para o frontend ou enviados para logs.
- Presenca de `auth.json` nao ativa `canInvokeLiveRuntime`.
- O runtime live continua dependendo do Runtime Binding Gate oficial.
- `auth.json` dentro do repositorio e tratado como bloqueio operacional.

## Estado Retornado
Campos principais:
- `phase: RC23_CODEX_DELEGATED_AUTH_BOUNDARY`
- `provider: codex_delegated`
- `authMode: chatgpt_managed`
- `authJsonManagedByAIOS: false`
- `authJsonContentRead: false`
- `apiKeyStoredByAIOS: false`
- `tokenValuesExposed: false`
- `canInvokeLiveRuntime: false`
- `readyForEnterpriseValidation: true|false`

## UI
O Workbench mostra o painel **Codex Auth RC23** com:
- modo de auth;
- status de `auth.json`;
- confirmacao de que o AIOS nao armazena API key;
- local seguro simbolico `%CODEX_HOME%\auth.json`;
- limite claro: `nao altera canInvokeLiveRuntime`.

## Validacao
```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2\backend
..\.venv\Scripts\python.exe -m pytest .\tests\test_api.py -q -k rc23

cd C:\AIOS\aios-codex-unlimited-enterprise-v2\frontend
npm run test:e2e -- --grep "logs in" --reporter=line
```

## Regra de Seguranca
Este RC nao autoriza copiar `auth.json`, compartilhar tokens, usar proxy OAuth nao oficial ou transformar auth local em desbloqueio de runtime. Ele apenas torna a fronteira de seguranca auditavel na API e no Workbench.
