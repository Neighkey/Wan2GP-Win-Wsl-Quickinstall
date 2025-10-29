@echo off
REM WGP Manager - Windows Launcher
REM Double-click this file to open WGP Manager in WSL Ubuntu

echo Starting WGP Manager in WSL Ubuntu...
echo.

REM Run the wgp_manager.sh script in WSL
wsl bash -c "~/wgp_manager.sh"

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)

