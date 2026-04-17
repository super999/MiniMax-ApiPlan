@echo off
setlocal

cd /d "%~dp0.."

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0branch_menu.ps1"
set EXIT_CODE=%ERRORLEVEL%

if not "%EXIT_CODE%"=="0" (
  echo.
  echo Branch switch script failed with exit code %EXIT_CODE%.
)

pause
endlocal
exit /b %EXIT_CODE%