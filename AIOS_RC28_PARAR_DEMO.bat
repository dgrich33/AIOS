@echo off
setlocal
cd /d "%~dp0"
echo.
echo ==========================================
echo  AIOS RC28 - Parar Demo Local
echo ==========================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc27-stop-local-demo.ps1"
echo.
pause
