# Simulations Directory

This directory contains simulation data organized by subject, session, and trial.

## Structure

```
simulations/
├── SubjectXX/
│   ├── SessionXX/
│   │   ├── TrialXX/
│   │   │   ├── input_files/
│   │   │   ├── results/
│   │   │   └── logs/
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

## Example Usage

For a squat analysis of Subject 01, Session 01, Trial 01:
```
simulations/Subject01/Session01/Trial01/
├── input_files/
│   ├── squat_markers.trc
│   ├── squat_forces.mot
│   └── squat_emg.txt
├── results/
│   ├── inverse_kinematics.mot
│   ├── inverse_dynamics.sto
│   └── muscle_forces.sto
└── logs/
    ├── ik_log.txt
    └── processing_notes.txt
```