@echo off
REM =========================================
REM MSK Modelling Setup Script
REM =========================================
REM This script automates the installation of required software for MSK modelling:
REM - Python 3.8.10 (automatic installation via winget or direct download)
REM - uv (Python package manager)
REM - msk_modelling_python package
REM - OpenSim installation guidance (manual installation required)
REM =========================================

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

REM =========================================
REM PYTHON INSTALLATION SECTION
REM =========================================
REM Check if Python 3.8.10 is already installed
python --version 2>&1 | findstr "3.8.10" >nul
if %errorlevel% == 0 (
    echo Python 3.8.10 is already installed
) else (
    echo Installing Python 3.8.10...
    echo.
    echo Attempting automatic installation...
    
    REM Method 1: Try Windows Package Manager (winget) first (Windows 10/11)
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
    
    REM Method 2: Direct download and installation from Python.org
    echo.
    echo Detecting system architecture...
    
    REM Detect system architecture (32-bit vs 64-bit) for correct installer download
    set ARCH=amd64
    set PYTHON_URL=https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
    set PYTHON_INSTALLER=%TEMP%\python-3.8.10-amd64.exe
    
    REM Check for AMD64 architecture (64-bit)
    if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
        echo Detected 64-bit system
        goto :arch_detected
    )
    
    REM Check for x86 architecture (32-bit or WOW64)
    if "%PROCESSOR_ARCHITECTURE%"=="x86" (
        if "%PROCESSOR_ARCHITEW6432%"=="AMD64" (
            echo Detected 64-bit system ^(WOW64^)
            goto :arch_detected
        ) else (
            set ARCH=win32
            set PYTHON_URL=https://www.python.org/ftp/python/3.8.10/python-3.8.10.exe
            set PYTHON_INSTALLER=%TEMP%\python-3.8.10.exe
            echo Detected 32-bit system
            goto :arch_detected
        )
    )
    
    REM Default to 64-bit if architecture detection fails
    echo Warning: Unknown architecture %PROCESSOR_ARCHITECTURE%, defaulting to 64-bit
    
    :arch_detected
    
    REM Download Python installer from official Python.org
    echo Downloading Python 3.8.10 installer for %ARCH%...
    
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"
    if %errorlevel% == 0 (
        echo Running Python installer...
        echo NOTE: Please ensure you check 'Add Python to PATH' during installation
        REM Run installer with silent installation parameters
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
    
    REM =========================================
    REM MANUAL INSTALLATION FALLBACK
    REM =========================================
    REM Provide manual installation instructions if automatic methods fail
    echo.
    echo =========================================
    echo Manual Installation Required
    echo =========================================
    echo Automatic installation failed. Please:
    echo 1. Download Python 3.8.10 from: https://www.python.org/downloads/release/python-3810/
    echo    - For 64-bit systems: python-3.8.10-amd64.exe
    echo    - For 32-bit systems: python-3.8.10.exe
    echo 2. Run the installer and make sure to check 'Add Python to PATH'
    echo 3. Restart this script after installation
    echo.
    echo TIP: You can also place the Python installer in the same directory as this script
    echo      Your system architecture: %ARCH%
    echo      Required installer: %PYTHON_INSTALLER%
    pause
    exit /b 1
    
    :python_installed
    echo Python installation completed.
    echo.
)

REM =========================================
REM UV PACKAGE MANAGER INSTALLATION
REM =========================================
REM Install uv package manager for faster Python package management
echo.
echo Installing uv package manager...
pip install uv
if %errorlevel% neq 0 (
    echo Failed to install uv. Please check your Python installation.
    pause
    exit /b 1
)

REM =========================================
REM MSK MODELLING PYTHON PACKAGE INSTALLATION
REM =========================================
REM Install the main MSK modelling Python package
echo.
echo Installing msk_modelling_python...
uv pip install msk_modelling_python
if %errorlevel% neq 0 (
    echo Failed to install msk_modelling_python. Trying with pip...
    pip install msk_modelling_python
)

REM =========================================
REM OPENSIM INSTALLATION INSTRUCTIONS
REM =========================================
REM OpenSim requires manual installation - provide clear instructions
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

REM =========================================
REM INSTALLATION VERIFICATION
REM =========================================
REM Verify that all components were installed correctly
echo.
echo =========================================
echo Verification
echo =========================================
echo Checking installations...

REM Check Python installation
python --version
if %errorlevel% neq 0 (
    echo WARNING: Python not found in PATH
)

REM Check uv installation
uv --version
if %errorlevel% neq 0 (
    echo WARNING: uv not found
)

REM Check OpenSim Python bindings
python -c "import opensim; print('OpenSim version:', opensim.GetVersion())" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: OpenSim Python bindings not found
)

REM =========================================
REM SETUP COMPLETION
REM =========================================
echo.
echo Setup complete! 
echo Make sure all components are properly installed before proceeding.
pause