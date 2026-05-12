@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==========================================
echo  AIOS RC27 - Abrir Demo Local
echo ==========================================
echo.
echo Este launcher inicia o backend, inicia o Workbench e abre o navegador.
echo Nao envia nada para GitHub e nao le segredos locais.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-start-local-demo.ps1"
echo.
echo Se o navegador nao abriu, acesse:
echo http://127.0.0.1:5173
echo.
pause
