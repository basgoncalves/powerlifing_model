# Code Directory

This directory contains all code and scripts for the powerlifting model project.

## Files

### Setup Scripts
- `msk_setup.bat` - Windows batch script to install required software:
  - Python 3.8.10
  - uv (Python package manager)
  - msk_modelling_python
  - OpenSim

### Usage

#### Initial Setup (Windows)
1. Right-click on `msk_setup.bat` and select "Run as administrator"
2. Follow the installation prompts
3. Restart your command prompt after installation

#### Development
- Place Python scripts and analysis code here
- Organize code by functionality (preprocessing, simulation, analysis, visualization)
- Follow consistent naming conventions

## Recommended Structure

```
code/
├── msk_setup.bat           # Setup script
├── preprocessing/          # Data preprocessing scripts
├── simulation/            # OpenSim simulation scripts
├── analysis/              # Analysis and statistics scripts
├── visualization/         # Plotting and visualization scripts
├── utils/                 # Utility functions
└── config/               # Configuration files
```

## Dependencies

After running `msk_setup.bat`, the following will be available:
- Python 3.8.10
- OpenSim Python API
- msk_modelling_python package
- uv package manager for fast Python package installation