@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==========================================
echo  AIOS RC31 - Abrir Demo Local
echo ==========================================
echo.
echo Frontend: http://127.0.0.1:5174
echo Backend:  http://127.0.0.1:8010/docs
echo.
echo RC31 inclui:
echo - Community Wrapper Runtime via variaveis locais
echo - Community Wrapper Runtime via .env.local.private ignorado pelo Git
echo - Painel de validacao e smoke test real no Workbench
echo - Indice completo do projeto em docs\AIOS_FULL_PROJECT_INDEX_RC31.md
echo.
echo Nao envia nada para GitHub e nao inclui segredos no ZIP.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-start-local-demo.ps1" -BackendPort 8010 -FrontendPort 5174
echo.
echo Se o navegador nao abriu, acesse:
echo http://127.0.0.1:5174
echo.
pause
