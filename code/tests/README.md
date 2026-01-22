# Model Comparison Analysis Tools

This directory contains tools for comprehensive biomechanical model comparison analysis, specifically designed for comparing powerlifting models (e.g., BG vs Katya personalized models).

## Overview

These tools implement the model comparison workflow as outlined in the project's issue tracker:

1. **Summary Figure Generation** - Compare IK, ID, Force, Activation, and JRA outputs
2. **SO Activation Conversion** - Convert Static Optimization activations to CEINMS excitations
3. **Hybrid Mode** - Combine SO activations with EMG for improved CEINMS simulations
4. **Sensitivity Analysis** - Control plots and load increment effects
5. **EMG Comparisons** - Validate model predictions against experimental EMG
6. **Clinical Conclusions** - Framework for interpreting results

## Tools

### 1. create_summary_figures.py

Generate comprehensive comparison figures for two models.

**Features:**
- Multi-panel summary showing IK, ID, Force, Activation, and JRA
- Detailed muscle force comparisons in grid layout
- Joint reaction analysis (JRA) comparison figures

**Usage:**
```python
from create_summary_figures import create_comparison_summary_figure

# Load data for both models
model1_data = {
    'ik': load_data_file('path/to/model1/ik.mot'),
    'id': load_data_file('path/to/model1/Analyse_ID_Moments.sto'),
    'forces': load_data_file('path/to/model1/Analyse_SO_force.sto'),
    'activations': load_data_file('path/to/model1/Analyse_SO_activation.sto'),
    'jra': load_data_file('path/to/model1/Analyse_JRA_ReactionLoads_SO.sto')
}

# Create comparison figure
create_comparison_summary_figure(
    model1_data, model2_data,
    model1_name="BG", model2_name="Katya",
    output_path='comparison_summary.png'
)
```

**Command-line usage:**
```bash
python create_summary_figures.py
# Follow interactive prompts to specify model paths
```

### 2. so_activation_to_excitation.py

Convert Static Optimization activations to excitation format for CEINMS.

**Features:**
- Convert SO activations (.sto) to excitation format
- Create excitation generator XML with all muscles
- Create hybrid excitation generator (SO + EMG)

**Usage:**
```python
from so_activation_to_excitation import create_excitation_generator_from_so

# Create excitation generator from SO activations
muscle_list, so_muscles = create_excitation_generator_from_so(
    osim_model_path='model.osim',
    so_activation_file='Analyse_SO_activation.sto',
    output_xml_path='excitationGenerator_SO.xml',
    use_all_muscles=True
)
```

**Hybrid mode example:**
```python
from so_activation_to_excitation import create_hybrid_excitation_generator

# Combine SO activations with EMG (50/50 weighting)
create_hybrid_excitation_generator(
    osim_model_path='model.osim',
    so_activation_file='Analyse_SO_activation.sto',
    emg_file='emg_normalised.sto',
    output_xml_path='excitationGenerator_Hybrid.xml',
    so_weight=0.5,
    emg_weight=0.5
)
```

**Command-line usage:**
```bash
python so_activation_to_excitation.py
# Choose: 1) Convert SO to excitations, 2) Create excitation generator, or 3) Create hybrid generator
```

### 3. sensitivity_analysis.py

Perform sensitivity analysis with control plots and load increment comparisons.

**Features:**
- Control plots for Moments, Activations, and Fiber Lengths
- Load increment analysis (compare baseline vs loaded conditions)
- Peak metrics calculation

**Usage:**
```python
from sensitivity_analysis import create_control_plots

# Create control plots
trial_data = {
    'moments': load_data_file('Analyse_ID_Moments.sto'),
    'activations': load_data_file('Analyse_SO_activation.sto'),
    'fiber_lengths': load_data_file('Analyse_SO_norm_fiber_length.sto')
}

create_control_plots(trial_data, trial_name="Squat_BW", output_dir='results/control_plots')
```

**Load increment analysis:**
```python
from sensitivity_analysis import analyze_load_increments

# Compare baseline with loaded conditions
results = analyze_load_increments(
    baseline_data=baseline_trial_data,
    loaded_data_list=[load1_data, load2_data],
    load_labels=['+10kg', '+20kg'],
    output_dir='results/load_analysis'
)
```

**Command-line usage:**
```bash
python sensitivity_analysis.py
# Choose: 1) Create control plots or 2) Analyze load increments
```

### 4. emg_comparisons.py

Compare EMG signals with model-predicted activations.

**Features:**
- Visual comparison of EMG vs model activations
- Correlation and RMSE metrics
- Validation report generation
- Summary statistics and plots

**Usage:**
```python
from emg_comparisons import compare_emg_with_activations

# Compare EMG with activations
results = compare_emg_with_activations(
    emg_data=emg_df,
    activation_data=activation_df,
    muscle_mapping=muscle_mapping_dict,
    trial_name="Walking",
    output_path='emg_comparison.png'
)

# Generate validation report
from emg_comparisons import create_emg_validation_report
report_df = create_emg_validation_report(
    results['metrics'],
    output_path='emg_validation_report.csv'
)
```

**Command-line usage:**
```bash
python emg_comparisons.py
# Provide EMG file, activation file, and output directory
```

## Notebook Integration

All tools are integrated into `code/notebook.ipynb` with dedicated sections:

1. **Model Comparison Analysis** - Summary figures and comparisons
2. **SO Activations as EMG Inputs** - Conversion and excitation generation
3. **Hybrid Mode Implementation** - Combined SO + EMG approach
4. **CEINMS Execution** - Run simulations with new excitations
5. **Sensitivity Analysis** - Control plots and load effects
6. **EMG Comparisons** - Validation against experimental data
7. **Clinical Conclusions** - Result interpretation framework

## Workflow Example

### Complete model comparison workflow:

```python
# 1. Load model data
model_bg_data = {...}
model_katya_data = {...}

# 2. Create summary comparison figures
create_comparison_summary_figure(model_bg_data, model_katya_data, ...)

# 3. Create control plots for each model
create_control_plots(model_bg_data, trial_name="BG", ...)
create_control_plots(model_katya_data, trial_name="Katya", ...)

# 4. Analyze load increments
analyze_load_increments(baseline_data, loaded_data_list, load_labels, ...)

# 5. Convert SO activations to excitations for CEINMS
create_excitation_generator_from_so(model_path, so_activation_file, ...)

# 6. Compare EMG with model predictions
compare_emg_with_activations(emg_data, activation_data, muscle_mapping, ...)

# 7. Generate validation reports
create_emg_validation_report(comparison_metrics, ...)
```

## Dependencies

All tools use the existing project infrastructure:
- `utils.py` - Data loading and helper functions
- `settings.py` - Configuration and parameters
- `ceinms.py` - CEINMS integration
- `openSim.py` - OpenSim model operations

Required Python packages:
- pandas
- numpy
- matplotlib
- scipy
- scikit-learn
- opensim (for model operations)

## Output Structure

Recommended output directory structure:
```
results/
├── model_comparison/
│   ├── model_comparison_summary.png
│   ├── muscle_forces_comparison.png
│   └── jra_comparison.png
├── control_plots/
│   ├── Trial_moments_control.png
│   ├── Trial_activations_control.png
│   └── Trial_fiber_lengths_control.png
├── load_analysis/
│   ├── load_increments_moments.png
│   └── load_increments_activations.png
└── emg_comparisons/
    ├── emg_activation_comparison.png
    ├── emg_validation_report.csv
    └── emg_comparison_summary.png
```

## Notes

- **Data Format**: All tools expect OpenSim .sto or .mot files with 'time' column
- **Missing Data**: Tools gracefully handle missing data files
- **Customization**: Plot parameters (colors, line styles, etc.) can be customized in the source code
- **Performance**: Large datasets may take time to process; consider subsampling for preliminary analysis

## Citation

If you use these tools in your research, please cite the appropriate OpenSim and CEINMS papers, as well as acknowledge the powerlifting model project.

## Support

For issues or questions:
1. Check the main project README
2. Review the notebook.ipynb for usage examples
3. Refer to inline documentation in each tool
4. Contact the repository maintainer

## License

These tools are part of the powerlifting_model project and follow the same license terms.
