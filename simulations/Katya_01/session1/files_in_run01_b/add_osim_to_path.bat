@echo off
REM This script adds the specified OpenSim directory to the system PATH.
REM It must be run with Administrator privileges to modify the system PATH.

echo Adding "C:\OpenSim 4.5" to the system PATH...

REM Use setx with the /M flag to make the change for all users (system-wide).
setx PATH "%PATH%;C:\OpenSim 4.5" /M

if %errorlevel% equ 0 (
    echo.
    echo Successfully updated the system PATH.
    echo Please restart your command prompt or log off and on for the changes to take effect.
) else (
    echo.
    echo An error occurred. Please make sure you are running this script as an Administrator.
)

echo.
pause