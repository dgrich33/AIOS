@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==========================================
echo  AIOS RC30 - Abrir Demo Local
echo ==========================================
echo.
echo Caminho oficial desta demo:
echo %CD%
echo.
echo Frontend: http://127.0.0.1:5174
echo Backend:  http://127.0.0.1:8010/docs
echo.
echo RC30 inclui:
echo - AIOS Native Runtime funcional para chat demo
echo - GPT-4o e GPT-5.2-Codex ativos no registry local
echo - Registry com 112 links recebidos
echo - Community Wrapper Runtime opcional via variaveis locais
echo.
echo Nao envia nada para GitHub e nao le auth.json/.env.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-start-local-demo.ps1" -BackendPort 8010 -FrontendPort 5174
echo.
echo Se o navegador nao abriu, acesse:
echo http://127.0.0.1:5174
echo.
pause
