# Powerlifting Model Project

A biomechanical analysis project for powerlifting movements using OpenSim and motion capture data.

## Project Structure

```
powerlifing_model/
├── code/                   # Scripts and analysis code
│   ├── msk_setup.bat      # Installation script for required software
│   └── README.md          # Code directory documentation
├── models/                # Biomechanical models and marker sets
│   ├── opensim_models/    # OpenSim (.osim) model files
│   ├── markersets/        # Marker set definitions (.xml)
│   └── README.md          # Models directory documentation
├── MRIs/                  # MRI data for subject-specific modeling
│   └── README.md          # MRI directory documentation
├── simulations/           # Simulation data organized by subject/session/trial
│   ├── Subject01/
│   │   ├── Session01/
│   │   │   ├── Trial01/   # Individual trial data
│   │   │   └── Trial02/
│   │   └── Session02/
│   ├── Subject02/
│   └── README.md          # Simulations directory documentation
└── README.md              # This file
```

## Getting Started

### 1. Setup Environment (Windows)

Run the setup script to install required software:

```bash
# Right-click and "Run as administrator"
code/msk_setup.bat
```

This will install:
- Python 3.8.10
- uv (Python package manager)
- msk_modelling_python
- OpenSim

### 2. Data Organization

- Place your OpenSim models in `models/opensim_models/`
- Place marker set definitions in `models/markersets/`
- Organize MRI data by subject in `MRIs/`
- Follow the SubjectXX/SessionXX/TrialXX structure in `simulations/`

### 3. Analysis Pipeline

1. **Data Collection**: Motion capture and force plate data
2. **Preprocessing**: Data cleaning and synchronization
3. **Model Scaling**: Subject-specific model creation
4. **Inverse Kinematics**: Joint angle calculation
5. **Inverse Dynamics**: Joint moment calculation
6. **Muscle Analysis**: Force and activation estimation

## Requirements

- Windows OS (for msk_setup.bat)
- Administrator privileges for installation
- OpenSim 4.x compatible models
- Motion capture system compatible with OpenSim

## Contributing

- Follow the established directory structure
- Document all code and analysis steps
- Use consistent naming conventions
- Include README files for new directories or major code additions