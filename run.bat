@echo off

:: Run the seedfinding executable.
:: Usage: run.bat [threads]

setlocal
cd /d "%~dp0"

if not exist seed.exe (
    echo.
    echo seed.exe was not found.
    echo Run compile.bat first, or use goats.bat for the full menu.
    pause
    exit /b 1
)

set "threads=%~1"
if "%threads%"=="" set "threads=1"

echo.
echo Running with %threads% thread^(s^)...
seed.exe %threads%

echo.
echo Filter finished.
pause
