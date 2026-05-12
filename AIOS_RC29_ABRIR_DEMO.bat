@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==========================================
echo  AIOS RC29 - Abrir Demo Local
echo ==========================================
echo.
echo Este launcher usa portas alternativas para evitar processos antigos presos:
echo Frontend: http://127.0.0.1:5174
echo Backend:  http://127.0.0.1:8010/docs
echo.
echo RC29 inclui todos os 112 links enviados no registry do AIOS.
echo Nao envia nada para GitHub e nao le segredos locais.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-start-local-demo.ps1" -BackendPort 8010 -FrontendPort 5174
echo.
echo Se o navegador nao abriu, acesse:
echo http://127.0.0.1:5174
echo.
pause
