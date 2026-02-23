# Code Directory

This directory contains the source code and scripts for the powerlifting model project.

## Files

- `ceinms.py`: Main script for running CEINMS (Calibrated EMG-Informed Neuromusculoskeletal) modeling
- `openSim.py`: Script for OpenSim-based biomechanical analysis
- `msk_setup.bat`: Installation script for setting up the MSK modeling environment
  - Automatically installs Python 3.8.10 via Windows Package Manager or direct download
  - Installs uv package manager
  - Installs msk_modelling_python
  - Provides instructions for OpenSim installation

## Usage

To run the powerlifting model analysis:

```bash
python ceinms.py
```

or

```bash
python openSim.py
```

First, ensure your environment is set up by running:
```bash
msk_setup.bat
```

## Requirements

- Windows operating system
- Python 3.8.10
- Internet connection for downloading packages
- Administrator privileges may be required for some installations