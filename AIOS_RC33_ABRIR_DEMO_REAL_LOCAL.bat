@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==========================================
echo  AIOS RC33 - Demo Real Local
echo ==========================================
echo.
echo Esta demo usa runtime real local via Ollama/OpenAI-compatible API.
echo Segredos nao sao colocados no Git nem no ZIP.
echo.

set AIOS_ENV=local_developer
set AIOS_PRESENTATION_MODE=true
set AIOS_LOCAL_ONLY=true
set AIOS_ALLOW_GITHUB_PUSH=false
set AIOS_PUBLIC_RELEASE=false
set AIOS_RUNTIME_PROVIDER=auto
set AIOS_CHAT_PROVIDER=community_wrapper_runtime
set AIOS_ALLOW_COMMUNITY_RUNTIME=true
set AIOS_COMMUNITY_RUNTIME_BASE_URL=http://127.0.0.1:11434/v1
set AIOS_COMMUNITY_RUNTIME_MODEL_ID=qwen2.5-coder:1.5b
set AIOS_REQUIRE_APPROVAL_GATE=true
set AIOS_SECRETS_EXPOSED=false

where ollama >nul 2>nul
if errorlevel 1 (
  echo ERRO: Ollama nao foi encontrado no PATH.
  echo Instale/abra o Ollama e rode: ollama pull qwen2.5-coder:1.5b
  pause
  exit /b 1
)

echo Garantindo servidor Ollama em http://127.0.0.1:11434 ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null } catch { Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden; Start-Sleep -Seconds 5 }"

echo Parando AIOS anterior para evitar backend antigo sem runtime real...
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-stop-local-demo.ps1"

echo Abrindo AIOS:
echo Frontend: http://127.0.0.1:5174
echo Backend:  http://127.0.0.1:8010/docs
echo Modelo:   qwen2.5-coder:1.5b
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-start-local-demo.ps1" -BackendPort 8010 -FrontendPort 5174

echo.
echo Login:
echo   Email: admin@aios.local
echo   Senha: AiosAdmin123!
echo.
echo Para testar: digite no campo "Sessao Codex" e clique em "Chat runtime real".
echo.
pause
