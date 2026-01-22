"""
Create comprehensive summary figures for model comparison analysis.
Generates multi-panel figures showing IK, ID, Force, Activation, and JRA comparisons.
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional

# Add parent directory to path to import utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


def load_data_file(filepath: str) -> Optional[pd.DataFrame]:
    """
    Load data file safely with error handling.
    
    Args:
        filepath: Path to the data file
        
    Returns:
        DataFrame or None if file doesn't exist
    """
    if not os.path.exists(filepath):
        print(f"Warning: File not found: {filepath}")
        return None
    
    try:
        return utils.load_any_data_file(filepath)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def create_comparison_summary_figure(
    model1_data: Dict[str, pd.DataFrame],
    model2_data: Dict[str, pd.DataFrame],
    model1_name: str = "BG",
    model2_name: str = "Katya",
    output_path: str = None
):
    """
    Create a comprehensive summary figure comparing two models.
    
    Args:
        model1_data: Dictionary with keys 'ik', 'id', 'forces', 'activations', 'jra'
        model2_data: Dictionary with keys 'ik', 'id', 'forces', 'activations', 'jra'
        model1_name: Name of first model (default: "BG")
        model2_name: Name of second model (default: "Katya")
        output_path: Path to save the figure
    """
    # Define analysis types
    analysis_types = ['IK', 'ID', 'Force', 'Activation', 'JRA']
    data_keys = ['ik', 'id', 'forces', 'activations', 'jra']
    
    # Create figure with subplots
    n_rows = len(analysis_types)
    fig, axes = plt.subplots(n_rows, 1, figsize=(15, n_rows * 3.5), constrained_layout=True)
    
    fig.suptitle(f'Model Comparison: {model1_name} vs {model2_name}', fontsize=16, fontweight='bold')
    
    colors = {model1_name: 'blue', model2_name: 'orange'}
    line_styles = {model1_name: '-', model2_name: '--'}
    
    for idx, (analysis_type, data_key) in enumerate(zip(analysis_types, data_keys)):
        ax = axes[idx] if n_rows > 1 else axes
        
        # Get data for both models
        df1 = model1_data.get(data_key)
        df2 = model2_data.get(data_key)
        
        if df1 is None and df2 is None:
            ax.text(0.5, 0.5, f'No data available for {analysis_type}', 
                   ha='center', va='center', fontsize=12, color='red')
            ax.set_title(f'{analysis_type}')
            ax.axis('off')
            continue
        
        # Plot data
        ax.set_title(f'{analysis_type}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (s)')
        
        # Determine y-label based on analysis type
        y_labels = {
            'IK': 'Joint Angle (deg)',
            'ID': 'Joint Moment (Nm)',
            'Force': 'Muscle Force (N)',
            'Activation': 'Muscle Activation',
            'JRA': 'Joint Reaction Force (N)'
        }
        ax.set_ylabel(y_labels.get(analysis_type, 'Value'))
        
        # Plot a subset of columns for readability
        max_cols = 5  # Plot max 5 columns per analysis type
        
        if df1 is not None:
            time_col1 = 'time' if 'time' in df1.columns else df1.columns[0]
            plot_cols1 = [col for col in df1.columns if col != time_col1][:max_cols]
            
            for col in plot_cols1:
                ax.plot(df1[time_col1], df1[col], 
                       label=f'{model1_name}_{col}', 
                       color=colors[model1_name],
                       linestyle=line_styles[model1_name],
                       alpha=0.7,
                       linewidth=1.5)
        
        if df2 is not None:
            time_col2 = 'time' if 'time' in df2.columns else df2.columns[0]
            plot_cols2 = [col for col in df2.columns if col != time_col2][:max_cols]
            
            for col in plot_cols2:
                ax.plot(df2[time_col2], df2[col], 
                       label=f'{model2_name}_{col}', 
                       color=colors[model2_name],
                       linestyle=line_styles[model2_name],
                       alpha=0.7,
                       linewidth=1.5)
        
        ax.grid(True, alpha=0.3)
        
        # Add legend only to first subplot
        if idx == 0:
            ax.legend(loc='upper right', fontsize=8, ncol=2)
    
    # Save figure
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f'Summary figure saved to: {output_path}')
    
    return fig, axes


def create_muscle_comparison_grid(
    model1_forces: pd.DataFrame,
    model2_forces: pd.DataFrame,
    muscle_list: List[str],
    model1_name: str = "BG SO",
    model2_name: str = "Katya SO",
    output_path: str = None
):
    """
    Create a grid of muscle force comparisons.
    
    Args:
        model1_forces: DataFrame with muscle forces for model 1
        model2_forces: DataFrame with muscle forces for model 2
        muscle_list: List of muscle names to plot
        model1_name: Name of first model
        model2_name: Name of second model
        output_path: Path to save the figure
    """
    n_muscles = len(muscle_list)
    n_cols = 5
    n_rows = int(np.ceil(n_muscles / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, n_rows * 3), constrained_layout=True)
    axes = axes.flatten() if n_muscles > 1 else [axes]
    
    fig.suptitle(f'Muscle Forces Comparison: {model1_name} vs {model2_name}', 
                fontsize=16, fontweight='bold')
    
    time_col1 = 'time' if 'time' in model1_forces.columns else model1_forces.columns[0]
    time_col2 = 'time' if 'time' in model2_forces.columns else model2_forces.columns[0]
    
    for idx, muscle in enumerate(muscle_list):
        ax = axes[idx]
        
        # Plot model 1
        if muscle in model1_forces.columns:
            ax.plot(model1_forces[time_col1], model1_forces[muscle], 
                   label=model1_name, color='blue', linestyle='-', linewidth=2)
        
        # Plot model 2
        if muscle in model2_forces.columns:
            ax.plot(model2_forces[time_col2], model2_forces[muscle], 
                   label=model2_name, color='orange', linestyle='--', linewidth=2)
        
        ax.set_title(muscle, fontsize=10)
        ax.set_xlabel('Time (s)', fontsize=8)
        ax.set_ylabel('Force (N)', fontsize=8)
        ax.grid(True, alpha=0.3)
        
        if idx == 0:
            ax.legend(fontsize=8)
    
    # Hide unused subplots
    for idx in range(n_muscles, len(axes)):
        axes[idx].axis('off')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f'Muscle comparison figure saved to: {output_path}')
    
    return fig, axes


def create_jra_comparison_figure(
    model1_jra: pd.DataFrame,
    model2_jra: pd.DataFrame,
    joint_list: List[str] = None,
    model1_name: str = "BG",
    model2_name: str = "Katya",
    output_path: str = None
):
    """
    Create comprehensive JRA comparison figure.
    
    Args:
        model1_jra: DataFrame with JRA data for model 1
        model2_jra: DataFrame with JRA data for model 2
        joint_list: List of joints to plot (if None, plots all)
        model1_name: Name of first model
        model2_name: Name of second model
        output_path: Path to save the figure
    """
    # Define force components
    force_components = ['_X', '_Y', '_Z', '_sum']
    
    if joint_list is None:
        # Extract unique joint names
        all_cols = set(model1_jra.columns) | set(model2_jra.columns)
        joint_list = list(set([col.split('_')[0] for col in all_cols 
                              if any(comp in col for comp in force_components)]))
    
    n_joints = len(joint_list)
    n_components = len(force_components)
    
    fig, axes = plt.subplots(n_joints, n_components, 
                            figsize=(16, n_joints * 3), 
                            constrained_layout=True)
    
    if n_joints == 1:
        axes = axes.reshape(1, -1)
    
    fig.suptitle(f'Joint Reaction Analysis: {model1_name} vs {model2_name}', 
                fontsize=16, fontweight='bold')
    
    time_col1 = 'time' if 'time' in model1_jra.columns else model1_jra.columns[0]
    time_col2 = 'time' if 'time' in model2_jra.columns else model2_jra.columns[0]
    
    for row, joint in enumerate(joint_list):
        for col, component in enumerate(force_components):
            ax = axes[row, col]
            col_name = f'{joint}{component}'
            
            # Plot model 1
            if col_name in model1_jra.columns:
                ax.plot(model1_jra[time_col1], model1_jra[col_name], 
                       label=model1_name, color='blue', linestyle='-', linewidth=2)
            
            # Plot model 2
            if col_name in model2_jra.columns:
                ax.plot(model2_jra[time_col2], model2_jra[col_name], 
                       label=model2_name, color='orange', linestyle='--', linewidth=2)
            
            if col == 0:
                ax.set_ylabel(f'{joint}\nForce (N)', fontsize=10)
            
            if row == 0:
                ax.set_title(f'{component.replace("_", "")}', fontsize=12)
            
            if row == n_joints - 1:
                ax.set_xlabel('Time (s)', fontsize=10)
            
            ax.grid(True, alpha=0.3)
            
            if row == 0 and col == 0:
                ax.legend(fontsize=9)
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f'JRA comparison figure saved to: {output_path}')
    
    return fig, axes


if __name__ == "__main__":
    # Example usage
    print("Summary Figure Generator for Model Comparison")
    print("=" * 60)
    
    # Get paths from user or use defaults
    model1_path = input("Enter path to Model 1 (BG) trial directory: ").strip('"')
    model2_path = input("Enter Model 2 (Katya) trial directory: ").strip('"')
    output_dir = input("Enter output directory for figures (or press Enter for current): ").strip('"')
    
    if not output_dir:
        output_dir = os.getcwd()
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data for both models
    print("\nLoading data files...")
    
    model1_data = {
        'ik': load_data_file(os.path.join(model1_path, 'ik.mot')),
        'id': load_data_file(os.path.join(model1_path, 'Analyse_ID_Moments.sto')),
        'forces': load_data_file(os.path.join(model1_path, 'Analyse_SO_force.sto')),
        'activations': load_data_file(os.path.join(model1_path, 'Analyse_SO_activation.sto')),
        'jra': load_data_file(os.path.join(model1_path, 'Analyse_JRA_ReactionLoads_SO.sto'))
    }
    
    model2_data = {
        'ik': load_data_file(os.path.join(model2_path, 'ik.mot')),
        'id': load_data_file(os.path.join(model2_path, 'Analyse_ID_Moments.sto')),
        'forces': load_data_file(os.path.join(model2_path, 'Analyse_SO_force.sto')),
        'activations': load_data_file(os.path.join(model2_path, 'Analyse_SO_activation.sto')),
        'jra': load_data_file(os.path.join(model2_path, 'Analyse_JRA_ReactionLoads_SO.sto'))
    }
    
    # Create summary figure
    print("\nCreating summary comparison figure...")
    summary_path = os.path.join(output_dir, 'model_comparison_summary.png')
    create_comparison_summary_figure(
        model1_data, model2_data, 
        model1_name="BG", model2_name="Katya",
        output_path=summary_path
    )
    
    # Create muscle force comparison if data available
    if model1_data['forces'] is not None and model2_data['forces'] is not None:
        print("\nCreating muscle force comparison figure...")
        
        # Get common muscles
        muscles1 = set(model1_data['forces'].columns) - {'time'}
        muscles2 = set(model2_data['forces'].columns) - {'time'}
        common_muscles = list(muscles1 & muscles2)[:20]  # Limit to 20 muscles
        
        if common_muscles:
            muscle_path = os.path.join(output_dir, 'muscle_forces_comparison.png')
            create_muscle_comparison_grid(
                model1_data['forces'], model2_data['forces'],
                common_muscles,
                model1_name="BG SO", model2_name="Katya SO",
                output_path=muscle_path
            )
    
    # Create JRA comparison if data available
    if model1_data['jra'] is not None and model2_data['jra'] is not None:
        print("\nCreating JRA comparison figure...")
        jra_path = os.path.join(output_dir, 'jra_comparison.png')
        
        # Extract joint names dynamically from column names
        force_components = ['_X', '_Y', '_Z', '_sum']
        all_cols = set(model1_data['jra'].columns) | set(model2_data['jra'].columns)
        joint_list = list(set([col.split('_')[0] for col in all_cols 
                              if any(comp in col for comp in force_components) and col != 'time']))[:3]  # Limit to 3 joints
        
        create_jra_comparison_figure(
            model1_data['jra'], model2_data['jra'],
            joint_list=joint_list if joint_list else None,
            model1_name="BG", model2_name="Katya",
            output_path=jra_path
        )
    
    print("\n" + "=" * 60)
    print("Summary figures generation complete!")
    print(f"Output directory: {output_dir}")
    plt.show()
