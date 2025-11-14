#------------------------------------------------------------------------#
# Copyright (c) 2015 Modenese L., Ceseracciu, E., Reggiani M., Lloyd, D.G.#
#                                                                         #
# Licensed under the Apache License, Version 2.0 (the "License");         #
# you may not use this file except in compliance with the License.        #
# You may obtain a copy of the License at                                 #
# http://www.apache.org/licenses/LICENSE-2.0.                             #
#                                                                         # 
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or         #
# implied. See the License for the specific language governing            #
# permissions and limitations under the License.                          #
#                                                                         #
#    Author: Luca Modenese, August 2014                                   #
#                            revised for paper May 2015                   #
#    email:    l.modenese@sheffield.ac.uk                                 # 
#    adapted by Basilio Goncalves                                         #
# ----------------------------------------------------------------------- #

import os
import warnings
from matplotlib import pyplot as plt
import opensim as osim

def main(osim_model_ref_filepath=None, osim_model_targ_filepath=None):
    # ========= USER SETTINGS =======
    # model files with paths
    if osim_model_ref_filepath is None:
        osim_model_ref_filepath = input("Please provide the path to the reference model: ").strip('"')
    if osim_model_targ_filepath is None:
        osim_model_targ_filepath = input("Please provide the path to the target model: ").strip('"')
    optimized_model_folder = os.path.dirname(osim_model_targ_filepath)
    
    # evaluations
    n_eval = 10
    # ===============================

    # initializing folders and log file
    log_folder = optimized_model_folder
    
    # checking if results folder exists. If not, create it.
    if not os.path.isdir(optimized_model_folder):
        warnings.warn(f'Folder {optimized_model_folder} does not exist. It will be created.')
        os.makedirs(optimized_model_folder)

    # optimizing target model based on reference model for n_eval points per
    # degree of freedom
    osim_model_opt, sims_info = optim_muscle_params(osim_model_ref_filepath,
                                                    osim_model_targ_filepath,
                                                    n_eval,
                                                    log_folder)

    # printing the optimized model
    output_path = osim_model_targ_filepath.replace('.osim', f'_opt_N{n_eval}.osim')
    osim_model_opt.printToXML(output_path)
    print(f'Optimized model saved to: {output_path}')
    
    # plotting optimization results
    plot_optimization_results(osim_model_targ_filepath, output_path)

def optim_muscle_params(ref_filepath, targ_filepath, n_eval, log_folder):
    """
    Optimize muscle parameters based on reference and target models.
    
    Parameters:
    -----------
    ref_filepath : str
        Path to reference OpenSim model
    targ_filepath : str
        Path to target OpenSim model
    n_eval : int
        Number of evaluations per degree of freedom
    log_folder : str
        Folder for logging optimization results
    
    Returns:
    --------
    tuple
        Optimized model and simulation info
    """
    # This function needs to be implemented based on the MuscleOptimizer
    # functionality. This is a placeholder for the actual optimization logic.
    
    # Load the models
    ref_model = osim.Model(ref_filepath)
    targ_model = osim.Model(targ_filepath)
    
    # Placeholder for optimization logic
    # The actual implementation would involve muscle parameter optimization
    
    # For now, return the target model as optimized (placeholder)
    sims_info = [None] * n_eval  # Placeholder for simulation info
    
    return targ_model, sims_info

def plot_optimization_results(intial_model_path, optimised_model_path):

    base_model = osim.Model(intial_model_path)
    optimized_model = osim.Model(optimised_model_path)
    
    muscles = base_model.getMuscles()
    n_muscles = muscles.getSize()
    
    params = ['optimal_fiber_length', 'tendon_slack_length', 'pennation_angle_at_optimal']
    fig, axes = plt.subplots(len(params), 1, figsize=(8, 12))
    
    for ax, param in zip(axes, params):
        ax.set_title(param.replace('_', ' ').title())
        ax.set_xlabel('Muscle Index')
        ax.set_ylabel(param.replace('_', ' ').title())
        for i in range(n_muscles):
            muscle = muscles.get(i)
            muscle_name = muscle.getName()
            base_muscle = base_model.getMuscles().get(muscle_name)
            optim_muscle = optimized_model.getMuscles().get(muscle_name)
            if param == 'optimal_fiber_length':
                base_value = base_muscle.getOptimalFiberLength()
                optim_value = optim_muscle.getOptimalFiberLength()
            elif param == 'tendon_slack_length':
                base_value = base_muscle.getTendonSlackLength()
                optim_value = optim_muscle.getTendonSlackLength()
            elif param == 'pennation_angle_at_optimal':
                base_value = base_muscle.getPennationAngleAtOptimalFiberLength()
                optim_value = optim_muscle.getPennationAngleAtOptimalFiberLength()
            
            # bar plot
            ax.bar(i - 0.2, base_value, width=0.4, label='Base' if i == 0 else "", color='b')
            ax.bar(i + 0.2, optim_value, width=0.4, label='Optimized' if i == 0 else "", color='r')
        ax.legend()    
    plt.tight_layout()
    
    save_path = optimised_model_path.replace('.osim', '_muscle_params.png')
    plt.savefig(save_path)
    print(f'Optimization results plot saved to {save_path}')

if __name__ == "__main__":
    main()