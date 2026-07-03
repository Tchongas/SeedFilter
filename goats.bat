@echo off
setlocal enabledelayedexpansion

title GoATS - Minecraft Seed Finder

:: Move to the folder where this script is located
cd /d "%~dp0"

:: Verify that the submodules are actually present
if not exist "submodules\cubiomes\finders.c" (
    echo.
    echo ERROR: Cubiomes submodule is missing.
    echo Run: git submodule update --init --recursive
    pause
    exit /b 1
)
if not exist "submodules\sfmt\SFMT.c" (
    echo.
    echo ERROR: SFMT submodule is missing.
    echo Run: git submodule update --init --recursive
    pause
    exit /b 1
)

:menu
cls
echo =========================================
echo   GoATS - Minecraft Seed Finder
echo =========================================
echo.
echo [1] Configure filter  ^(config.py^)
echo [2] Compile seedfinder
echo [3] Run seedfinder
echo [4] Run lava checker
echo [5] Exit
echo.
set /p choice="Choose an option: "

if "%choice%"=="1" goto configure
if "%choice%"=="2" goto compile
if "%choice%"=="3" goto run
if "%choice%"=="4" goto lavachecker
if "%choice%"=="5" exit /b

goto menu

:configure
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found. Install Python and add it to PATH.
    pause
    goto menu
)

echo.
python config.py
if errorlevel 1 (
    echo.
    echo ERROR: config.py failed. Check the messages above.
    pause
)
goto menu

:compile
call compile.bat
if errorlevel 1 goto menu
goto menu

:run
if not exist seed.exe (
    echo.
    echo seed.exe not found. Compile first ^(option 2^).
    pause
    goto menu
)

echo.
set /p threads="Number of threads (default 1): "
if "!threads!"=="" set threads=1

call run.bat !threads!
goto menu

:lavachecker
where java >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Java was not found. Install Java 17+ and add it to PATH.
    pause
    goto menu
)

echo.
java -jar jar\lava_checker.jar
pause
goto menu
