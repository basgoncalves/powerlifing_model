# Code Directory

This directory contains the source code and setup scripts for the powerlifting model project.

## Files

- `msk_setup.bat`: Installation script for setting up the MSK modelling environment
  - Automatically installs Python 3.8.10 via Windows Package Manager or direct download
  - Installs uv package manager
  - Installs msk_modelling_python
  - Provides instructions for OpenSim installation

## Usage

To set up your development environment, run:
```bash
msk_setup.bat
```

## Installation Methods

The setup script uses multiple methods to install Python automatically:

1. **Windows Package Manager (winget)** - Modern, preferred method for Windows 10/11
2. **Direct Download** - Downloads and runs the official Python installer
3. **Manual Installation** - Fallback with clear instructions if automatic methods fail

For easier manual installation, you can place the Python installer (`python-3.8.10-amd64.exe`) in the same directory as the setup script.

## Requirements

- Windows operating system (for .bat script)
- Internet connection for downloading packages
- Administrator privileges may be required for some installations