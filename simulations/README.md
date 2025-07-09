# Simulations Directory

This directory contains all simulation data organized by subject, session, and trial.

## Directory Structure

```
simulations/
├── Subject01/
│   ├── Session01/
│   │   ├── Trial01/
│   │   ├── Trial02/
│   │   └── ...
│   ├── Session02/
│   │   ├── Trial01/
│   │   └── ...
│   └── ...
├── Subject02/
│   └── ...
└── ...
```

## Naming Convention

- **SubjectXX**: Use zero-padded subject numbers (e.g., Subject01, Subject02, ..., Subject10)
- **SessionXX**: Use zero-padded session numbers (e.g., Session01, Session02)
- **TrialXX**: Use zero-padded trial numbers (e.g., Trial01, Trial02)

## Trial Contents

Each trial directory should contain:
- Motion capture data (.trc files)
- Force plate data (.mot files)
- OpenSim simulation results
- Analysis outputs
- Configuration files

## Processing Pipeline

1. **Data Collection**: Raw motion capture and force data
2. **Preprocessing**: Filtering, gap filling, synchronization
3. **Inverse Kinematics**: Joint angle calculation
4. **Inverse Dynamics**: Joint moment calculation
5. **Muscle Analysis**: Force and activation estimation
6. **Results**: Final analysis outputs and visualizations

## Example Files per Trial

- `motion_data.trc` - Motion capture marker data
- `grf_data.mot` - Ground reaction force data
- `ik_results.mot` - Inverse kinematics results
- `id_results.sto` - Inverse dynamics results
- `muscle_analysis.sto` - Muscle force analysis
- `trial_config.xml` - Trial-specific configuration