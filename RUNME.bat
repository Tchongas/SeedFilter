@echo off
setlocal

title Seed Filter

:: Move to the folder where this script is located
cd /d "%~dp0"

:: Enter the project subfolder
cd /d "SeedFilter"

:: Create a Desktop shortcut on first run
if not exist "%USERPROFILE%\Desktop\SeedFilter.lnk" (
    powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $sc = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\SeedFilter.lnk'); $sc.TargetPath = '%~dp0RUNME.bat'; $sc.WorkingDirectory = '%~dp0'; $sc.IconLocation = '%~dp0SeedFilter\icon.ico,0'; $sc.Save()" >nul 2>&1
)

:: Verify Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found.
    echo Install Python and add it to your PATH.
    pause
    exit /b 1
)

:: Launch the UI
python goats_filter_ui.py

if errorlevel 1 (
    echo.
    echo Seed Filter exited with an error.
    pause
)
