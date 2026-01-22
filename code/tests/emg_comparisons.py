"""
EMG Comparisons
Compare EMG signals with model-predicted activations and excitations.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Optional
from scipy.stats import pearsonr
from sklearn.metrics import mean_squared_error, r2_score

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


def compare_emg_with_activations(
    emg_data: pd.DataFrame,
    activation_data: pd.DataFrame,
    muscle_mapping: Dict[str, List[str]],
    trial_name: str = "Trial",
    output_path: str = None
):
    """
    Compare EMG signals with model-predicted activations.
    
    Args:
        emg_data: DataFrame with EMG signals
        activation_data: DataFrame with model activations
        muscle_mapping: Dictionary mapping EMG labels to muscle names
        trial_name: Name of trial for plot title
        output_path: Path to save comparison figure
        
    Returns:
        Dictionary with comparison metrics and figure
    """
    print(f"Comparing EMG with activations for {trial_name}")
    
    # Get time columns
    emg_time = 'time' if 'time' in emg_data.columns else emg_data.columns[0]
    act_time = 'time' if 'time' in activation_data.columns else activation_data.columns[0]
    
    # Find common muscles
    emg_muscles = [col for col in emg_data.columns if col != emg_time]
    
    # Create comparison figure
    n_muscles = min(len(emg_muscles), 12)  # Limit to 12 for readability
    n_cols = 4
    n_rows = int(np.ceil(n_muscles / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, n_rows * 3), constrained_layout=True)
    axes = axes.flatten() if n_muscles > 1 else [axes]
    
    fig.suptitle(f'EMG vs Model Activations - {trial_name}', fontsize=16, fontweight='bold')
    
    comparison_metrics = {}
    
    for idx, emg_label in enumerate(emg_muscles[:n_muscles]):
        ax = axes[idx]
        
        # Get corresponding muscle names from mapping
        mapped_muscles = muscle_mapping.get(emg_label, [emg_label])
        
        # Plot EMG signal
        ax.plot(emg_data[emg_time], emg_data[emg_label], 
               label='EMG', linewidth=2, color='blue', alpha=0.7)
        
        # Plot corresponding activation(s)
        colors = ['red', 'orange', 'purple']
        for i, muscle in enumerate(mapped_muscles[:3]):  # Max 3 muscles per EMG
            if muscle in activation_data.columns:
                ax.plot(activation_data[act_time], activation_data[muscle], 
                       label=f'Model: {muscle}', linewidth=2, 
                       color=colors[i % len(colors)], linestyle='--', alpha=0.7)
                
                # Calculate correlation if time series match
                if len(emg_data) == len(activation_data):
                    try:
                        corr, p_value = pearsonr(emg_data[emg_label], activation_data[muscle])
                        rmse = np.sqrt(mean_squared_error(emg_data[emg_label], activation_data[muscle]))
                        
                        comparison_metrics[f'{emg_label}_{muscle}'] = {
                            'correlation': corr,
                            'p_value': p_value,
                            'rmse': rmse
                        }
                    except Exception as e:
                        print(f"Could not calculate metrics for {emg_label} vs {muscle}: {e}")
        
        ax.set_title(f'{emg_label}', fontsize=10)
        ax.set_xlabel('Time (s)', fontsize=8)
        ax.set_ylabel('Activation/Excitation', fontsize=8)
        ax.set_ylim([0, 1.05])
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7)
    
    # Hide unused subplots
    for idx in range(n_muscles, len(axes)):
        axes[idx].axis('off')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"EMG comparison figure saved to: {output_path}")
    
    return {'metrics': comparison_metrics, 'figure': fig}


def create_emg_validation_report(
    comparison_metrics: Dict,
    output_path: str = None
):
    """
    Create a validation report summarizing EMG-activation comparisons.
    
    Args:
        comparison_metrics: Dictionary with comparison metrics
        output_path: Path to save report
        
    Returns:
        DataFrame with summary statistics
    """
    print("Creating EMG validation report")
    
    # Extract metrics into DataFrame
    data = []
    for key, metrics in comparison_metrics.items():
        emg_muscle = key.split('_')
        emg_label = emg_muscle[0]
        muscle_name = '_'.join(emg_muscle[1:])
        
        data.append({
            'EMG_Label': emg_label,
            'Muscle': muscle_name,
            'Correlation': metrics['correlation'],
            'P_Value': metrics['p_value'],
            'RMSE': metrics['rmse']
        })
    
    df = pd.DataFrame(data)
    
    # Sort by correlation
    df = df.sort_values('Correlation', ascending=False)
    
    # Create summary statistics
    print("\nEMG Validation Summary:")
    print("=" * 60)
    print(f"Total comparisons: {len(df)}")
    print(f"Mean correlation: {df['Correlation'].mean():.3f}")
    print(f"Median correlation: {df['Correlation'].median():.3f}")
    print(f"Mean RMSE: {df['RMSE'].mean():.3f}")
    print(f"Significant correlations (p<0.05): {(df['P_Value'] < 0.05).sum()}")
    print("\nTop 5 correlations:")
    print(df[['EMG_Label', 'Muscle', 'Correlation', 'RMSE']].head())
    
    if output_path:
        df.to_csv(output_path, index=False)
        print(f"\nValidation report saved to: {output_path}")
    
    return df


def plot_emg_comparison_summary(
    comparison_metrics: Dict,
    output_path: str = None
):
    """
    Create summary plots of EMG-activation comparison metrics.
    
    Args:
        comparison_metrics: Dictionary with comparison metrics
        output_path: Path to save summary figure
        
    Returns:
        Figure object
    """
    # Extract data
    correlations = [m['correlation'] for m in comparison_metrics.values()]
    rmse_values = [m['rmse'] for m in comparison_metrics.values()]
    labels = list(comparison_metrics.keys())
    
    # Create summary figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), constrained_layout=True)
    
    fig.suptitle('EMG-Activation Comparison Summary', fontsize=16, fontweight='bold')
    
    # Histogram of correlations
    ax = axes[0]
    ax.hist(correlations, bins=20, color='blue', alpha=0.7, edgecolor='black')
    ax.axvline(np.mean(correlations), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(correlations):.3f}')
    ax.set_xlabel('Correlation Coefficient')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of Correlations')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Histogram of RMSE
    ax = axes[1]
    ax.hist(rmse_values, bins=20, color='green', alpha=0.7, edgecolor='black')
    ax.axvline(np.mean(rmse_values), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(rmse_values):.3f}')
    ax.set_xlabel('RMSE')
    ax.set_ylabel('Frequency')
    ax.set_title('Distribution of RMSE')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Scatter plot: Correlation vs RMSE
    ax = axes[2]
    ax.scatter(correlations, rmse_values, alpha=0.6, s=50, color='purple')
    ax.set_xlabel('Correlation Coefficient')
    ax.set_ylabel('RMSE')
    ax.set_title('Correlation vs RMSE')
    ax.grid(True, alpha=0.3)
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Summary plot saved to: {output_path}")
    
    return fig


if __name__ == "__main__":
    print("EMG Comparison Tool")
    print("=" * 60)
    
    # Get input files
    emg_file = input("Enter path to EMG data file (.sto/.csv): ").strip('"')
    activation_file = input("Enter path to activation data file (.sto): ").strip('"')
    output_dir = input("Enter output directory for results: ").strip('"')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    print("\nLoading data files...")
    emg_data = utils.load_any_data_file(emg_file)
    activation_data = utils.load_any_data_file(activation_file)
    
    # Get muscle mapping
    muscle_mapping = utils.CEINMSParameters().EMG_muscle_mapping
    
    # Perform comparison
    trial_name = input("Enter trial name for plots: ").strip() or "Trial"
    
    comparison_output = os.path.join(output_dir, 'emg_activation_comparison.png')
    results = compare_emg_with_activations(
        emg_data,
        activation_data,
        muscle_mapping,
        trial_name,
        comparison_output
    )
    
    # Create validation report
    if results['metrics']:
        report_path = os.path.join(output_dir, 'emg_validation_report.csv')
        df_report = create_emg_validation_report(results['metrics'], report_path)
        
        # Create summary plots
        summary_plot_path = os.path.join(output_dir, 'emg_comparison_summary.png')
        plot_emg_comparison_summary(results['metrics'], summary_plot_path)
    
    print("\n" + "=" * 60)
    print("EMG comparison complete!")
    print(f"Results saved to: {output_dir}")
    
    plt.show()
