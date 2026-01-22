"""
Sensitivity Analysis and Control Plots
Generate control plots for Moments, Activations, and Fiber Lengths (FL).
Analyze effects of load increments on model outputs.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


def create_control_plots(
    trial_data: Dict[str, pd.DataFrame],
    trial_name: str = "Trial",
    output_dir: str = None
):
    """
    Create control plots for Moments, Activations, and Fiber Lengths.
    
    Args:
        trial_data: Dictionary with keys 'moments', 'activations', 'fiber_lengths'
        trial_name: Name of the trial for plot titles
        output_dir: Directory to save plots
        
    Returns:
        Dictionary of figure objects
    """
    figures = {}
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 1. Moments Control Plot
    if 'moments' in trial_data and trial_data['moments'] is not None:
        print(f"Creating moments control plot for {trial_name}")
        
        moments_df = trial_data['moments']
        time_col = 'time' if 'time' in moments_df.columns else moments_df.columns[0]
        moment_cols = [col for col in moments_df.columns if col != time_col][:10]
        
        n_moments = len(moment_cols)
        n_cols = 3
        n_rows = int(np.ceil(n_moments / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 3), constrained_layout=True)
        axes = axes.flatten() if n_moments > 1 else [axes]
        
        fig.suptitle(f'Moment Control Plots - {trial_name}', fontsize=16, fontweight='bold')
        
        for idx, moment in enumerate(moment_cols):
            ax = axes[idx]
            ax.plot(moments_df[time_col], moments_df[moment], linewidth=2, color='blue')
            ax.set_title(moment, fontsize=11)
            ax.set_xlabel('Time (s)', fontsize=9)
            ax.set_ylabel('Moment (Nm)', fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        
        # Hide unused subplots
        for idx in range(n_moments, len(axes)):
            axes[idx].axis('off')
        
        if output_dir:
            output_path = os.path.join(output_dir, f'{trial_name}_moments_control.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved moments control plot to: {output_path}")
        
        figures['moments'] = fig
    
    # 2. Activations Control Plot
    if 'activations' in trial_data and trial_data['activations'] is not None:
        print(f"Creating activations control plot for {trial_name}")
        
        act_df = trial_data['activations']
        time_col = 'time' if 'time' in act_df.columns else act_df.columns[0]
        act_cols = [col for col in act_df.columns if col != time_col][:15]
        
        n_muscles = len(act_cols)
        n_cols = 4
        n_rows = int(np.ceil(n_muscles / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 2.5), constrained_layout=True)
        axes = axes.flatten() if n_muscles > 1 else [axes]
        
        fig.suptitle(f'Activation Control Plots - {trial_name}', fontsize=16, fontweight='bold')
        
        for idx, muscle in enumerate(act_cols):
            ax = axes[idx]
            ax.plot(act_df[time_col], act_df[muscle], linewidth=2, color='green')
            ax.set_title(muscle, fontsize=9)
            ax.set_xlabel('Time (s)', fontsize=8)
            ax.set_ylabel('Activation', fontsize=8)
            ax.set_ylim([0, 1.05])
            ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for idx in range(n_muscles, len(axes)):
            axes[idx].axis('off')
        
        if output_dir:
            output_path = os.path.join(output_dir, f'{trial_name}_activations_control.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved activations control plot to: {output_path}")
        
        figures['activations'] = fig
    
    # 3. Fiber Lengths Control Plot
    if 'fiber_lengths' in trial_data and trial_data['fiber_lengths'] is not None:
        print(f"Creating fiber lengths control plot for {trial_name}")
        
        fl_df = trial_data['fiber_lengths']
        time_col = 'time' if 'time' in fl_df.columns else fl_df.columns[0]
        fl_cols = [col for col in fl_df.columns if col != time_col][:15]
        
        n_muscles = len(fl_cols)
        n_cols = 4
        n_rows = int(np.ceil(n_muscles / n_cols))
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 2.5), constrained_layout=True)
        axes = axes.flatten() if n_muscles > 1 else [axes]
        
        fig.suptitle(f'Fiber Length Control Plots - {trial_name}', fontsize=16, fontweight='bold')
        
        for idx, muscle in enumerate(fl_cols):
            ax = axes[idx]
            ax.plot(fl_df[time_col], fl_df[muscle], linewidth=2, color='red')
            ax.set_title(muscle, fontsize=9)
            ax.set_xlabel('Time (s)', fontsize=8)
            ax.set_ylabel('Normalized FL', fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=1.0, color='k', linestyle='--', alpha=0.3, label='Optimal')
        
        # Hide unused subplots
        for idx in range(n_muscles, len(axes)):
            axes[idx].axis('off')
        
        if output_dir:
            output_path = os.path.join(output_dir, f'{trial_name}_fiber_lengths_control.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved fiber lengths control plot to: {output_path}")
        
        figures['fiber_lengths'] = fig
    
    return figures


def analyze_load_increments(
    baseline_data: Dict[str, pd.DataFrame],
    loaded_data_list: List[Dict[str, pd.DataFrame]],
    load_labels: List[str],
    output_dir: str = None
):
    """
    Analyze effects of load increments on model outputs.
    
    Args:
        baseline_data: Dictionary with baseline trial data
        loaded_data_list: List of dictionaries with loaded trial data
        load_labels: Labels for each loaded condition
        output_dir: Directory to save plots
        
    Returns:
        Dictionary with analysis results and figures
    """
    results = {
        'peak_moments': {},
        'peak_activations': {},
        'peak_forces': {},
        'figures': {}
    }
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Analyze peak moments across loads
    if 'moments' in baseline_data and baseline_data['moments'] is not None:
        print("Analyzing moment increments with load...")
        
        baseline_moments = baseline_data['moments']
        moment_cols = [col for col in baseline_moments.columns if col != 'time'][:6]
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 8), constrained_layout=True)
        axes = axes.flatten()
        
        fig.suptitle('Effects of Load Increments on Joint Moments', fontsize=16, fontweight='bold')
        
        for idx, moment in enumerate(moment_cols):
            ax = axes[idx]
            
            # Plot baseline
            time_col = 'time' if 'time' in baseline_moments.columns else baseline_moments.columns[0]
            ax.plot(baseline_moments[time_col], baseline_moments[moment], 
                   label='Baseline', linewidth=2, color='blue', linestyle='-')
            
            # Plot loaded conditions
            colors = ['orange', 'red', 'purple', 'brown']
            for i, (loaded_data, label) in enumerate(zip(loaded_data_list, load_labels)):
                if 'moments' in loaded_data and loaded_data['moments'] is not None:
                    loaded_moments = loaded_data['moments']
                    if moment in loaded_moments.columns:
                        time_col_loaded = 'time' if 'time' in loaded_moments.columns else loaded_moments.columns[0]
                        ax.plot(loaded_moments[time_col_loaded], loaded_moments[moment], 
                               label=label, linewidth=2, color=colors[i % len(colors)], 
                               linestyle='--', alpha=0.8)
            
            ax.set_title(moment, fontsize=11)
            ax.set_xlabel('Time (s)', fontsize=9)
            ax.set_ylabel('Moment (Nm)', fontsize=9)
            ax.grid(True, alpha=0.3)
            
            if idx == 0:
                ax.legend(fontsize=8)
        
        if output_dir:
            output_path = os.path.join(output_dir, 'load_increments_moments.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved load increment analysis to: {output_path}")
        
        results['figures']['moments'] = fig
    
    # Analyze peak muscle activations across loads
    if 'activations' in baseline_data and baseline_data['activations'] is not None:
        print("Analyzing activation increments with load...")
        
        baseline_act = baseline_data['activations']
        muscle_cols = [col for col in baseline_act.columns if col != 'time'][:8]
        
        fig, axes = plt.subplots(2, 4, figsize=(16, 8), constrained_layout=True)
        axes = axes.flatten()
        
        fig.suptitle('Effects of Load Increments on Muscle Activations', fontsize=16, fontweight='bold')
        
        for idx, muscle in enumerate(muscle_cols):
            ax = axes[idx]
            
            # Plot baseline
            time_col = 'time' if 'time' in baseline_act.columns else baseline_act.columns[0]
            ax.plot(baseline_act[time_col], baseline_act[muscle], 
                   label='Baseline', linewidth=2, color='green', linestyle='-')
            
            # Plot loaded conditions
            colors = ['orange', 'red', 'purple', 'brown']
            for i, (loaded_data, label) in enumerate(zip(loaded_data_list, load_labels)):
                if 'activations' in loaded_data and loaded_data['activations'] is not None:
                    loaded_act = loaded_data['activations']
                    if muscle in loaded_act.columns:
                        time_col_loaded = 'time' if 'time' in loaded_act.columns else loaded_act.columns[0]
                        ax.plot(loaded_act[time_col_loaded], loaded_act[muscle], 
                               label=label, linewidth=2, color=colors[i % len(colors)], 
                               linestyle='--', alpha=0.8)
            
            ax.set_title(muscle, fontsize=10)
            ax.set_xlabel('Time (s)', fontsize=8)
            ax.set_ylabel('Activation', fontsize=8)
            ax.set_ylim([0, 1.05])
            ax.grid(True, alpha=0.3)
            
            if idx == 0:
                ax.legend(fontsize=7)
        
        if output_dir:
            output_path = os.path.join(output_dir, 'load_increments_activations.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"Saved activation increment analysis to: {output_path}")
        
        results['figures']['activations'] = fig
    
    return results


def calculate_peak_metrics(data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    """
    Calculate peak values for moments, activations, and forces.
    
    Args:
        data_dict: Dictionary with 'moments', 'activations', 'forces' data
        
    Returns:
        Dictionary with peak values for each metric
    """
    metrics = {}
    
    for data_type in ['moments', 'activations', 'forces']:
        if data_type in data_dict and data_dict[data_type] is not None:
            df = data_dict[data_type]
            cols = [col for col in df.columns if col != 'time']
            
            peaks = {}
            for col in cols:
                peaks[col] = {
                    'max': df[col].max(),
                    'min': df[col].min(),
                    'mean': df[col].mean(),
                    'std': df[col].std()
                }
            
            metrics[data_type] = peaks
    
    return metrics


if __name__ == "__main__":
    print("Sensitivity Analysis and Control Plots")
    print("=" * 60)
    
    choice = input("Choose operation:\n1. Create control plots\n2. Analyze load increments\nEnter choice (1/2): ")
    
    if choice == '1':
        # Create control plots
        trial_path = input("Enter path to trial directory: ").strip('"')
        output_dir = input("Enter output directory for plots: ").strip('"')
        
        # Load data
        trial_data = {
            'moments': utils.load_any_data_file(os.path.join(trial_path, 'Analyse_ID_Moments.sto')),
            'activations': utils.load_any_data_file(os.path.join(trial_path, 'Analyse_SO_activation.sto')),
            'fiber_lengths': utils.load_any_data_file(os.path.join(trial_path, 'Analyse_SO_norm_fiber_length.sto'))
        }
        
        trial_name = os.path.basename(trial_path)
        create_control_plots(trial_data, trial_name, output_dir)
        
        print("\nControl plots created successfully!")
        
    elif choice == '2':
        # Analyze load increments
        print("\nLoad increment analysis")
        baseline_path = input("Enter path to baseline trial: ").strip('"')
        
        n_loads = int(input("Enter number of loaded conditions: "))
        loaded_paths = []
        load_labels = []
        
        for i in range(n_loads):
            path = input(f"Enter path to loaded trial {i+1}: ").strip('"')
            label = input(f"Enter label for load {i+1} (e.g., '+10kg', '+20kg'): ").strip()
            loaded_paths.append(path)
            load_labels.append(label)
        
        output_dir = input("Enter output directory for plots: ").strip('"')
        
        # Load baseline data
        baseline_data = {
            'moments': utils.load_any_data_file(os.path.join(baseline_path, 'Analyse_ID_Moments.sto')),
            'activations': utils.load_any_data_file(os.path.join(baseline_path, 'Analyse_SO_activation.sto')),
            'forces': utils.load_any_data_file(os.path.join(baseline_path, 'Analyse_SO_force.sto'))
        }
        
        # Load loaded trial data
        loaded_data_list = []
        for path in loaded_paths:
            loaded_data = {
                'moments': utils.load_any_data_file(os.path.join(path, 'Analyse_ID_Moments.sto')),
                'activations': utils.load_any_data_file(os.path.join(path, 'Analyse_SO_activation.sto')),
                'forces': utils.load_any_data_file(os.path.join(path, 'Analyse_SO_force.sto'))
            }
            loaded_data_list.append(loaded_data)
        
        # Analyze
        results = analyze_load_increments(baseline_data, loaded_data_list, load_labels, output_dir)
        
        print("\nLoad increment analysis completed!")
        
    else:
        print("Invalid choice")
    
    plt.show()
