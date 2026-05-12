@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==========================================
echo  AIOS RC33 - Parar Demo Real Local
echo ==========================================
echo.
echo Parando backend/frontend do AIOS.
echo O Ollama fica aberto para nao interromper outros usos locais.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-stop-local-demo.ps1"
echo.
pause
