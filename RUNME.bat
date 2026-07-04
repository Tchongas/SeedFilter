@echo off
setlocal

title Seed Filter

:: Move to the folder where this script is located
cd /d "%~dp0"

:: Verify Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python was not found.
    echo Install Python and add it to your PATH.
    pause
    exit /b 1
)

:: Install Python dependency if missing
python -c "import ttkbootstrap" >nul 2>&1
if errorlevel 1 goto install_ttkbootstrap
goto ttkbootstrap_ok

:install_ttkbootstrap
echo.
echo Installing missing Python dependency ttkbootstrap...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install ttkbootstrap.
    echo Make sure you are connected to the internet and Python is installed.
    pause
    exit /b 1
)

:ttkbootstrap_ok

:: Enter the project subfolder
cd /d "SeedFilter"

:: Create a Desktop shortcut on first run
if exist "%USERPROFILE%\Desktop\SeedFilter.lnk" goto shortcut_ok
powershell -NoProfile -Command "$WshShell = New-Object -ComObject WScript.Shell; $sc = $WshShell.CreateShortcut([System.Environment]::GetFolderPath('Desktop') + '\SeedFilter.lnk'); $sc.TargetPath = '%~dp0RUNME.bat'; $sc.WorkingDirectory = '%~dp0'; $sc.IconLocation = '%~dp0SeedFilter\icon.ico,0'; $sc.Save()" >nul 2>&1

:shortcut_ok

:: Launch the UI
python goats_filter_ui.py

if errorlevel 1 (
    echo.
    echo Seed Filter exited with an error.
    pause
)
