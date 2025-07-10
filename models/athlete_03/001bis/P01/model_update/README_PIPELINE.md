# Model Creation Pipeline

This directory contains a simplified model creation pipeline that consolidates the functionality from multiple notebooks and scripts into a single, configurable workflow.

## Files

- `run_model_creation.py` - Main orchestration script that runs the complete workflow
- `model_creation_config.json` - Configuration file containing all paths and parameters
- Original files (0_*.py, 1_*.py, *.ipynb, etc.) - Original workflow files (preserved for reference)

## Usage

### Quick Start

Run the complete pipeline with default configuration:

```bash
python run_model_creation.py
```

### Advanced Usage

Use a custom configuration file:

```bash
python run_model_creation.py --config my_config.json
```

Run specific steps only:

```bash
python run_model_creation.py --steps install_requirements,morph_bones_from_mri,tps_processing
```

## Configuration

The `model_creation_config.json` file contains all the necessary paths and parameters:

```json
{
  "model_creation_config": {
    "participant_id": "P01",
    "working_directory": ".",
    "paths": {
      "input": {
        "mri_results": "../../MRI/results",
        "orientation_json": "../../MRI/results/orientation.mrk.json",
        "xml_markerset": "../../../../Geometry/tps_warping.xml",
        "osim_model": "Athlete_03_lowerBody_final_increased_3.00.osim",
        "geometry_dir": "./Geometry"
      },
      "output": {
        "tps_warping_results": "./tps_warping_results",
        "tps_warping_after_mri": "./tps_warping_results/after_MRI",
        "control_path": "./tps_warping_results/control",
        "logs": "./logs"
      }
    },
    "processing_steps": [
      "install_requirements",
      "morph_bones_from_mri",
      "start_c3d_processing",
      "tps_processing",
      "tps_after_mri",
      "tps_workflow_scaling",
      "after_mri_tps",
      "model_compare",
      "moment_arms_compare"
    ]
  }
}
```

## Processing Steps

The pipeline includes the following steps:

1. **install_requirements** - Install required Python packages
2. **morph_bones_from_mri** - Process MRI data for bone morphing
3. **start_c3d_processing** - Process C3D motion capture data
4. **tps_processing** - Thin Plate Spline processing
5. **tps_after_mri** - TPS processing after MRI adjustments
6. **tps_workflow_scaling** - OpenSim marker scaling workflow
7. **after_mri_tps** - Additional TPS processing after MRI
8. **model_compare** - Compare different model versions
9. **moment_arms_compare** - Compare moment arms between models

## Requirements

The pipeline will automatically install the following packages:
- numpy
- scipy
- nibabel
- matplotlib
- pandas
- opensim
- plotly
- pyvista

## Logging

All processing steps are logged to `./logs/model_creation.log` with timestamps and status information.

## Customization

To customize the pipeline:

1. Edit the `model_creation_config.json` file to change paths and parameters
2. Modify the `run_model_creation.py` script to add new processing steps
3. The original notebook files remain available for reference and detailed analysis

## Error Handling

The pipeline includes comprehensive error handling and will stop execution if any step fails. Check the log file for detailed error information.