# Powerlifting Model

A biomechanical modeling toolkit for analyzing powerlifting movements using OpenSim and CEINMS.

## Overview

This project provides tools for processing motion capture data, running musculoskeletal simulations, and analyzing muscle forces during powerlifting exercises.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd powerlifing_model
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install OpenSim Python API (required):
```bash
pip install opensim
```

## Basic Usage

### Running a Complete Analysis

The main entry point is `code/__main__.py`. Configure your analysis by editing the settings at the top:

```python
from code import __main__

# Configure which subjects, sessions, and trials to analyze
SUBJECTS_TO_ANALYSE = ['Athlete_03']
SESSIONS_TO_ANALYSE = ['25_03_31']
TRIALS_TO_ANALYSE = ['Walking_03']

# Run the analysis
python -m code
```

### Individual Analysis Steps

#### 1. Inverse Kinematics (IK)

```python
from code import openSim

# Run inverse kinematics on a trial
openSim.run_inverse_kinematics(
    model_path='models/Athlete_03/scaled_model.osim',
    marker_file='simulations/Athlete_03/Session01/Trial01/markers.trc',
    output_motion='simulations/Athlete_03/Session01/Trial01/ik_results.mot'
)
```

#### 2. Inverse Dynamics (ID)

```python
from code import openSim

# Run inverse dynamics
openSim.run_inverse_dynamics(
    model_path='models/Athlete_03/scaled_model.osim',
    motion_file='simulations/Athlete_03/Session01/Trial01/ik_results.mot',
    external_loads='simulations/Athlete_03/Session01/Trial01/grf.xml',
    output_file='simulations/Athlete_03/Session01/Trial01/id_results.sto'
)
```

#### 3. Static Optimization (SO)

```python
from code import openSim

# Run static optimization
openSim.run_static_optimization(
    model_path='models/Athlete_03/scaled_model.osim',
    motion_file='simulations/Athlete_03/Session01/Trial01/ik_results.mot',
    output_dir='simulations/Athlete_03/Session01/Trial01/so_results/'
)
```

#### 4. Muscle Parameter Optimization

```python
from code import muscleOptimizer

# Optimize muscle parameters
muscleOptimizer.optimize_muscle_parameters(
    model_path='models/Athlete_03/scaled_model.osim',
    motion_file='simulations/Athlete_03/Session01/Trial01/ik_results.mot',
    output_model='models/Athlete_03/optimized_model.osim'
)
```

#### 5. CEINMS Calibration

```python
from code import ceinms

# Create CEINMS model
ceinms.create_ceinms_model(
    opensim_model='models/Athlete_03/scaled_model.osim',
    output_dir='manual_usage_ceinms_nn/'
)

# Run calibration
ceinms.run_calibration(
    subject_dir='manual_usage_ceinms_nn/',
    calibration_trials=['Walking_02']
)
```

### Export C3D Data

```python
from code import exportC3D

# Export C3D file to OpenSim format
exportC3D.export_c3d_to_opensim(
    c3d_file='simulations/Athlete_03/Session01/Trial01/raw_data.c3d',
    output_dir='simulations/Athlete_03/Session01/Trial01/'
)
```

## Directory Structure

### Main Directories

- **code/** - Main source code and analysis scripts
- **models/** - OpenSim musculoskeletal models (.osim files)
- **simulations/** - Simulation data organized by subject/session/trial
- **manual_usage_ceinms_nn/** - CEINMS calibration configuration files
- **results/** - Analysis results and figures
- **mrts/** - Measurement and anthropometric data

### Simulations Directory Structure

```
simulations/
├── SubjectXX/
│   ├── SessionXX/
│   │   ├── TrialXX/
│   │   │   ├── input_files/
│   │   │   └── results/
│   │   └── TrialXX/
│   └── SessionXX/
└── SubjectXX/
```

## Organization

- **SubjectXX**: Individual participant data (e.g., Subject01, Subject02, ...)
- **SessionXX**: Testing session within a subject (e.g., Session01, Session02, ...)
- **TrialXX**: Individual trials within a session (e.g., Trial01, Trial02, ...)

## Trial Structure

Each trial directory should contain:
- `input_files/`: Motion capture data, force plate data, EMG data
- `results/`: Simulation outputs, analysis results
- `logs/`: Processing logs and metadata

## File Types

Common file types in simulation directories:
- `.trc` - Motion capture marker data
- `.mot` - OpenSim motion files
- `.sto` - OpenSim storage files
- `.c3d` - Motion capture data files
- `.txt` - Force plate and other sensor data
- `.csv` - Processed data and results

## Complete Analysis Example

For a squat analysis of Subject 01, Session 01, Trial 01:

```bash
# 1. Organize your data
simulations/Subject01/Session01/Trial01/
├── input_files/
│   ├── c3dfile.c3d
│   ├── experimental_markers.trc
│   ├── grf.mot
│   └── squat_emg.sto
└── results/
    ├── joint_angles.mot
    ├── inverse_dynamics.sto
    ├── setup_IK.xml
    └── setup_ID.xml
```

## Configuration

Edit [code/__main__.py](code/__main__.py) to configure which analyses to run:

```python
class Execute:
    def __init__(self):
        self.IK = True              # Inverse Kinematics
        self.ID = True              # Inverse Dynamics
        self.SO = True              # Static Optimization
        self.JRA = True             # Joint Reaction Analysis
        self.CEINMS_CALIBRATION = False
        # ... other options
```

## Contributing

Contributions are welcome. Please ensure code follows existing patterns and includes appropriate documentation.

## License

See LICENSE file for details.
