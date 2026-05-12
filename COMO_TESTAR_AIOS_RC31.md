# Como testar o AIOS RC31

Use o caminho oficial:

```text
C:\AIOS\aios-codex-unlimited-enterprise-v2
```

## Abrir

De dois cliques:

```text
AIOS_RC31_ABRIR_DEMO.bat
```

URLs:

```text
Frontend: http://127.0.0.1:5174
Backend:  http://127.0.0.1:8010/docs
```

Login:

```text
Email: admin@aios.local
Senha: AiosAdmin123!
```

## Testar sem wrapper externo

1. Abra `AIOS Chat`.
2. Escolha `gpt-4o` ou `gpt-5.2-codex`.
3. Envie uma mensagem.
4. A resposta vem do `aios_native_runtime`.

## Testar wrapper real por variavel de ambiente

Abra PowerShell:

```powershell
cd C:\AIOS\aios-codex-unlimited-enterprise-v2
$env:AIOS_CHAT_PROVIDER="community_wrapper_runtime"
$env:AIOS_ALLOW_COMMUNITY_RUNTIME="true"
$env:AIOS_COMMUNITY_RUNTIME_BASE_URL="http://127.0.0.1:11434/v1"
$env:AIOS_COMMUNITY_RUNTIME_MODEL_ID="gpt-oss:20b"
.\scripts\rc27-start-local-demo.ps1 -BackendPort 8010 -FrontendPort 5174
```

Se o wrapper exigir credencial:

```powershell
$env:AIOS_COMMUNITY_RUNTIME_API_KEY="valor-apenas-neste-terminal"
```

## Testar wrapper real por arquivo privado

1. Copie:

```text
.env.local.private.example
```

2. Crie:

```text
.env.local.private
```

3. Ajuste:

```env
AIOS_ENV=local_developer
AIOS_CHAT_PROVIDER=community_wrapper_runtime
AIOS_ALLOW_COMMUNITY_RUNTIME=true
AIOS_COMMUNITY_RUNTIME_BASE_URL=http://127.0.0.1:11434/v1
AIOS_COMMUNITY_RUNTIME_MODEL_ID=gpt-oss:20b
AIOS_COMMUNITY_RUNTIME_API_KEY=opcional-se-o-wrapper-exigir
```

4. Abra a demo com `AIOS_RC31_ABRIR_DEMO.bat`.

## Validar no Workbench

No Workbench, veja o card `RC31 Private Community Runtime` perto do painel `Runtime Broker RC21`.

Use:

- `Validar Wrapper`: confirma configuracao local sem mostrar segredo.
- `Smoke Test Vivo`: chama o wrapper configurado com prompt pequeno.

Para uma resposta real no chat do broker, clique em `Invocar Broker`. Se o `community_wrapper_runtime` estiver pronto, ele sera o provider recomendado e a resposta vira do seu endpoint privado.

## Preparar GPT OSS 20B local

Se for usar Ollama:

```powershell
ollama pull gpt-oss:20b
ollama run gpt-oss:20b
```

Depois mantenha `AIOS_COMMUNITY_RUNTIME_BASE_URL=http://127.0.0.1:11434/v1` e `AIOS_COMMUNITY_RUNTIME_MODEL_ID=gpt-oss:20b`.

## Parar

De dois cliques:

```text
AIOS_RC31_PARAR_DEMO.bat
```

## Arquivos de referencia

- `docs\RC31_PRIVATE_COMMUNITY_RUNTIME.md`
- `docs\AIOS_FULL_PROJECT_INDEX_RC31.md`
- `.env.local.private.example`
