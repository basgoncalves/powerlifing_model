import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Read the data
filepath = input("Please provide the path to the CEINMS Executable Results CSV file: ")
df = pd.read_csv(filepath)

# Set up the figure with 2x2 subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Effects of Parameters on Model Performance', fontsize=16)

# Define colors for Alpha values
alpha_colors = {1: 'red', 10: 'blue'}
alpha_labels = {1: 'Alpha=1', 10: 'Alpha=10'}

# Plot 1: RMSE_Moments vs Gamma (colored by Alpha)
ax1 = axes[0, 0]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax1.scatter(alpha_data['Gamma'], alpha_data['RMSE_Moments'], 
               c=alpha_colors[alpha_val], label=alpha_labels[alpha_val], 
               s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
ax1.set_xlabel('Gamma')
ax1.set_ylabel('RMSE Moments')
ax1.set_title('RMSE Moments vs Gamma')
ax1.set_xscale('log')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: R²_Moments vs Gamma (colored by Alpha)
ax2 = axes[0, 1]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax2.scatter(alpha_data['Gamma'], alpha_data['R2_Moments'], 
               c=alpha_colors[alpha_val], label=alpha_labels[alpha_val], 
               s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
ax2.set_xlabel('Gamma')
ax2.set_ylabel('R² Moments')
ax2.set_title('R² Moments vs Gamma')
ax2.set_xscale('log')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: RMSE_Excitations vs Beta (colored by Alpha)
ax3 = axes[1, 0]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax3.scatter(alpha_data['Beta'], alpha_data['RMSE_Excitations'], 
               c=alpha_colors[alpha_val], label=alpha_labels[alpha_val], 
               s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
ax3.set_xlabel('Beta')
ax3.set_ylabel('RMSE Excitations')
ax3.set_title('RMSE Excitations vs Beta')
ax3.set_xscale('log')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: R²_Excitations vs Beta (colored by Alpha)
ax4 = axes[1, 1]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax4.scatter(alpha_data['Beta'], alpha_data['R2_Excitations'], 
               c=alpha_colors[alpha_val], label=alpha_labels[alpha_val], 
               s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
ax4.set_xlabel('Beta')
ax4.set_ylabel('R² Excitations')
ax4.set_title('R² Excitations vs Beta')
ax4.set_xscale('log')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
savepath = filepath.replace('.csv', '_Parameter_Effects.png')
plt.savefig(savepath)

# Additional plot: All metrics vs both Gamma and Beta
fig2, axes2 = plt.subplots(2, 2, figsize=(16, 12))
fig2.suptitle('All Metrics vs Gamma and Beta (Alpha as colors)', fontsize=16)

# RMSE Moments
ax1 = axes2[0, 0]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax1.scatter(alpha_data['Gamma'], alpha_data['RMSE_Moments'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Gamma', 
               s=60, alpha=0.7, marker='o')
    ax1.scatter(alpha_data['Beta'], alpha_data['RMSE_Moments'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Beta', 
               s=60, alpha=0.7, marker='^')
ax1.set_xlabel('Parameter Value (Gamma=circles, Beta=triangles)')
ax1.set_ylabel('RMSE Moments')
ax1.set_title('RMSE Moments vs Gamma & Beta')
ax1.set_xscale('log')
ax1.legend()
ax1.grid(True, alpha=0.3)

# R² Moments
ax2 = axes2[0, 1]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax2.scatter(alpha_data['Gamma'], alpha_data['R2_Moments'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Gamma', 
               s=60, alpha=0.7, marker='o')
    ax2.scatter(alpha_data['Beta'], alpha_data['R2_Moments'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Beta', 
               s=60, alpha=0.7, marker='^')
ax2.set_xlabel('Parameter Value (Gamma=circles, Beta=triangles)')
ax2.set_ylabel('R² Moments')
ax2.set_title('R² Moments vs Gamma & Beta')
ax2.set_xscale('log')
ax2.legend()
ax2.grid(True, alpha=0.3)

# RMSE Excitations
ax3 = axes2[1, 0]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax3.scatter(alpha_data['Gamma'], alpha_data['RMSE_Excitations'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Gamma', 
               s=60, alpha=0.7, marker='o')
    ax3.scatter(alpha_data['Beta'], alpha_data['RMSE_Excitations'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Beta', 
               s=60, alpha=0.7, marker='^')
ax3.set_xlabel('Parameter Value (Gamma=circles, Beta=triangles)')
ax3.set_ylabel('RMSE Excitations')
ax3.set_title('RMSE Excitations vs Gamma & Beta')
ax3.set_xscale('log')
ax3.legend()
ax3.grid(True, alpha=0.3)

# R² Excitations
ax4 = axes2[1, 1]
for alpha_val in df['Alpha'].unique():
    alpha_data = df[df['Alpha'] == alpha_val]
    ax4.scatter(alpha_data['Gamma'], alpha_data['R2_Excitations'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Gamma', 
               s=60, alpha=0.7, marker='o')
    ax4.scatter(alpha_data['Beta'], alpha_data['R2_Excitations'], 
               c=alpha_colors[alpha_val], label=f'{alpha_labels[alpha_val]} vs Beta', 
               s=60, alpha=0.7, marker='^')
ax4.set_xlabel('Parameter Value (Gamma=circles, Beta=triangles)')
ax4.set_ylabel('R² Excitations')
ax4.set_title('R² Excitations vs Gamma & Beta')
ax4.set_xscale('log')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print summary statistics
print("Parameter Effects Summary:")
print("="*50)
print(f"Best RMSE_Moments: {df['RMSE_Moments'].min():.3f} - {df.loc[df['RMSE_Moments'].idxmin(), ['Alpha', 'Beta', 'Gamma']].to_dict()}")
print(f"Best R2_Moments: {df['R2_Moments'].max():.3f} - {df.loc[df['R2_Moments'].idxmax(), ['Alpha', 'Beta', 'Gamma']].to_dict()}")
print(f"Best RMSE_Excitations: {df['RMSE_Excitations'].min():.3f} - {df.loc[df['RMSE_Excitations'].idxmin(), ['Alpha', 'Beta', 'Gamma']].to_dict()}")
print(f"Best R2_Excitations: {df['R2_Excitations'].max():.3f} - {df.loc[df['R2_Excitations'].idxmax(), ['Alpha', 'Beta', 'Gamma']].to_dict()}")