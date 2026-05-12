@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==========================================
echo  AIOS RC34 - Abrir Product Owner no VS Code
echo ==========================================
echo.
echo Tarefas criadas no VS Code:
echo   - AIOS RC34 Owner: Start Workbench
echo   - AIOS RC34 Owner: Test Real Chat gpt-5.5
echo   - AIOS RC34 Owner: Stop Workbench
echo.
echo URL da demo visual: http://127.0.0.1:5176
echo Guia: COMO_TESTAR_AIOS_RC34_PRODUCT_OWNER.md
echo.

where code >nul 2>nul
if errorlevel 1 (
  echo VS Code nao esta no PATH. Abra manualmente esta pasta:
  echo %CD%
  echo.
  pause
  exit /b 1
)

code "%CD%"
echo VS Code aberto. Use Terminal ^> Run Task para iniciar/testar o AIOS.
echo.
pause
