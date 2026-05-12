@echo off
setlocal
cd /d "%~dp0"

set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%POWERSHELL_EXE%" set "POWERSHELL_EXE=powershell"
set "CODEX_CLI_BIN=%LOCALAPPDATA%\OpenAI\Codex\bin"
if exist "%CODEX_CLI_BIN%\codex.exe" set "PATH=%CODEX_CLI_BIN%;%PATH%"
set "AIOS_OWNER_BACKEND_PORT=8026"
set "AIOS_OWNER_FRONTEND_PORT=5176"

echo.
echo ==========================================
echo  AIOS RC34 - Product Owner Live Workbench
echo ==========================================
echo.
echo Esta versao carrega .env.local.private apenas nesta maquina.
echo O arquivo privado escolhe o provider:
echo   - codex_cli_local_developer para conversar com modelo real via Codex CLI
echo   - aios_native_runtime para camada AIOS Native sem API key, sem auth.json e sem endpoint externo
echo   - openai_api_authorized para gpt-4o / gpt-5.2-codex / gpt-5.5 com OPENAI_API_KEY
echo   - community_wrapper_runtime para Ollama/local OpenAI-compatible
echo.

set AIOS_ENV=local_developer
set AIOS_PRESENTATION_MODE=true
set AIOS_LOCAL_ONLY=true
set AIOS_ALLOW_GITHUB_PUSH=false
set AIOS_PUBLIC_RELEASE=false
set AIOS_REQUIRE_APPROVAL_GATE=true
set AIOS_SECRETS_EXPOSED=false
set AIOS_CHAT_PROVIDER=codex_cli_local_developer
set AIOS_ALLOW_CODEX_CLI_RUNTIME=true
set AIOS_CODEX_CLI_MODEL=gpt-5.5
set AIOS_NATIVE_RUNTIME_ENABLED=true
set AIOS_NATIVE_RUNTIME_MODEL=aios-native-fabric-v1

if not exist ".env.local.private" (
  echo AVISO: .env.local.private nao existe.
  echo Criando fallback local privado para modelo real via Codex CLI.
  > ".env.local.private" echo AIOS_ENV=local_developer
  >> ".env.local.private" echo AIOS_PRESENTATION_MODE=true
  >> ".env.local.private" echo AIOS_LOCAL_ONLY=true
  >> ".env.local.private" echo AIOS_ALLOW_GITHUB_PUSH=false
  >> ".env.local.private" echo AIOS_PUBLIC_RELEASE=false
  >> ".env.local.private" echo AIOS_DATABASE_URL=sqlite:///./aios_local_private.db
  >> ".env.local.private" echo AIOS_RUNTIME_PROVIDER=auto
  >> ".env.local.private" echo AIOS_CHAT_PROVIDER=codex_cli_local_developer
  >> ".env.local.private" echo AIOS_ALLOW_CODEX_CLI_RUNTIME=true
  >> ".env.local.private" echo AIOS_CODEX_CLI_MODEL=gpt-5.5
  >> ".env.local.private" echo AIOS_NATIVE_RUNTIME_ENABLED=true
  >> ".env.local.private" echo AIOS_NATIVE_RUNTIME_MODEL=aios-native-fabric-v1
  >> ".env.local.private" echo AIOS_ALLOW_OPENAI_API_RUNTIME=true
  >> ".env.local.private" echo AIOS_REQUIRE_APPROVAL_GATE=true
  >> ".env.local.private" echo AIOS_SECRET_STORAGE=env_or_os_keychain
  >> ".env.local.private" echo AIOS_SECRETS_EXPOSED=false
)

echo Verificando Codex CLI local para modelo real...
"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Command codex -ErrorAction SilentlyContinue) { codex --version; exit 0 } else { exit 1 }"
if errorlevel 1 (
  echo AVISO: Codex CLI nao encontrado no PATH. O app ainda abrira, mas o chat real via Codex CLI precisa do codex instalado/autenticado.
)

"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -Command "if (Get-Command ollama -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }" >nul 2>nul
if not errorlevel 1 (
  echo Garantindo servidor Ollama em http://127.0.0.1:11434 ...
  "%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null } catch { Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden; Start-Sleep -Seconds 5 }"
) else (
  echo Ollama nao encontrado. Se usar OpenAI API autorizada, isso nao impede a demo.
)

echo Parando AIOS anterior para evitar backend antigo...
"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -Command "& '.\scripts\rc27-stop-local-demo.ps1' -BackendPort @(8000,8010,%AIOS_OWNER_BACKEND_PORT%) -FrontendPort @(5173,5174,%AIOS_OWNER_FRONTEND_PORT%)"

echo Abrindo AIOS Product Owner:
echo Frontend: http://127.0.0.1:%AIOS_OWNER_FRONTEND_PORT%
echo Backend:  http://127.0.0.1:%AIOS_OWNER_BACKEND_PORT%/docs
echo Config:   .env.local.private
echo.
"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-start-local-demo.ps1" -BackendPort %AIOS_OWNER_BACKEND_PORT% -FrontendPort %AIOS_OWNER_FRONTEND_PORT% -ForceRestart

echo.
echo Login:
echo   Email: admin@aios.local
echo   Senha: AiosAdmin123!
echo.
echo Para testar: use o painel "AIOS Chat Principal" no topo e clique em "Enviar para runtime real".
echo.
pause
