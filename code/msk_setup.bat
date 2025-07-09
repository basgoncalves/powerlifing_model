@echo off
REM MSK Modeling Setup Script for Powerlifting Model Project
REM This script installs Python 3.8.10, uv, msk_modelling_python, and OpenSim

echo Starting MSK Modeling Environment Setup...
echo.

REM Check if script is run as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as administrator.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Create temporary directory for downloads
if not exist "%TEMP%\msk_setup" mkdir "%TEMP%\msk_setup"
cd /d "%TEMP%\msk_setup"

echo Step 1: Installing Python 3.8.10...
echo.

REM Download Python 3.8.10 installer
curl -L -o python-3.8.10-amd64.exe https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe

REM Install Python 3.8.10 silently
echo Installing Python 3.8.10...
python-3.8.10-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

REM Wait for installation to complete
timeout /t 30 /nobreak

REM Refresh environment variables
call refreshenv.cmd

echo Step 2: Installing uv (Python package manager)...
echo.

REM Install uv using pip
python -m pip install --upgrade pip
python -m pip install uv

echo Step 3: Installing msk_modelling_python...
echo.

REM Install msk_modelling_python using uv
uv pip install msk_modelling_python

echo Step 4: Installing OpenSim...
echo.

REM Download OpenSim (assuming Windows installer)
REM Note: This URL should be updated with the actual OpenSim download link
echo Downloading OpenSim installer...
curl -L -o opensim-installer.exe "https://simtk-confluence.stanford.edu/download/attachments/8913574/OpenSim-4.4-win64.exe"

REM Install OpenSim
echo Installing OpenSim...
opensim-installer.exe /S

REM Install OpenSim Python bindings
echo Installing OpenSim Python bindings...
python -m pip install opensim

echo.
echo Setup complete!
echo.
echo The following have been installed:
echo - Python 3.8.10
echo - uv (Python package manager)
echo - msk_modelling_python
echo - OpenSim
echo.
echo Please restart your command prompt to ensure all environment variables are loaded.
echo.

REM Clean up temporary files
cd /d "%USERPROFILE%"
rmdir /s /q "%TEMP%\msk_setup"

pause