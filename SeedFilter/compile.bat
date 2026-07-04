@echo off
setlocal enabledelayedexpansion

:: Build the seedfinding executable on Windows.
:: Requires gcc (MinGW/TDM-GCC/MSYS2) and the Cubiomes + SFMT submodules.

cd /d "%~dp0"

where gcc >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: gcc was not found.
    echo Install MinGW, TDM-GCC, or MSYS2 and add the bin folder to your PATH.
    pause
    exit /b 1
)

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

echo.
echo Compiling seedfinder...

:: Collect all source files, expanding wildcards ourselves.
:: TDM-GCC on Windows does not always expand *.c in arguments.
set "SRC_FILES=main.c"
for %%f in (filters\*.c) do set "SRC_FILES=!SRC_FILES! %%f"
for %%f in (logic\*.c) do set "SRC_FILES=!SRC_FILES! %%f"
for %%f in (util\*.c) do set "SRC_FILES=!SRC_FILES! %%f"
for %%f in (submodules\cubiomes\*.c) do (
    if /I not "%%~nxf"=="tests.c" (
        set "SRC_FILES=!SRC_FILES! %%f"
    )
)
set "SRC_FILES=!SRC_FILES! submodules\sfmt\SFMT.c"

gcc !SRC_FILES! -lm -pthread -Ofast -DSFMT_MEXP=19937 -g -mavx -Wno-format -o seed.exe

if errorlevel 1 (
    echo.
    echo ERROR: Compilation failed.
    pause
    exit /b 1
)

echo.
echo SUCCESS: built seed.exe
echo.
pause
