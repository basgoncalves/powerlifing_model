@echo off
echo =========================================
echo MSK Modelling Setup Script
echo =========================================
echo.
echo This script will install the required software for MSK modelling:
echo - Python 3.8.10
echo - uv (Python package manager)
echo - msk_modelling_python
echo - OpenSim
echo.

REM Check if Python 3.8.10 is already installed
python --version 2>&1 | findstr "3.8.10" >nul
if %errorlevel% == 0 (
    echo Python 3.8.10 is already installed
) else (
    echo Installing Python 3.8.10...
    echo Please download and install Python 3.8.10 from https://www.python.org/downloads/release/python-3810/
    echo Make sure to add Python to your PATH during installation
    pause
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