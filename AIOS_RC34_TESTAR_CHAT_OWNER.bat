@echo off
setlocal
cd /d "%~dp0"

set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%POWERSHELL_EXE%" set "POWERSHELL_EXE=powershell"

echo.
echo ==========================================
echo  AIOS RC34 - Teste de Chat no Terminal
echo ==========================================
echo.
echo Este teste abre o backend/frontend se necessario, faz login local,
echo cria uma sessao e envia uma mensagem ao Runtime Broker.
echo Nenhum segredo e lido ou impresso.
echo.

"%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File ".\scripts\rc34-owner-terminal-chat-test.ps1"

echo.
pause
