@echo off
echo =========================================
echo MSK Modelling Setup Script
echo =========================================
echo.
echo This script will install the required software for MSK modelling:
echo - Python 3.8.10 (automatic installation via winget or direct download)
echo - uv (Python package manager)
echo - msk_modelling_python
echo - OpenSim (manual installation required)
echo.

REM Check if Python 3.8.10 is already installed
python --version 2>&1 | findstr "3.8.10" >nul
if %errorlevel% == 0 (
    echo Python 3.8.10 is already installed
) else (
    echo Installing Python 3.8.10...
    echo.
    echo Attempting automatic installation...
    
    REM Try winget first (Windows 10/11)
    winget --version >nul 2>&1
    if %errorlevel% == 0 (
        echo Using Windows Package Manager (winget)...
        winget install Python.Python.3.8 --version 3.8.10 --silent
        if %errorlevel% == 0 (
            echo Python 3.8.10 installed successfully via winget
            goto :python_installed
        ) else (
            echo Winget installation failed, trying alternative method...
        )
    ) else (
        echo Windows Package Manager not available, trying alternative method...
    )
    
    REM Try direct download and installation
    echo.
    echo Downloading Python 3.8.10 installer...
    set PYTHON_URL=https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
    set PYTHON_INSTALLER=%TEMP%\python-3.8.10-amd64.exe
    
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
    if %errorlevel% == 0 (
        echo Running Python installer...
        echo NOTE: Please ensure you check 'Add Python to PATH' during installation
        "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
        if %errorlevel% == 0 (
            echo Python 3.8.10 installed successfully
            del "%PYTHON_INSTALLER%"
            goto :python_installed
        ) else (
            echo Automatic installation failed. Please install manually.
            del "%PYTHON_INSTALLER%"
        )
    ) else (
        echo Download failed. Please install manually.
    )
    
    REM Manual installation fallback
    echo.
    echo =========================================
    echo Manual Installation Required
    echo =========================================
    echo Automatic installation failed. Please:
    echo 1. Download Python 3.8.10 from: https://www.python.org/downloads/release/python-3810/
    echo 2. Run the installer and make sure to check 'Add Python to PATH'
    echo 3. Restart this script after installation
    echo.
    echo TIP: You can also place the Python installer (python-3.8.10-amd64.exe) 
    echo      in the same directory as this script for easier access
    pause
    exit /b 1
    
    :python_installed
    echo Python installation completed.
    echo.
)

REM Install uv package manager
echo.
echo Installing uv package manager...
pip install uv
if %errorlevel% neq 0 (
    echo Failed to install uv. Please check your Python installation.
    pause
    exit /b 1
)

REM Install msk_modelling_python
echo.
echo Installing msk_modelling_python...
uv pip install msk_modelling_python
if %errorlevel% neq 0 (
    echo Failed to install msk_modelling_python. Trying with pip...
    pip install msk_modelling_python
)

REM OpenSim installation instructions
echo.
echo =========================================
echo OpenSim Installation
echo =========================================
echo Please install OpenSim manually:
echo 1. Go to https://opensim.stanford.edu/downloads
echo 2. Download OpenSim 4.4 or later
echo 3. Follow the installation instructions for your operating system
echo 4. Make sure to install the Python bindings if you plan to use Python scripting
echo.

REM Verify installations
echo.
echo =========================================
echo Verification
echo =========================================
echo Checking installations...

python --version
if %errorlevel% neq 0 (
    echo WARNING: Python not found in PATH
)

uv --version
if %errorlevel% neq 0 (
    echo WARNING: uv not found
)

python -c "import opensim; print('OpenSim version:', opensim.GetVersion())" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: OpenSim Python bindings not found
)

echo.
echo Setup complete! 
echo Make sure all components are properly installed before proceeding.
pause