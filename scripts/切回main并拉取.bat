@echo off
REM 切回 main 分支并拉取远端更新
setlocal enableextensions enabledelayedexpansion

REM 将当前目录切换到脚本所在目录的上一级（假定 scripts 在仓库根目录下）
cd /d "%~dp0\.."

echo 当前路径: %CD%
echo.
echo 切换到 main 分支...
git checkout main
if %ERRORLEVEL% neq 0 (
  echo git checkout main 失败
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo 从远端拉取更新...
git pull
if %ERRORLEVEL% neq 0 (
  echo git pull 失败
  pause
  exit /b %ERRORLEVEL%
)

echo.
echo 更新完成。
pause
endlocal
exit /b 0
