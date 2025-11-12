import math
import os
import shutil
import time
import sys
import re

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.offsetbox import AnchoredText

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk

import numpy as np
import pandas as pd

import xml.etree.ElementTree as ET
import xml.dom.minidom

import opensim as osim

import c3d
from scipy import signal

import settings
import ceinms
import openSim
test = 1

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

class Analyse(settings.Inputs):
    '''
    Contains paths from the user settings and functions to implement in the OpenSim/Ceinms analysis
    
    subject_name: Name of the subject (or the trial path if session_name and trial_name are None)
    '''
    def __init__(self, trialPath=None, settingsXML=None):
        super().__init__()
        
        if not trialPath and not settingsXML:
            trialPath = input("Enter the trial path: ")
        
        # if settingsXML provided, load settings from there
        if settingsXML and os.path.exists(settingsXML):
            self.load_settings(settingsXML)
            return
        else:
            
            # if trialPath does not exist, print error
            if not trialPath or not os.path.exists(trialPath):
                print(f"Trial path not found: {trialPath}")
                return
            
            # check for trial_settings.xml in trialPath
            self.settingsXML = os.path.relpath(os.path.join(trialPath, 'trial_settings.xml'), trialPath)
            if os.path.exists(self.settingsXML):
                self.load_settings(self.settingsXML)
                return

            # Create paths based on trialPath and settings.Inputs()
            path_parts = os.path.normpath(trialPath).split(os.sep)
            self.subject = path_parts[-3]
            self.session = path_parts[-2]
            self.trial = path_parts[-1]

            self.path = os.path.join(settings.SIMULATIONS_DIR, self.subject, self.session, self.trial)
            self.parentdir = os.path.dirname(self.path)
                
            self.TIME_RANGE = []
            inputs = settings.Inputs(parentdir=self.path)
            for varInput in inputs.__dict__.items():
                filepath = os.path.join(self.path, varInput[1])
                if os.path.exists(filepath):
                    setattr(self, varInput[0], os.path.relpath(filepath, self.path))
                else:
                    setattr(self, varInput[0], varInput[1])
                
            # add ceinms parameters
            ceinms_params = settings.CEINMSParameters()
            for varParam in ceinms_params.__dict__.items():
                setattr(self, varParam[0], varParam[1])
            
            self.MODEL = os.path.relpath(os.path.join(settings.MODELS_DIR, self.subject, self.session, settings.MODEL_NAME), self.path)
            self.TIME_RANGE = self.get_time_range()
            
            if not os.path.exists(self.settingsXML):
                self._to_xml()
                
    def reset(self):
        '''Delete all output files for the trial. Outputs set in settings.Outputs() '''
        for key, step in self.items():
            if step.output:
                output_path = os.path.join(self.path, step.output)
                if os.path.exists(output_path):
                    if os.path.isfile(output_path):
                        os.remove(output_path)
                        print(f"Deleted file: {output_path}")
                    elif os.path.isdir(output_path):
                        shutil.rmtree(output_path)
                        print(f"Deleted directory: {output_path}")
                else:
                    print(f"Output file does not exist, nothing to delete: {output_path}")
    
    def load_inputs(self):
        """Load all input files for the trial into dataframes."""
        for key, step in self.inputFiles.items():
            input_path = os.path.join(self.path, step)
            if os.path.exists(input_path):
                try:
                    data = pd.read_csv(input_path, delim_whitespace=True)
                    setattr(self, key.lower(), data)
                    print(f"Loaded input file: {input_path}")
                except Exception as e:
                    print(f"Error loading input file {input_path}: {e}")
            else:
                print(f"Input file does not exist: {input_path}")
    
    def load_outputs(self):
        """Load all output files for the trial into dataframes."""
        for key, step in self.__dict__.items():
        
            output_path = os.path.join(self.path, step)
            if os.path.exists(output_path):
                try:
                    data = load_any_data_file(output_path)
                    setattr(self, key.lower(), data)
                    print(f"Loaded output file: {output_path}")
                except Exception as e:
                    print(f"Error loading output file {output_path}: {e}")
            else:
                print(f"Output file does not exist: {output_path}")
    
    def _to_xml(self):
        '''Print all settings for the trial to an xml in trial.path'''
        
        root = ET.Element("TrialSettings")
        for attr, value in self.__dict__.items():
            
            if isinstance(value, (str, int, float, bool, list, dict)):
                child = ET.SubElement(root, attr)
                if os.path.exists(str(value)):
                    child.text = rel_path(str(value), self.path)
                else:
                    child.text = str(value)
            else:
                for sub_attr, sub_value in value.__dict__.items():
                    child = ET.SubElement(root, f"{sub_attr}")
                    if os.path.exists(str(sub_value)):
                        child.text = rel_path(str(sub_value), self.path)
                    else:
                        child.text = str(sub_value)
                
        tree = ET.ElementTree(root)
        save_pretty_xml(tree, self.settingsXML)
        print(f"Trial settings saved to: {self.settingsXML}")
    
    def load_settings(self, settingsXML):
        '''Load all settings for the trial from an xml in trial.path'''
        tree = ET.parse(settingsXML)
        root = tree.getroot()
    
        self.settingsXML = settingsXML
        
        for variable in root:
            var_name = variable.tag
            var_value = variable.text
            
            # Check if the attribute already exists
            if hasattr(self, var_name):
                current_attr = getattr(self, var_name)
                
                # Determine the type of the current attribute and convert accordingly
                if isinstance(current_attr, bool):
                    converted_value = var_value.lower() == 'true'
                elif isinstance(current_attr, int):
                    converted_value = int(var_value)
                elif isinstance(current_attr, float):
                    converted_value = float(var_value)
                elif isinstance(current_attr, list):
                    # Assuming list of strings separated by commas
                    converted_value = var_value.strip('[]').split(', ')
                else:
                    converted_value = var_value
            else:
                converted_value = var_value  # Default to string if attribute doesn't exist
            
            setattr(self, var_name, converted_value)
            
            # update self.path if path variable
            if var_name == "path":
                parent_dir = os.path.dirname(settingsXML)
                self.path = os.path.abspath(os.path.join(parent_dir, converted_value))
                
            if var_name == "TIME_RANGE":
                # Convert string representation of list to actual list of floats
                converted_value = re.findall(r"[-+]?\d*\.\d+|\d+", var_value)
                converted_value = [float(num) for num in converted_value]
                setattr(self, var_name, converted_value)

    def get_time_range(self):
        os.chdir(self.path)
        if os.path.exists(self.EVENTS):
            event_data = pd.read_csv(self.EVENTS, index_col=None, header=None)
            self.TIME_RANGE = [event_data.iloc[:, 1].min(), event_data.iloc[:, 1].max()]
            return self.TIME_RANGE

        if os.path.exists(self.MARKERS):
            marker_data = load_any_data_file(self.MARKERS)
            self.TIME_RANGE = [marker_data['time'].min(), marker_data['time'].max()]
            return self.TIME_RANGE

        if os.path.exists(self.C3D):
            c3d_data = load_any_data_file(self.C3D)
            self.TIME_RANGE = [c3d_data['time'].min(), c3d_data['time'].max()]
            return self.TIME_RANGE

    def check_paths(self):
        """Check if all input and output file paths exist."""
        for key, step in self.items():
            if step.input:
                input_path = os.path.join(self.path, step.input)
                if not os.path.exists(input_path):
                    print(f"Input file does not exist: {input_path}")
        
    def increase_muscle_force(self, factor=1, replace: bool = False):
        """Increase muscle force in the scaled model by a given factor.
        
        Args:
            factor (float): Factor to increase muscle force by. Default is 1.5.
            replace (bool): Whether to replace existing modified model. Default is False.
        """
        if not os.path.exists(self.MODEL):
            print(f"Scaled model not found: {self.MODEL}")
            return

        new_model_path = self.MODEL.replace('.osim', f'_increased_{factor:.2f}.osim')

        if os.path.exists(new_model_path) and not replace:
            print(f"Modified model already exists: {new_model_path}")
            self.USED_MODEL = new_model_path
            return
        
        # Load the model
        model = osim.Model(self.USED_MODEL)
        state = model.initSystem()
        
        # Increase max isometric force for each muscle
        for i in range(model.getMuscles().getSize()):
            muscle = model.getMuscles().get(i)
            original_force = muscle.getMaxIsometricForce()
            new_force = original_force * factor
            muscle.setMaxIsometricForce(new_force)
            print(f"Muscle: {muscle.getName()}, Original Force: {original_force:.2f}, New Force: {new_force:.2f}")
        
        # Save the modified model
        model.printToXML(new_model_path)
        print(f"Modified model saved to: {new_model_path}")
        
        # Update the used model path
        self.USED_MODEL = new_model_path
    
    def scale_emg(self, scale_factor=1.0):
        """Scale EMG data by a given factor and save to a new file.
        
        Args:
            scale_factor (float): Factor to scale EMG data by. Default is 1.0.
        """
        os.chdir(self.path)
        if not os.path.exists(self.EMG_NORMALISED):
            print(f"EMG normalised file not found: {self.EMG_NORMALISED}")
            return
        
        emg_data = load_any_data_file(self.EMG_NORMALISED)
        
        # Scale all columns except 'time'
        for col in emg_data.columns:
            if col != 'time':
                emg_data[col] *= scale_factor
        
        scaled_emg_path = self.EMG_NORMALISED.replace('.sto', f'_scaled_{scale_factor:.2f}.sto')
        write_sto_file(emg_data, os.path.abspath(scaled_emg_path))
        print(f"Scaled EMG data saved to: {scaled_emg_path}")

        # Update the EMG normalised path
        self.EMG_NORMALISED = scaled_emg_path
        
        self._to_xml()
        
    # analyses to run
    def export_c3d(self):
        pass

    def run_ik(self):
        os.chdir(os.path.abspath(self.path))
        
        if not os.path.exists(self.setupIK):            
            openSim.create_setup_IK(osim_modelPath=self.MODEL,
                                marker_trc=self.MARKERS,
                                ik_output=self.IK,
                                taskSetPath=None,
                                time_range=self.TIME_RANGE,
                                saveXMLPath=self.setupIK)
        
        if os.path.exists(self.IK) and not settings.Execute().replace:
            return
        
        try:
            openSim.run_ik(osim_modelPath=self.MODEL,
                    marker_trc=self.MARKERS,
                    ik_output=self.IK,
                    setup_xml=self.setupIK,
                    time_range=self.TIME_RANGE,
                    resultsDir=self.path)
            print_to_log(f'[Success] Inverse Kinematics completed. Results are saved in {self.path}')
        except Exception as e:
            print_to_log(f'[Error] during Inverse Kinematics: {e}')
            
    def run_id(self):
        
        os.chdir(self.path)

        if not os.path.exists(self.setupGRF):            
            template_grf_path = os.path.join(settings.SETUP_DIR, settings.Inputs().setupGRF)
            shutil.copyfile(template_grf_path, self.setupGRF)

        if os.path.exists(self.ID) and not settings.Execute().replace:
            return
        
        try:
            openSim.run_id(osimModelPath=self.MODEL,
                    ikOutputPath=self.IK,
                    grfXmlPath=self.setupGRF,
                    setupXmlPath=self.setupID)
            
            print_to_log(f'[Success] Inverse Dynamics completed. Results are saved in {self.ID}')
        except Exception as e:
            print_to_log(f'[Error] during Inverse Dynamics: {e}')
    
    def run_ma(self):
        
        os.chdir(self.path)
        if os.path.exists(self.MA) and not settings.Execute().replace:
            return
        
        try:
            openSim.run_ma(osim_modelPath=self.MODEL,
                        ik_output=self.IK,
                        grf_xml=self.setupGRF)
            print_to_log(f'[Success] Muscle Analysis completed. Results are saved in {self.MA}')
        except Exception as e:
            print_to_log(f'[Error] during Muscle Analysis: {e}')
    
    def run_so(self):
        
        os.chdir(self.path)

        if not os.path.exists(self.ACTUATORS_SO):            
            template_actuators_path = os.path.join(settings.SETUP_DIR, settings.Inputs().ACTUATORS_SO)
            shutil.copyfile(template_actuators_path, self.ACTUATORS_SO)
        
        if os.path.exists(self.SO_forces) and not settings.Execute().replace:
            return
        try:
            openSim.run_so(osim_modelPath=self.MODEL,
                    ik_output=self.IK,
                    grf_xml=self.setupGRF,
                    setup_xml=self.setupSO,
                    actuators=self.ACTUATORS_SO,
                    resultsDir=self.path)
            print_to_log(f'[Success] Static Optimization completed. Results are saved in {self.path} and {self.SO_activations}')
        except Exception as e:
            print_to_log(f'[Error] during Static Optimization: {e}')
        
    def run_jra(self):
        
        os.chdir(self.path)
        if not os.path.exists(self.setupJRA):
            template_jra_path = os.path.join(settings.SETUP_DIR, settings.Inputs().setupJRA)
            shutil.copyfile(template_jra_path, self.setupJRA)
             
        if os.path.exists(self.JRA) and not settings.Execute().replace:
            return
        try:
            openSim.run_jra(osim_modelPath=self.MODEL,
                     ik_output=self.IK,
                     grf_xml=self.setupGRF,
                     setup_xml=self.setupJRA,
                     actuators=None,
                     muscle_force_path=self.JRA_FORCES,
                     saveFileName=self.JRA)
        
            print_to_log(f"JRA analysis complete. Results saved {os.path.abspath(self.JRA)}")
        except Exception as e:
            print_to_log(f'[Error] during Joint Reaction Analysis: {e}')
            
    def run_jra_ceinms(self):
        
        os.chdir(self.path)
        if os.path.exists(self.JRA_CEINMS) and not settings.Execute().replace:
            return
        
        try:
            openSim.run_jra(osim_modelPath=self.MODEL,
                     ik_output=self.IK,
                     grf_xml=self.setupGRF,
                     setup_xml=self.setupJRA,
                     actuators=None,
                     muscle_force_path=self.JRA_FORCES_CEINMS,
                     saveFileName=self.JRA_CEINMS)
            print_to_log(f"JRA CEINMS analysis complete. Results saved {os.path.abspath(self.JRA_CEINMS)}")
        except Exception as e:
            print_to_log(f'[Error] during Joint Reaction Analysis CEINMS: {e}')
        
    def run_emg_normalise(self):
        
        os.chdir(self.path)
        emg_normalise_list = []
        
        for trialName in os.listdir(self.parentdir):
            emgPath = os.path.join(self.parentdir, trialName, settings.Inputs().EMG_FILTERED)
            if os.path.exists(emgPath):
                emg_normalise_list.append(emgPath)
        
        openSim.EMG_normalise(target_emg_path= str(self.EMG_FILTERED),
                                normalise_emg_list=emg_normalise_list)
    
    @staticmethod
    def muscles_per_coordinate(osimModel, coord_name):
        muscles = []
        indexes = []
        coord = osimModel.getCoordinateSet().get(coord_name)
        state = osimModel.initSystem()
        osimModel.realizePosition(state)

        for i in range(osimModel.getMuscles().getSize()):
            muscle = osimModel.getMuscles().get(i)
            if abs(muscle.computeMomentArm(state, coord)) > 1e-4:
                muscles.append(muscle.getName())
                indexes.append(i)

        return muscles, indexes
    
    #--- Valid
    def compare_marker_locations(self):
        try:
            openSim.compare_marker_locations(marker_experimental_path=os.path.abspath(self.MARKERS),
                                        marker_virtual_path=os.path.abspath(self.MODEL_MARKERS))
        
            print_to_log(f'[Success] Marker location comparison completed: {self.MODEL_MARKERS} vs {self.MARKERS}')
        except Exception as e:
            print_to_log(f'[Error] during marker location comparison: {e}')

    def plot(self,trialList,columns_to_plot):
        
        if columns_to_plot == 'all':

            columns_to_plot.remove('time')
        
        plt.figure(figsize=(10,6))
        for trial in trialList:
            plt.plot(trial.joint_angles[columns_to_plot], label=trial.name)
        plt.legend([trial.name for trial in trialList])
    
    def plot_create_subplot(self, n_muscles, fig=None):
        ncols = int(math.ceil(math.sqrt(n_muscles)))
        nrows = int(math.ceil(n_muscles / ncols))
        if fig is None:
            fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*5, nrows*4), constrained_layout=True)
            axes = axes.flatten()
        else:
            axes = fig.get_axes()

        # Hide any unused subplots
        for i in range(n_muscles, len(axes)):
            axes[i].axis('off')
        
        return fig, axes
      
    def plot_moment_arms(self, coord_name: str = None, fig=None):
        
        os.chdir(self.path)
        fileList = os.listdir(self.MA)
        fileList = [file for file in fileList if file.startswith('_MuscleAnalysis_MomentArm') and file.endswith('.sto')]
        
        for file in fileList:
            filepath = self.MA + '\\' + file
            if coord_name in file:
                break
            else:
                continue
        
        dof = file.replace('.sto','').replace('_MuscleAnalysis_MomentArm_','')
        print(f"Loading moment arms for DOF: {dof} from {file}")
        moment_arms = load_any_data_file(filepath)
        muscleList,muscleIdx = self.muscles_per_coordinate(osim.Model(self.USED_MODEL), dof)
        
        n_muscles = len(muscleList)
        if n_muscles == 0:
            print(f"No muscles found for DOF: {dof}")
            return None, None
        
        ncols = int(math.ceil(math.sqrt(n_muscles)))
        nrows = int(math.ceil(n_muscles / ncols))
        if fig is None:
            fig, axes = self.plot_create_subplot(n_muscles)
        else:
            axes = fig.get_axes()
        

        fig.suptitle(f"Moment Arms for DOF: {dof}", fontsize=16)
        line_label = f'{self.subject}_{self.session}_{self.trial}'
        for muscle in muscleList:
            ax = axes[muscleList.index(muscle)]
            ax.plot(moment_arms[muscle], label=line_label)
            ax.set_title(f"{muscle}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Moment Arm")
        
        axes[0].legend()
        return fig, axes
            
    def plot_ik(self, columns_to_plot='all'):
        self.joint_angles = load_any_data_file(self.IK)
        
        if columns_to_plot == 'all':
            columns_to_plot = list(self.joint_angles.columns)
            columns_to_plot.remove('time')
        
        n_vars = len(columns_to_plot)
        fig, axes = self.plot_create_subplot(n_vars)
        
        fig.suptitle(f"Inverse Kinematics Joint Angles: {self.trial}", fontsize=16)
        for var in columns_to_plot:
            ax = axes[columns_to_plot.index(var)]
            ax.plot(self.joint_angles['time'], self.joint_angles[var], label=self.trial)
            ax.set_title(f"{var}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Angle (degrees)")
        
        axes[0].legend()
        
        # save figure and return
        plt.savefig(os.path.join(self.path, f"{self.trial}_IK_Joint_Angles.png"))
        print(f'Figure saved to {os.path.join(self.path, f"{self.trial}_IK_Joint_Angles.png")}')
        
        return fig, axes
    
    def plot_id(self, columns_to_plot='all'):
        self.inverse_dynamics = load_any_data_file(self.ID)
        
        if columns_to_plot == 'all':
            columns_to_plot = list(self.inverse_dynamics.columns)
            columns_to_plot.remove('time')
        
        n_vars = len(columns_to_plot)
        fig, axes = self.plot_create_subplot(n_vars)
        
        fig.suptitle(f"Inverse Dynamics Joint Moments: {self.trial}", fontsize=16)
        for var in columns_to_plot:
            ax = axes[columns_to_plot.index(var)]
            ax.plot(self.inverse_dynamics['time'], self.inverse_dynamics[var], label=self.trial)
            ax.set_title(f"{var}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Moment (Nm)")
        
        axes[0].legend()
        
        # save figure and return
        plt.savefig(os.path.join(self.path, f"{self.trial}_ID_Joint_Moments.png"))
        print(f'Figure saved to {os.path.join(self.path, f"{self.trial}_ID_Joint_Moments.png")}')
        
        return fig, axes
    
    def plot_so(self):
        self.so_forces = load_any_data_file(self.SO_forces)
        self.so_activations = load_any_data_file(self.SO_activations)
        
        muscleGroups = settings.Muscle_Groups
        
        n_vars = len(muscleGroups)
        fig, axes = self.plot_create_subplot(n_vars)
        
        fig.suptitle(f"Static Optimization Muscle Forces: {self.trial}", fontsize=16)
        for i, (group, muscles) in enumerate(muscleGroups.items()):
            ax = axes[i]
            muscleForces = self.so_forces[muscles].sum(axis=1)
            line1 = ax.plot(self.so_forces['time'], muscleForces, label='Force')
            # on a secondary y-axis plot activations
            activations = self.so_activations[muscles].mean(axis=1)
            ax2 = ax.twinx()
            line2 = ax2.plot(self.so_activations['time'], activations, color='orange', linestyle='--', label='Activation')

            ax.set_title(f"{group}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Force (N)")
            ax2.set_ylabel("Activation")
            
            if i == 0:
                # Combine lines from both axes
                lines = line1 + line2
                labels = [l.get_label() for l in lines]
                ax.legend(lines, labels, loc='upper right')
        
        # save figure and return
        plt.savefig(os.path.join(self.path, f"{self.trial}_SO_Muscle_Forces.png"))
        print(f'Figure saved to {os.path.join(self.path, f"{self.trial}_SO_Muscle_Forces.png")}')
        
        return fig, axes
    
    def plot_jra(self):
        self.jra_results = load_any_data_file(self.JRA)
        
        joints = settings.JCF_Groups

        n_vars = len(joints)
        fig, axes = self.plot_create_subplot(n_vars*4)
        
        fig.suptitle(f"Joint Reaction Analysis: {self.trial}", fontsize=16)
        i_subplot = -1
        for row, (joint, components) in enumerate(joints.items()):
                        
            # 3d sum of reaction forces
            x = self.jra_results[components[0]]
            y = self.jra_results[components[1]]
            z = self.jra_results[components[2]]
            resultant = np.sqrt(x**2 + y**2 + z**2)
            
            i_subplot += 1  
            ax = axes[i_subplot]
            ax.plot(self.jra_results['time'], x, label='X')
            ax.set_title(f"{joint} - X Reaction Force")
            ax.set_ylabel("Reaction Force (N)")
            
            i_subplot += 1
            ax = axes[i_subplot]
            ax.plot(self.jra_results['time'], y, label='Y')
            ax.set_title(f"{joint} - Y Reaction Force")
            
            i_subplot += 1
            ax = axes[i_subplot]
            ax.plot(self.jra_results['time'], z, label='Z')
            ax.set_title(f"{joint} - Z Reaction Force")
            
            i_subplot += 1
            ax = axes[i_subplot]
            ax.plot(self.jra_results['time'], resultant, label='Resultant')
            ax.set_title(f"{joint} - Resultant Reaction Force")

            ax.set_ylabel("Reaction Force (N)")

            if row == 0:
                ax.legend(loc='upper right')
                
            if row == n_vars - 1:
                ax.set_xlabel("Time")
        
        # save figure and return
        savePath = os.path.join(self.path, f"{self.trial}_JRA_Results.png")
        plt.savefig(savePath)
        print(f'Figure saved to {savePath}')

        return fig, axes
    
    def plot_emg(self):
        self.emg_data = load_any_data_file(self.inputFiles.EMG_NORMALISED)
        
        muscles = self.emg_data.columns

        n_vars = len(muscles)
        fig, axes = self.plot_create_subplot(n_vars)
        
        fig.suptitle(f"EMG Excitations: {self.trial}", fontsize=16)
        for i, muscle in enumerate(muscles):
            ax = axes[i]
            ax.plot(self.emg_data['time'], self.emg_data[muscle], label=muscle)

            ax.set_title(f"{muscle}")
            ax.set_xlabel("Time")
            ax.set_ylabel("Excitation")
            ax.set_ylim([0, 1])
            
            if i == 0:
                ax.legend(loc='upper right')
        
        # save figure and return
        savePath = os.path.join(self.inputFiles.EMG_NORMALISED.replace('.sto','.png'))
        plt.savefig(savePath)
        print(f'Figure saved to {savePath}')

        return fig, axes
    
    def plot_summary(self):
        '''
        plot summary of all analyses for the trial
        
        row 1 - IK joint angles
        row 2 - ID joint moments and CEINMS joint moments
        row 3 - SO muscle forces and CEINMS forces
        row 4 - EMG excitations, SO activations, CEINMS activations
        row 5 - Norm Fiber lengths
        row 6 - Joint Reaction Forces
        '''
        # load all data
        self.joint_angles = load_any_data_file(self.IK)
        self.inverse_dynamics = load_any_data_file(self.ID)
        self.so_forces = load_any_data_file(self.SO_forces)
        self.so_activations = load_any_data_file(self.SO_activations)
        self.jra_results = load_any_data_file(self.JRA)
        self.emg_data = load_any_data_file(self.EMG_NORMALISED)

        self.ceinms_activations = load_any_data_file(os.path.join(self.CEINMS_EXE_DIR, 'Activations.sto'))
        self.ceinms_forces = load_any_data_file(os.path.join(self.CEINMS_EXE_DIR, 'MuscleForces.sto'))
        
        breakpoint()
        n_rows = 6
        fig, axes = plt.subplots(n_rows, 1, figsize=(15, n_rows*4), constrained_layout=True)
        
    # ceinms
    def create_ceinms_model(self):
        os.chdir(self.path)
        ceinms.create_ceinms_model(osimModelPath=self.MODEL, 
                                   outputCEINMSModelPath=self.CEINMS_UNCALIBRATED_MODEL)
    
    def create_ceinms_input_data(self):
        os.chdir(self.path)
        ceinms.create_input_data(MAFolder=self.MA,
                                  excitationsFile=self.CEINMS_EXCITATIONS,
                                  motionFile=self.IK,
                                  externalTorquesFile=self.ID,
                                  externalLoadsFile=self.setupGRF,
                                  startStopTime=self.TIME_RANGE)
    
    def create_ceinms_calibration_gfc(self):
        """
        Create ceinms_cfg_calibration.xml for CEINMS calibration.
        """
        
        os.chdir(self.path)
        inputPaths = []
        for trial_name in settings.CEINMS_CALIBRATION_TRIALS:
            filepath = os.path.join(self.parentdir, trial_name, settings.Inputs().CEINMS_INPUT_DATA)
            inputPaths.append(os.path.relpath(filepath, self.parentdir))
        
        ceinms.create_calibrationCfg(osimModelPath=self.MODEL,
                                     inputPaths=inputPaths,
                                     outputPath=self.CEINMS_CALIBRATION_CFG)

    def create_excitation_generator(self):
        os.chdir(self.path)
        ceinms.create_excitation_generator(osim_model_path=self.MODEL,
                                           emg_path=self.CEINMS_EXCITATIONS,
                                           save_path=self.CEINMS_EXCITATION_GENERATOR
        )
    
    def create_ceinms_cfg_from_excitation_generator(self):
        """
        Create ceinms_cfg_optimise.xml based on excitationGenerator.xml
        
        Args:
            excitation_file: Path to excitationGenerator.xml
            output_file: Path for output ceinms_cfg_optimise.xml
        """
        excitation_file = self.inputFiles.CEINMS_EXCITATIONS
        output_file = self.setupFiles.CEINMS_CALIBRATION_CFG
        
        # Parse the excitation generator XML
        tree = ET.parse(excitation_file)
        root = tree.getroot()
        
        # Lists to store muscle names
        synth_mtus = []
        adjust_mtus = []
        
        # Find all excitation elements
        mapping = root.find('mapping')
        if mapping is not None:
            for excitation in mapping.findall('excitation'):
                muscle_id = excitation.get('id')
                
                # Check if excitation has input elements (non-empty)
                inputs = excitation.findall('input')
                if inputs and len(inputs) > 0:
                    # Has EMG input - add to adjustMTUs
                    adjust_mtus.append(muscle_id)
                else:
                    # No EMG input - add to synthMTUs
                    synth_mtus.append(muscle_id)
        
        # Sort the lists for consistent output
        synth_mtus.sort()
        adjust_mtus.sort()
        
        # Create the XML structure
        execution = ET.Element('execution')
        
        # Add XML declaration attributes
        execution.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        
        nms_model = ET.SubElement(execution, 'NMSmodel')
        type_elem = ET.SubElement(nms_model, 'type')
        hybrid = ET.SubElement(type_elem, 'hybrid')
        
        # Add hybrid parameters
        ET.SubElement(hybrid, 'alpha').text = '1'
        ET.SubElement(hybrid, 'beta').text = '4'
        ET.SubElement(hybrid, 'gamma').text = '120'
        
        # Add DOF set (you may need to adjust this based on your model)
        dof_set = ET.SubElement(hybrid, 'dofSet')
        dof_set.text = ' '.join(settings.DOFs)
        
        # Add synthMTUs
        synth_mtus_elem = ET.SubElement(hybrid, 'synthMTUs')
        synth_mtus_elem.text = ' '.join(synth_mtus)
        
        # Add adjustMTUs
        adjust_mtus_elem = ET.SubElement(hybrid, 'adjustMTUs')
        adjust_mtus_elem.text = ' '.join(adjust_mtus)
        
        # Add algorithm section
        algorithm = ET.SubElement(hybrid, 'algorithm')
        sim_annealing = ET.SubElement(algorithm, 'simulatedAnnealing')
        ET.SubElement(sim_annealing, 'noEpsilon').text = '4'
        ET.SubElement(sim_annealing, 'rt').text = '0.3'
        ET.SubElement(sim_annealing, 'T').text = '20000'
        ET.SubElement(sim_annealing, 'NS').text = '15'
        ET.SubElement(sim_annealing, 'NT').text = '5'
        ET.SubElement(sim_annealing, 'epsilon').text = '0.001'
        ET.SubElement(sim_annealing, 'maxNoEval').text = '200000'
        
        # Add tendon section
        tendon = ET.SubElement(nms_model, 'tendon')
        equilibrium = ET.SubElement(tendon, 'equilibriumElastic')
        ET.SubElement(equilibrium, 'tolerance').text = '1e-09'
        
        # Add activation section
        activation = ET.SubElement(nms_model, 'activation')
        ET.SubElement(activation, 'exponential')
        
        # Create tree and write to file
        tree = ET.ElementTree(execution)
        save_pretty_xml(tree, output_file)
        
        print(f"Created {output_file}")
        print(f"synthMTUs: {len(synth_mtus)} muscles")
        print(f"adjustMTUs: {len(adjust_mtus)} muscles")
    
    def create_ceinms_calibration_setup(self):
        os.chdir(self.path)
        ceinms.create_calibrationSetupXML(uncalibratedCEINMSModelPath=self.CEINMS_UNCALIBRATED_MODEL,
                                           excitationGeneratorFile=self.CEINMS_EXCITATION_GENERATOR,
                                           calibrationCfgPath=self.CEINMS_CALIBRATION_CFG,
                                           outputSubjectFile=self.CEINMS_CALIBRATED_MODEL,
                                           outputDirectory=self.CEINMS_CALIBRATION_DIR,
                                           setupXMLPath=self.CEINMS_CALIBRATION_SETUP)

    def run_ceinms_calibration(self):        
        
        start_time = time.time()
        os.chdir(self.path)
        
        ceinms.plot_ceinms_model_parameters(self.CEINMS_UNCALIBRATED_MODEL)
        
        calibrationSetupPath = os.path.abspath(self.CEINMS_CALIBRATION_SETUP)
        ceinms.calibrate(setupXML_path=calibrationSetupPath)
        
        # if date modified of calibrated model is after start time, assume success
        os.chdir(self.path)
        mod_time = os.path.getmtime(self.CEINMS_CALIBRATED_MODEL)
        if mod_time >= start_time:
            print_to_log(f'CEINMS calibration completed successfully in {mod_time - start_time:.2f} seconds.')
            ceinms.plot_ceinms_model_parameters(self.CEINMS_CALIBRATED_MODEL)
            
            try:
                ceinmsTorquesFile = os.path.join(self.CEINMS_CALIBRATION_DIR, 'Moments_inputData.csv')
                ceinms.plot_moments_calibration_results(momentResultsCSV=ceinmsTorquesFile)
            except:
                print_to_log(f'Could not plot moments vs CEINMS results.')
                
            try:
                ceinms.plot_compare_ceinms_models(uncalibratedModelPath=self.CEINMS_UNCALIBRATED_MODEL,
                                                 calibratedModelPath=self.CEINMS_CALIBRATED_MODEL)
                print_to_log(f'Could not plot EMG vs CEINMS results.')
            except:
                print_to_log(f'Could not plot EMG vs CEINMS results.')
        else:
            print_to_log(f'CEINMS calibration may have failed: calibrated model not updated.')
            
    def create_ceinms_optimise_setup(self):
        os.chdir(self.path)
        ceinms.create_optimise_setupXML(ceinmsModelPath=self.CEINMS_CALIBRATED_MODEL, 
                            inputDataFile=self.CEINMS_INPUT_DATA,
                             calibrationCfgPath=self.CEINMS_OPTIMISE_CFG,
                             excitationGeneratorFilePath=self.CEINMS_EXCITATION_GENERATOR,
                             outputDirectory=self.CEINMS_OPTIMISATION_DIR,
                             setupXMLPath=self.CEINMS_OPTIMISE_SETUP)

    def create_ceinms_exe_setup(self):

        root = ET.Element('ceinms')
        ET.SubElement(root, 'subjectFile').text = os.path.relpath(self.CEINMS_CALIBRATED_MODEL, self.path)
        ET.SubElement(root, 'inputDataFile').text = os.path.relpath(self.CEINMS_INPUT_DATA, self.path)
        ET.SubElement(root, 'executionFile').text = os.path.relpath(self.CEINMS_OPTIMISE_CFG, self.path)
        ET.SubElement(root, 'excitationGeneratorFile').text = os.path.relpath(self.CEINMS_EXCITATION_GENERATOR, self.path)
        ET.SubElement(root, 'outputDirectory').text = os.path.relpath(self.CEINMS_EXE_DIR, self.path)

        # Create tree and write to file
        tree = ET.ElementTree(root)
        save_pretty_xml(tree, self.CEINMS_EXE_SETUP)
        print(f"Created {self.CEINMS_EXE_SETUP}")

    def run_ceinms_exe(self):
        
        os.chdir(self.path)
        ceinms.executable(setupXML_path=os.path.abspath(self.CEINMS_EXE_SETUP))
    
    def run_ceinms_optimise(self):
        
        os.chdir(self.path)
        setupAbsPath = os.path.abspath(self.CEINMS_OPTIMISE_SETUP)
        ceinms.optimise(setupXML_path=setupAbsPath)

        try:    
            adjustedEMG_path = os.path.join(self.CEINMS_OPTIMISATION_DIR, 'AdjustedEmgs.sto')
            torqueCEINMS_path = os.path.join(self.CEINMS_OPTIMISATION_DIR, 'Torques.sto')
            ceinms.plot_experimental_vs_ceinms(emgFile=self.EMG_NORMALISED,
                                               ceinmsExcitationsFile=adjustedEMG_path,
                                               excitationGeneratorFile=self.CEINMS_EXCITATION_GENERATOR,
                                                externalMomentsFile=self.ID,
                                                ceinmsTorquesFile=torqueCEINMS_path)
            print_to_log(f'Plotted Experimental vs CEINMS results {self.path}')
        except:
            print_to_log(f'Could not plot EMG vs CEINMS results {self.path}')
    
    def run_ceinms_exe_loop(self):
        
        os.chdir(self.path)
        ceinms.executable_loop(setupXML_path=os.path.abspath(self.CEINMS_EXE_SETUP),
                               cfgXML_path=os.path.abspath(self.CEINMS_EXE_CFG),
                               alphas=settings.CEINMSParameters().alphas,
                               betas=settings.CEINMSParameters().betas,
                               gammas=settings.CEINMSParameters().gammas
                            )
    

def cmd_analysis(trialPath=None):
    
    if not trialPath or not os.path.exists(trialPath):
        trialPath = input("Please provide the path to the trial directory: ")
        
        trial = Analyse(trialPath)
        options = ['export_c3d', 'run_ik', 'run_id', 'run_ma', 
                   'run_so', 'run_jra', 'run_jra_ceinms',]
        while True:
            command = input(f'Enter command ({", ".join(options)}): ').strip().lower()
            trial = Analyse(trialPath)
            if command == 'export_c3d':
                trial.export_c3d()
            elif command == 'run_ik':
                trial.run_ik()
            elif command == 'run_id':
                trial.run_id()
            elif command == 'run_ma':
                trial.run_ma()
            elif command == 'run_so':
                trial.run_so()
            elif command == 'run_jra':
                trial.run_jra()
               
            


def print_to_log(message, terminal=False):
    """
    Prints a message to the console and logs it to a file.
    
    Args:
        message (str): The message to print and log.
    """
    timestamp = time.strftime('%d.%m.%Y_%H:%M:%S', time.localtime()) + f":{int((time.time() % 1) * 1000):03d}"
    print(f'{timestamp} {message}')
    with open(MODULE_DIR + '\\log.txt', 'a') as log_file:
        log_file.write(f'{timestamp}: {message}\n')
        
    if terminal:
        print(message)

def rel_path(path, relative_to):
    """
    Returns the relative path from the given path to the code directory.
    
    Args:
        path (str): The path to convert.
        relative_to (str): The base path to which the relative path is calculated.
        
    Returns:
        str: The relative path.
    """
    return os.path.relpath(path, relative_to)

def check_path(path, create=False, isdir=False):
    """Check if a path exists and is a directory."""
    if not os.path.exists(path):        
        if create:
            try:
                os.makedirs(path)
                print("[INFO] Created directory:", path)
            except Exception as e:
                print("[ERROR] Could not create directory:", path, "Error:", e)
        else:
            print("[ERROR] Path does not exist:", path)
    if isdir and not os.path.isdir(path):
        print("[ERROR] Path is not a directory:", path)

    return path, os.path.isdir(path)

def load_c3d(path=None, output=0):
    """
    Load a .c3d file into a pandas DataFrame.

    Args:
        path (str): The path to the .c3d file. If None, prompts for input.
        output (int): If 1, prints the columns of the DataFrame.

    Returns:
        pd.DataFrame: The loaded data from the .c3d file.
    """
    
    if not check_path(path):
        path = input("Please provide the path to the .c3d file: ")

    try:
        reader = c3d.Reader(open(path, 'rb'))
        breakpoint()
        return reader 
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None
        
def load_trc(path=None, output=False, combine_headers=False):
    
    if not check_path(path):
        path = input("Please provide the path to the .trc file: ")

    # find line with '#Frame' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'Frame#' in line:
                    header_start_line = i
                    break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None
    
    df = pd.read_csv(path,sep='\t',skiprows=header_start_line,index_col=False)
    
    # Create a temporary frame from the multi-index, forward-fill, and get values
    markers = df.columns.tolist()
    coordinates = df.iloc[0].to_list()  # First row contains sub-headers

    # replace Unnamed with empty cells
    for idx, marker in enumerate(markers):
        if marker.startswith('Unnamed'):
            markers[idx] = markers[idx-1]
    
    coordinates = [coord if not pd.isna(coord) else '' for coord in coordinates]

    # create multi-index dataFrame and delete row 0
    df.columns = pd.MultiIndex.from_tuples(zip(markers, coordinates), names=['Marker', 'Coordinate'])
    df = df.iloc[2:]
    
    # if needed make 'time' lower case (only)
    if 'Time' in df.columns:
        df = df.rename(columns={'Time': 'time'})
        
    # if needed combine headers
    if combine_headers:
        df.columns = df.columns.map(lambda x: f"{x[0]}_{x[1]}" if x[1] else x[0])

    if output == 1: print(df.columns)

    return df

def load_sto(path=None, output=0):
    """
    Load a .sto file into a pandas DataFrame.

    Args:
        path (str): The path to the .sto file. If None, prompts for input.
        output (int): If 1, prints the columns of the DataFrame.

    Returns:
        pd.DataFrame: The loaded data from the .sto file.
    """
    
    if not check_path(path):
        path = input("Please provide the path to the .sto file: ")

    # find line with 'endheader' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'endheader' in line or i > 100:  # Limit to first 100 lines to avoid long files
                        break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None

    # read the file into a pandas DataFrame, skipping the header
    try:
        columns = []
        offset = -3
        while 'time' not in columns:
            try:    
                data = pd.read_csv(path, sep= '\s+', header=i+offset)
                columns = data.columns
                offset += 1
                if offset > 100:
                    print(f"Error: Could not find 'time' column in the file {path}. Please check the file format.")
                    return None
            except pd.errors.ParserError:
                offset += 1
                
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None

    if output == 1: print(data.columns)

    return data

def load_grf_mot(path=None, output=0):
    
    if not check_path(path):
        path = input("Please provide the path to the .mot file: ")

    # find line with 'endheader' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'endheader' in line:
                        break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None

    # read the file into a pandas DataFrame, skipping the header
    try:
        data = pd.read_csv(path, sep= '\s+', header=i+1)
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None

    if output == 1: print(data.columns)

    return data

def load_data_file(file_path):
    """
    Loads the motion capture data file into a pandas DataFrame.

    This function reads the header to extract metadata and then loads the
    actual data into a structured DataFrame.

    Args:
        file_path (str): The path to the data file.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: The loaded data.
            - dict: A dictionary with the file's metadata.
    """
    metadata = {}
    header_lines = []
    
    # Read the header part of the file first to extract metadata
    with open(file_path, 'r') as f:
        for i in range(5):  # First 5 lines are metadata or headers
            line = f.readline().strip()
            header_lines.append(line)
            if i < 2: # The first two lines contain key-value metadata
                parts = line.split('\t')
                for j in range(0, len(parts), 2):
                    if j + 1 < len(parts) and parts[j]:
                        metadata[parts[j]] = parts[j+1]

    # The 4th line contains the main column headers (FHD, RBHD, etc.)
    # The 5th line contains the sub-column headers (X1, Y1, etc.)
    main_headers = re.split(r'\s+', header_lines[3].strip())[2:] # Skip first two empty items
    sub_headers = re.split(r'\s+', header_lines[4].strip())[2:] # Skip first two items

    # Create a MultiIndex (hierarchical column names) for the DataFrame
    # This matches your file's structure (e.g., FHD -> X1, Y1, Z1)
    header_tuples = []
    i = 0
    for main_header in main_headers:
        if main_header: # Check if it's not an empty string
            # Each main header corresponds to a set of sub-headers (e.g., X, Y, Z coordinates)
            num_sub_headers = 3 # Assuming X, Y, Z for markers. Adjust if needed.
            for j in range(num_sub_headers):
                header_tuples.append((main_header, sub_headers[i]))
                i += 1

    # Define the column names for the first two columns
    final_column_names = [('Frame', '#'), ('Time', '')] + header_tuples

    # Load the actual data, skipping the header rows
    data = pd.read_csv(
        file_path,
        sep='\t',        # Data is separated by tabs
        header=None,     # We are providing our own column names
        skiprows=6,      # Skip the metadata and header lines we already processed
        engine='python'  # Use python engine for more flexibility with separators
    )
    
    # Assign the hierarchical column names to the DataFrame
    data.columns = pd.MultiIndex.from_tuples(final_column_names)

    return data, metadata

def load_any_data_file(file_path):
    """
    Loads any data file (TRC, MOT, STO, C3D) into a pandas DataFrame.

    Args:
        file_path (str): The path to the data file.

    Returns:
        pd.DataFrame: The loaded data.
    """
    
    if file_path.endswith('.trc'):
        return load_trc(file_path)
    
    elif file_path.endswith('.mot'):
        return load_sto(file_path)
    
    elif file_path.endswith('.sto'):
        return load_sto(file_path)
    
    elif file_path.endswith('.c3d'):
        breakpoint()
        return load_c3d(file_path)
    
    elif file_path.endswith('.csv'):
        return pd.read_csv(file_path)
        
    elif file_path.endswith('.txt'):
        # Assuming these are plain text files with tab-separated values
        return pd.read_csv(file_path, sep='\t', header=0)
    
    elif file_path.endswith('.xml'):
        # For XML files, we can use the XML_tools module to read them
        tree = ET.parse(file_path)
        if tree is not None:
            return pd.DataFrame([elem.attrib for elem in tree.findall('.//')])
        else:
            raise ValueError(f"Could not read XML file: {file_path}")
    
    else:
        try:
            # Try to read as a generic text file
            with open(file_path, 'r') as f:
                data = f.readlines()
            # Assuming the first line is a header
            header = data[0].strip().split('\t')
            # Load the rest of the data into a DataFrame
            data = [line.strip().split('\t') for line in data[1:]]
            return pd.DataFrame(data, columns=header)
        
        except Exception as e:
            print(f"Error: Could not read the file at {file_path}. Please check the file format and try again.")
            print(f"Details: {e}")
            
def save_data_file(file_path, data, metadata):
    """
    Saves the DataFrame back to a file in the original format.

    Args:
        file_path (str): The path where the file will be saved.
        data (pd.DataFrame): The DataFrame to save.
        metadata (dict): The metadata to write to the header.
    """
    with open(file_path, 'w') as f:
        # Write metadata lines
        # This part reconstructs the first two header lines from the metadata dictionary
        # It's a bit manual to match the format exactly.
        f.write(f"PathFileType\t4\t(X/Y/Z)\t{metadata.get('PathFileType', '')}\n")
        f.write(f"DataRate\t{metadata.get('DataRate', '')}\tCameraRate\t{metadata.get('CameraRate', '')}\tNumFrames\t{metadata.get('NumFrames', '')}\tNumMarkers\t{metadata.get('NumMarkers', '')}\tUnits\t{metadata.get('Units', '')}\tOrigDataRate\t{metadata.get('OrigDataRate', '')}\tOrigDataStartFrame\t{metadata.get('OrigDataStartFrame', '')}\tOrigNumFrames\t{metadata.get('OrigNumFrames', '')}\n")
        f.write('\n') # The empty line
        
        # Reconstruct the column headers
        main_headers = data.columns.get_level_values(0)
        sub_headers = data.columns.get_level_values(1)
        
        # Write main headers line
        f.write("Frame#\tTime\t")
        unique_main_headers = main_headers.unique()
        # This logic ensures each main header is printed once and padded correctly
        header_line = ""
        last_main = ""
        for main in main_headers[2:]: # Skip Frame and Time
            if main != last_main:
                header_line += f"{main}\t\t\t" # Assuming 3 sub-columns, hence 3 tabs
                last_main = main
        f.write(header_line.strip() + '\n')

        # Write sub-headers line
        f.write("\t\t") # Align with the data columns
        f.write('\t'.join(sub_headers[2:]) + '\n')
        f.write('\n') # The final empty line before data

    # Append the data to the file
    data.to_csv(
        file_path,
        mode='a',          # Append to the file we just created with the header
        header=False,      # Don't write DataFrame headers again
        index=False,       # Don't write the DataFrame index
        sep='\t',          # Use tabs as separators
        float_format='%.6f'# Format floats to 6 decimal places
    )

def load_sto_header(file_path):
    """
    Loads the header of a .sto file and returns it as a list of strings.

    Args:
        file_path (str): The path to the .sto file.

    Returns:
        list: A list of strings representing the header lines.
    """
    header = []
    break_next = False
    with open(file_path, 'r') as f:
        for line in f:
            if break_next:
                break
            if 'endheader' in line:
                break_next = True
            header.append(line.strip())
    
    return header

def write_trc(markers_df, trc_file, units, frame_rate, first_frame):
    """
    Write marker data (frames, n_markers, 3) to TRC.
    """
    
    # remove time column
    time = markers_df["time"]
    markers_df = markers_df.drop(columns=["time"])
    
    num_frames = markers_df.shape[0]
    marker_labels = markers_df.columns.droplevel(1).to_list()
    
    # only unique labels
    marker_labels = list(dict.fromkeys(marker_labels))
    n_markers = len(marker_labels)

    with open(trc_file, "w") as writer:
        # Header
        writer.write(f"PathFileType\t4\t(X/Y/Z)\t{os.path.basename(writer.name)}\n")
        writer.write("DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n")
        writer.write(f"{frame_rate}\t{frame_rate}\t{num_frames}\t{n_markers}\t{units}\t{frame_rate}\t{first_frame}\t{num_frames}\n")

        # Marker names
        header = "Frame#\tTime\t" + "\t".join([f"{name}\t\t" for name in marker_labels]) + "\n"
        writer.write(header)

        # Coordinate labels
        coord_line = "\t\t" + "\t".join([f"X{i+1}\tY{i+1}\tZ{i+1}" for i in range(n_markers)]) + "\n"
        writer.write(coord_line)

        # Data rows
        for i in range(num_frames):
            frame_num = first_frame + i
            time_val = time.iloc[i]
            row = [f"{frame_num}", f"{time_val:.6f}"]
            row.extend([f"{coord:.6f}" for coord in markers_df.iloc[i].values])
            writer.write("\t".join(row) + "\n")

def write_mot(analog_df, labels, mot_file):
    """
    Write analog data (samples, n_channels) to MOT.
    
    inputs:
        labels: The labels for the analog channels.
        analog_df: The DataFrame containing the analog data.
        
    """
    
    # make sure labels include time
    labels = ['time'] + labels

    # Crop dataframe to include only labels
    analog_df = analog_df[labels]
    num_samples, num_columns = analog_df.shape
    
    # create writer
    with open(mot_file, "w") as writer:
        # Header
        writer.write(f"{os.path.basename(writer.name)}\n")
        writer.write("version=1\n")
        writer.write(f"nRows={num_samples}\n")
        writer.write(f"nColumns={num_columns}\n") 
        writer.write("in_degrees=yes\n")
        writer.write("endheader\n")

        # Column labels
        writer.write("\t".join(labels) + "\n")
    
        # Data rows
        for i, row in analog_df.iterrows():
            # breakpoint()
            writer.write(f"{row['time']:.6f}\t" + "\t".join([f"{val:.6f}" for val in row[1:]]) + "\n")

def write_sto_header(writer, dataFrame):
    """
    Writes the header for a .sto file.

    Args:
        writer (TextIOWrapper): The file writer object.
        dataFrame (pd.DataFrame): The DataFrame containing the data.
    """
    writer.write(f"{os.path.basename(writer.name)}\n")
    writer.write("version=1\n")
    writer.write(f"nRows={dataFrame.shape[0]}\n")
    writer.write(f"nColumns={dataFrame.shape[1]}\n")
    writer.write("in_degrees=yes\n")
    writer.write("endheader\n")

def write_sto_file(dataFrame, file_path):
    """
    Writes a pandas DataFrame to a .sto file with a specified header.

    Args:
        dataFrame (pd.DataFrame): The DataFrame to write.
        file_path (str): The path where the .sto file will be saved.
        header (list): A list of strings representing the header lines to write.
    """
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
        print(f"Created directory: {os.path.dirname(file_path)}")
        
    # make time lowercase
    if 'Time' in dataFrame.columns:
        dataFrame = dataFrame.rename(columns={"Time": "time"})
        

    with open(file_path, 'w', newline='') as f:
        # Write the header lines
        write_sto_header(f, dataFrame)

        # bring time column to front
        dataFrame = dataFrame[['time'] + [col for col in dataFrame.columns if col != 'time']]

        # Write the data without extra line spaces
        dataFrame.to_csv(f, sep='\t', index=False, float_format='%.6f')

def read_xml(path):
    """
    Reads an XML file and returns its content as a string.

    Args:
        path (str): The path to the XML file.

    Returns:
        str: The content of the XML file.
    """
    try:
        tree = ET.parse(path)
        return tree
    except FileNotFoundError:
        print(f"Error: The file at {path} does not exist.")
        return None
    except Exception as e:
        print(f"Error reading the file at {path}: {e}")
        return None

def dict_to_xml(parent_elem, data_dict):
    """
    Convert nested dictionary to XML elements recursively.
    Each dictionary key becomes an XML tag, handles unlimited nesting depth.
    """
    for key, value in data_dict.items():
        elem = ET.SubElement(parent_elem, key)

        if isinstance(value, dict):
            # Recursive call for nested dictionaries
            dict_to_xml(elem, value)
        elif isinstance(value, list):
            # Handle lists - each item becomes a separate element with same tag
            for item in value:
                if isinstance(item, dict):
                    dict_to_xml(elem, item)
                else:
                    item_elem = ET.SubElement(elem, "item")
                    item_elem.text = str(item)
        else:
            # If value is not a dict or list, set it as text content
            elem.text = str(value)

def save_pretty_xml(tree, save_path):
            """Saves the XML tree to a file with proper indentation and no blank lines."""
            rough_string = ET.tostring(tree.getroot(), 'utf-8')
            reparsed = xml.dom.minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="   ")
            # Remove blank lines
            pretty_xml_no_blanks = "\n".join([line for line in pretty_xml.splitlines() if line.strip()])
            with open(save_path, 'w') as file:
                file.write(pretty_xml_no_blanks)

# opensim 
def select_osim_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select OpenSim Model File",
        filetypes=[("OpenSim Model Files", "*.osim")]
    )
    root.destroy()
    return file_path

def muscles_per_coordinate(osimModel, coord_name):
    muscles = []
    indexes = []
    coord = osimModel.getCoordinateSet().get(coord_name)
    state = osimModel.initSystem()
    osimModel.realizePosition(state)

    for i in range(osimModel.getMuscles().getSize()):
        muscle = osimModel.getMuscles().get(i)
        if abs(muscle.computeMomentArm(state, coord)) > 1e-4:
            muscles.append(muscle.getName())
            indexes.append(i)

    return muscles, indexes

def checkMuscleMomentArms(osim_modelPath, ik_output, leg = 'l', threshold = 0.005):
# Adapted from Willi Koller: https://github.com/WilliKoller/OpenSimMatlabBasic/blob/main/checkMuscleMomentArms.m
# Only checked if works for for the Rajagopal and Catelli models

    def get_model_coord(model, coord_name):
        try:
            index = model.getCoordinateSet().getIndex(coord_name)
            coord = model.updCoordinateSet().get(index)
        except:
            index = None
            coord = None
            print(f'Coordinate {coord_name} not found in model')
        
        return index, coord

    def muscle_crosses_coordinate(muscle, coord_name):
        
        coord = model.getCoordinateSet().get(coord_name)
        # Check if the muscle crosses the specified coordinate
        for path in muscle.getGeometryPath().getAllPoints():
            if path.getName() == coord_name:
                return True
        return False

    # Load motions and model
    motion = osim.Storage(ik_output)
    model = osim.Model(osim_modelPath)

    # Initialize system and state
    model.initSystem()
    state = model.initSystem()

    # coordinate names
    HipflexIndex, HipflexCoord = get_model_coord(model, 'hip_flexion_' + leg)
    HiprotIndex, HipRotCoord = get_model_coord(model, 'hip_rotation_' + leg)
    HipAddIndex, HipAddCoord = get_model_coord(model, 'hip_adduction_' + leg)
    flexIndexLknee, flexCoordLknee = get_model_coord(model, 'knee_angle_' + leg)
    addIndexLknee, addCoordLknee = get_model_coord(model, 'knee_adduction_' + leg)
    flexIndexLank, flexCoordLank = get_model_coord(model, 'ankle_angle_' + leg)

    # get hip flexion muscles
    muscleNames_Hipflex, muscleIndices_Hipflex = muscles_per_coordinate(model, HipflexCoord.getName())
    flexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_Hipflex)))

    muscleNames_HipAdd, muscleIndices_HipAdd = muscles_per_coordinate(model, HipAddCoord.getName())
    addMomentArms = np.zeros((motion.getSize(), len(muscleIndices_HipAdd)))

    # get hip rotation muscles
    muscleNames_HipRot, muscleIndices_HipRot = muscles_per_coordinate(model, HipRotCoord.getName())
    rotMomentArms = np.zeros((motion.getSize(), len(muscleIndices_HipRot)))

    # get names of the knee muscles
    muscleNames_knee, muscleIndices_knee = muscles_per_coordinate(model, flexCoordLknee.getName())
    kneeFlexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_knee)))

    # get names of the ankle muscles
    muscleNames_ankle, muscleIndices_ankle = muscles_per_coordinate(model, flexCoordLank.getName())
    ankleFlexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_ankle)))

    # compute moment arms for each muscle and create time vector
    time_vector = []
    initial_time = time.time()
    for i in range(1, motion.getSize()):
        
        flexAngleL = motion.getStateVector(i-1).getData().get(HipflexIndex) / 180 * np.pi
        rotAngleL = motion.getStateVector(i-1).getData().get(HiprotIndex) / 180 * np.pi
        addAngleL = motion.getStateVector(i-1).getData().get(HipAddIndex) / 180 * np.pi
        flexAngleLknee = motion.getStateVector(i-1).getData().get(flexIndexLknee) / 180 * np.pi
        flexAngleLank = motion.getStateVector(i-1).getData().get(flexIndexLank) / 180 * np.pi

        time_vector.append(motion.getStateVector(i-1).getTime())
        # Update the state with the joint angle
        coordSet = model.updCoordinateSet()
        coordSet.get(HipflexIndex).setValue(state, flexAngleL)
        coordSet.get(HiprotIndex).setValue(state, rotAngleL)
        coordSet.get(HipAddIndex).setValue(state, addAngleL)
        coordSet.get(flexIndexLknee).setValue(state, flexAngleLknee)
        coordSet.get(flexIndexLank).setValue(state, flexAngleLank)

        # Realize the state to compute dependent quantities
        model.computeStateVariableDerivatives(state)
        model.realizeVelocity(state)

        # Compute the moment arm hip
        for j in range(len(muscleIndices_Hipflex)):
            muscleIndex = muscleIndices_Hipflex[j]
            if muscleNames_Hipflex[j][-1] == leg:
                flexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, HipflexCoord)
                flexMomentArms[i, j] = flexMomentArm

        # Compute the moment arm hip rotation
        for j in range(len(muscleIndices_HipRot)):
            muscleIndex = muscleIndices_HipRot[j]
            if muscleNames_HipRot[j][-1] == leg:
                rotMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, HipRotCoord)
                rotMomentArms[i, j] = rotMomentArm

                addMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, HipAddCoord)
                addMomentArms[i, j] = addMomentArm

        # Compute the moment arm knee
        for j in range(len(muscleNames_knee)):
            muscleIndex = muscleIndices_knee[j]
            if muscleNames_knee[j][-1] == leg:
                kneeFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLknee)
                kneeFlexMomentArms[i, j] = kneeFlexMomentArm

        # Compute the moment arm ankle
        for j in range(len(muscleNames_ankle)):
            muscleIndex = muscleIndices_ankle[j]
            if muscleNames_ankle[j][-1] == leg:
                ankleFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLank)
                ankleFlexMomentArms[i, j] = ankleFlexMomentArm

        # print time to compute one frame
        if i % 50 == 0:
            elapsed_time = time.time() - initial_time
            print(f"Time to compute frame {i}/{motion.getSize()}: {elapsed_time:.6f} seconds")
    # check discontinuities
    discontinuity = []
    muscle_action = []
    time_discontinuity = []

    fDistC = plt.figure('Discontinuity', figsize=(8, 8))
    plt.title(ik_output)

    save_folder = os.path.join(os.path.dirname(ik_output),'momentArmsCheck')

    def find_discontinuities(momArms, threshold, muscleNames, action, discontinuity, muscle_action, time_discontinuity):
        for i in range(momArms.shape[1]):
            dy = np.diff(momArms[:, i])
            discontinuity_indices = np.where(np.abs(dy) > threshold)[0]
            if discontinuity_indices.size > 0:
                print('Discontinuity detected at', muscleNames[i], 'at ', action, ' moment arm')
                plt.plot(momArms[:, i])
                plt.plot(discontinuity_indices, momArms[discontinuity_indices, i], 'rx')
                discontinuity.append(i)
                muscle_action.append(str(muscleNames[i] + ' ' + action + ' at frames: ' + str(discontinuity_indices)))
                time_discontinuity.append([time_vector[index] for index in discontinuity_indices])


        return discontinuity, muscle_action, time_discontinuity

    # hip flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        flexMomentArms, threshold, muscleNames_Hipflex, 'flexion', discontinuity, muscle_action, time_discontinuity)

    # hip adduction
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        addMomentArms, threshold, muscleNames_HipAdd, 'adduction', discontinuity, muscle_action, time_discontinuity)

    # hip rotation
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        rotMomentArms, threshold, muscleNames_HipRot, 'rotation', discontinuity, muscle_action, time_discontinuity)

    # knee flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        kneeFlexMomentArms, threshold, muscleNames_knee, 'flexion', discontinuity, muscle_action, time_discontinuity)
    
    # ankle flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        ankleFlexMomentArms, threshold, muscleNames_ankle, 'dorsiflexion', discontinuity, muscle_action, time_discontinuity)
    
    # plot discontinuities
    if len(discontinuity) > 0:
        plt.legend(muscle_action)
        plt.ylabel('Muscle Moment Arms with discontinuities (m)')
        plt.xlabel('Frame (after start time)')
        save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'discontinuities_' + leg + '.png'))
        print('\n\nYou should alter the model - most probably you have to reduce the radius of corresponding wrap objects for the identified muscles\n\n\n')

        # save txt file with discontinuities
        with open(os.path.join(save_folder, 'discontinuities_' + leg + '.txt'), 'w') as f:
            f.write(f"model file = {osim_modelPath}\n")
            f.write(f"motion file = {ik_output}\n")
            f.write(f"leg checked = {leg}\n")
            
            f.write("\n muscles with discontinuities \n", ) 
            
            for i in range(len(muscle_action)):
                try:
                    f.write("%s : time %s \n" % (muscle_action[i], time_discontinuity[i]))
                except:
                    print('no discontinuities detected')

        momentArmsAreWrong = 1
    else:
        plt.close(fDistC)
        print('No discontinuities detected')
        momentArmsAreWrong = 0

    # plot hip flexion
    plt.figure('flexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(flexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_Hipflex, loc='best')
    plt.ylabel('Hip Flexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_flex_MomentArms_' + leg + '.png'))

    # hip adduction
    plt.figure('addMomentArms_' + leg, figsize=(8, 8))
    plt.plot(addMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_HipAdd, loc='best')
    plt.ylabel('Hip Adduction Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_add_MomentArms_' + leg + '.png'))

    # hip rotation
    plt.figure('rotMomentArms_' + leg, figsize=(8, 8))
    plt.plot(rotMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_HipRot, loc='best')
    plt.ylabel('Hip Rotation Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_rot_MomentArms_' + leg + '.png'))

    # knee flexion
    plt.figure('kneeFlexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(kneeFlexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_knee, loc='best')
    plt.ylabel('Knee Flexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'knee_MomentArms_' + leg + '.png'))

    # ankle flexion
    plt.figure('ankleFlexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(ankleFlexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_ankle, loc='best')
    plt.ylabel('Ankle Dorsiflexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'ankle_MomentArms_' + leg + '.png'))

    print('Moment arms checked for ' + ik_output)
    print('Results saved in ' + save_folder + ' \n\n' )

    return momentArmsAreWrong,  discontinuity, muscle_action

def compareMomentArms(osimModelPath1, osimModelPath2, m, ikPath2, coord_name):

    osimModel1 = osim.Model(osimModelPath1)
    osimModel2 = osim.Model(osimModelPath2)
    
    muscles1, indexes1 = muscles_per_coordinate(osimModel1, coord_name)
    muscles2, indexes2 = muscles_per_coordinate(osimModel2, coord_name)

    common_muscles = set(muscles1).intersection(set(muscles2))
    unique_to_model1 = set(muscles1) - common_muscles
    unique_to_model2 = set(muscles2) - common_muscles
    
    for muscle in unique_to_model1:
        print(f"Muscle {muscle} is only in model 1")

    return common_muscles, unique_to_model1, unique_to_model2

def get_factor():
    '''Prompt the user to enter a factor to increase muscle force.'''
    root = tk.Tk()
    root.withdraw()
    factor = simpledialog.askfloat(
        "Increase Factor",
        "Enter factor to multiply max isometric force (e.g., 1.2):",
        minvalue=0.0
    )
    root.destroy()
    return factor

def increase_muscle_force(osim_file=None, factor=None, save_path=None):
    '''Increase the max isometric force of muscles in the given osim file.'''
    root = tk.Tk() # prevent the main window from appearing
    root.withdraw()
    if osim_file is None:
        osim_file = select_osim_file()
        
    if not osim_file:
        messagebox.showinfo("Cancelled", "No file selected.")
        return
    
    if factor is None:
        factor = get_factor()
        
    if not factor:
        messagebox.showinfo("Cancelled", "No factor entered.")
        return

    model = osim.Model(osim_file)
    muscles = model.getMuscles()
    for i in range(muscles.getSize()):
        muscle = muscles.get(i)
        orig_force = muscle.getMaxIsometricForce()
        muscle.setMaxIsometricForce(orig_force * factor)

    if save_path is None:
        new_file = osim_file.replace('.osim', f'_increased_{factor:.2f}.osim')
    else:
        new_file = save_path
        
    model.printToXML(new_file)
    messagebox.showinfo("Done", f"Saved new model to:\n{new_file}")

def get_muscle_params(osimModelPath, muscleNamesList, printOutput=False):
    """Get the parameters of the specified muscles from the OpenSim model."""
    
    osimModel = osim.Model(osimModelPath)
    muscleSet = osimModel.getMuscles()
    musclesList = []

    for i, muscleName in enumerate(muscleNamesList):
        muscle = muscleSet.get(muscleName)
        if muscle:
            muscle.max_isometric_force = muscle.getMaxIsometricForce()
            muscle.optimal_fiber_length = muscle.getOptimalFiberLength()
            muscle.tendon_slack_length = muscle.getTendonSlackLength()
            muscle.specific_tension_N_cm2 = 15  # 150 and 155 kN/m2 DOI 10.1152/jappl.2001.90.3.865
            muscle.pennation_angle_rad = muscle.getPennationAngleAtOptimalFiberLength()
            muscle.physiological_cross_sectional_area_cm2 = muscle.getMaxIsometricForce() / muscle.specific_tension_N_cm2

            musclesList.append(muscle)
        
    print(f'[WARNING] for this muscle set, specific tension was assumed as {muscle.specific_tension_N_cm2} N/cm2')
    
    if printOutput:
        for i, muscleName in enumerate(muscleNamesList): 
            muscle = musclesList[i]
            print(f"Muscle parameters for {muscleName}: {muscle.getName()}")
            print(f"  Max Isometric Force: {muscle.getMaxIsometricForce()} N")
            print(f"  Optimal Fiber Length: {muscle.getOptimalFiberLength()} m")
            print(f"  Tendon Slack Length: {muscle.getTendonSlackLength()} m")
            print(f"  Physiological Cross-Sectional Area: {muscle.physiological_cross_sectional_area_cm2} cm^2")
    
    # return both model and muscleList so muscles keep attributes
    return osimModel, musclesList

def check_arg(arg=None,name=None):
    if arg is None:
        arg = input(f"Please provide a value for {name}: ").strip('"')
    
    if arg.startswith('[') and arg.endswith(']'):
        arg = [float(x.strip()) for x in arg.strip('[]').split(',')]

    return arg

def compare_marker_locations(marker_experimental_path=None, marker_virtual_path=None):
    """
    Calculates the root mean square error between experimental and virtual markers.

    Args:
        marker_experimental_path (str, optional): Path to the experimental .trc file.
        marker_virtual_path (str, optional): Path to the virtual .sto markers file.
    """
    # Set up a root window for the file dialog but hide it
    root = tk.Tk()
    root.withdraw()

    # Select the trials if needed
    if not marker_experimental_path:
        marker_experimental_path = filedialog.askopenfilename(title='Select experimental .trc file', filetypes=[("TRC files", "*.trc")])
        if not marker_experimental_path: return # User cancelled

    if not marker_virtual_path:
        marker_virtual_path = filedialog.askopenfilename(title='Select virtual .sto markers file', filetypes=[("STO files", "*.sto")])
        if not marker_virtual_path: return # User cancelled

    virtual_markers_df = load_sto(marker_virtual_path)
    experimental_markers_df = load_trc(marker_experimental_path,
                                combine_headers=True)

    exp_marker_names = experimental_markers_df.columns.get_level_values(0).unique().tolist()
    
    # Find frames to plot in the experimental data
    time = virtual_markers_df['time']
    
    # Find the closest indices in experimental time to the start and end of virtual time
    exp_time = experimental_markers_df['time']
    initial_index = (exp_time - time.iloc[0]).abs().idxmin()
    final_index = (exp_time - time.iloc[-1]).abs().idxmin()

    distances = pd.DataFrame({'time': time.values})
    
    output_dir = os.path.dirname(marker_experimental_path)
    mean_errors_filename = os.path.join(output_dir, '_ik_marker_errors_mean.txt')

    print('Calculating marker errors for all markers...')
    with open(mean_errors_filename, 'w') as f_mean_errors:
        f_mean_errors.write('mean errors for each marker (m)\n\n')

        for marker_name in exp_marker_names:

            if 'time' in marker_name.lower() or 'frame' in marker_name.lower():
                continue

            try:
                marker_name = marker_name.split('_')[0]
                exp_cols = [col for col in exp_marker_names if col.split('_')[0] == marker_name]
                virtual_cols = [col for col in virtual_markers_df.columns if col.split('_')[0] == marker_name]

                if not exp_cols or not virtual_cols:
                    continue

                # Get experimental data for the current time range and convert mm to m
                exp_slice = experimental_markers_df.iloc[initial_index:final_index + 1]
                x1 = pd.to_numeric(exp_slice[exp_cols[0]], errors='coerce').values / 1000.0
                y1 = pd.to_numeric(exp_slice[exp_cols[1]], errors='coerce').values / 1000.0
                z1 = pd.to_numeric(exp_slice[exp_cols[2]], errors='coerce').values / 1000.0

                # Get virtual data
                x2 = virtual_markers_df[virtual_cols[0]].values
                y2 = virtual_markers_df[virtual_cols[1]].values
                z2 = virtual_markers_df[virtual_cols[2]].values
                
                # Ensure arrays are the same length by trimming the longer one
                min_len = min(len(x1), len(x2))
                x1, y1, z1 = x1[:min_len], y1[:min_len], z1[:min_len]
                x2, y2, z2 = x2[:min_len], y2[:min_len], z2[:min_len]
                
                # Calculate the 3D distance
                dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
                distances[marker_name] = pd.Series(dist)

                # Write mean error to file
                mean_error_text = f'{marker_name} = {np.mean(dist):.4f} m\n'
                f_mean_errors.write(mean_error_text)

            except (KeyError, IndexError) as e:
                print(f"Could not process marker '{marker_name}'. It might be missing in one of the files. Error: {e}")

    # Write all distance data to a .sto file
    all_errors_filename = os.path.join(output_dir, '_ik_marker_errors_all.sto')
    write_sto_file(distances.dropna(axis=1, how='all'), all_errors_filename)
    print(f"Mean errors saved to: {mean_errors_filename}")
    print(f"All error data saved to: {all_errors_filename}")
    
    
    # plot marker errors
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(12, 6))
    for marker_name in distances.columns:
        if marker_name != 'time':
            plt.plot(distances['time'], distances[marker_name], label=marker_name)
    plt.xlabel('Time (s)')
    plt.ylabel('Marker Error (m)')
    plt.title('Marker Errors Over Time')
    plt.legend()
    plt.grid()
    
    # save fig
    plt.savefig(os.path.join(output_dir, '_ik_marker_errors_plot.png'))
    plt.close()
    print(f"Marker errors plot saved to: {os.path.join(output_dir, '_ik_marker_errors_plot.png')}")

    return distances

# plotting
def save_fig(fig, save_path):
    """Saves the figure to the specified path."""
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    fig.savefig(save_path, bbox_inches='tight')
    print(f"Figure saved to {save_path}")

def get_screen_size():

    try:
        import tkinter as tk
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    except Exception as e:
        print(f"Error getting screen size: {e}")
        return None

def calculate_nRows_nCold(n_subplots):
    """
    Calculate the number of rows and columns for subplots based on the number of subplots.

    Args:
        n_subplots (int): The total number of subplots.

    Returns:
        tuple: (nrows, ncols) where nrows is the number of rows and ncols is the number of columns.
    """
    import numpy as np
    # Find the smallest nrows and ncols such that nrows * ncols >= n_subplots and (nrows-1) * ncols < n_subplots
    ncols = int(np.ceil(np.sqrt(n_subplots)))
    nrows = int(np.ceil(n_subplots / ncols))
    while (nrows - 1) * ncols >= n_subplots:
        nrows -= 1
    return nrows, ncols

# data manipulation
def time_normalise_df(df, fs=''):

    if not type(df) == pd.core.frame.DataFrame:
        raise Exception('Input must be a pandas DataFrame')
    
    if not fs:
        try:
            # mean sampling frequency over the time column
            fs = 1/((df['time'].iloc[-1]-df['time'].iloc[0])/(len(df)-1))
        except  KeyError as e:
            raise Exception('Input DataFrame must contain a column named "time"')
    
    normalised_df = pd.DataFrame(columns=df.columns)

    for column in df.columns:
        normalised_df[column] = np.zeros(101)

        currentData = df[column]
        currentData = currentData[~np.isnan(currentData)]
        
        if currentData.empty:
            currentData = np.zeros(len(df))
        
        timeTrial = np.arange(0, len(currentData)/fs, 1/fs)           
        Tnorm = np.arange(0, timeTrial[-1], timeTrial[-1]/101)
        
        if len(Tnorm) == 102:
            Tnorm = Tnorm[:-1]
        normalised_df[column] = np.interp(Tnorm, timeTrial, currentData)
    
    return normalised_df

def time_normalise_file(filepath=None, fs=None):
    
    if filepath is None:
        filepath = input("Please provide the path to the file to be time-normalised: ").strip('"')
    
    df = load_any_data_file(filepath)
    if fs is None:
        fs = 1/(df['time'][1]-df['time'][0])
    normalised_df = time_normalise_df(df, fs)
    # save normalised file
    normalised_filepath = filepath.replace('.sto', '_timeNormalised.sto')
    write_sto_file(normalised_df, normalised_filepath)

def get_unique_names(paths):
    # Split each path into parts
    split_paths = [p.split(os.sep) for p in paths]

    # Transpose to compare columns
    columns = list(zip(*split_paths))

    # Find the indices where not all elements are the same
    diff_indices = [i for i, col in enumerate(columns) if len(set(col)) > 1]

    # Create unique names using the differing parts
    unique_names = []
    for parts in split_paths:
        unique = "_".join([parts[i] for i in diff_indices])
        unique_names.append(unique)
    return unique_names

def create_color_and_style_dict(labels):
    """Creates a color and style dictionary based on unique labels.
    Args:
        labels (list): List of unique labels.
        Returns:
        tuple: Two dictionaries, one for colors and one for styles.
            
    Example:
        labels = ['Athlete_03_sq_70', 'Athlete_03_sq_75', 'Athlete_03_sq_80']
        color_dict, style_dict = create_color_and_style_dict(labels)
        
    """
    
    
    color_dict = {}
    style_dict = {}
    # Extract the number (e.g., 70, 75, 80, 85, 90) from each label for color assignment
    # Assume the number is always at the end after an underscore
    numbers = [label.split('_')[-1] for label in labels]
    unique_numbers = sorted(set(numbers), key=lambda x: int(x))
    color_map = matplotlib.colormaps['tab10']
    number_to_color = {num: color_map.colors[i % 10] for i, num in enumerate(unique_numbers)}
    for label, num in zip(labels, numbers):
        color_dict[label] = number_to_color[num]
        if 'mri' in label.lower():
            style_dict[label] = '--'
        else:
            style_dict[label] = '-'
    return color_dict, style_dict

def rsquared(y_true, y_pred):
    """Calculate the R-squared value between true and predicted values.
    
    Args:
        y_true (array-like): The true values.
        y_pred (array-like): The predicted values.
    """
    r = np.corrcoef(y_true, y_pred)[0, 1]
    return r ** 2

def rmse(y_true, y_pred):
    """Calculate the Root Mean Square Error (RMSE) between true and predicted values.
    
    Args:
        y_true (array-like): The true values.
        y_pred (array-like): The predicted values.
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))    

def compare_curves(dataFrame1, dataFrame2, mapping=None):
    """Calculate RMSE and R-squared the common columns between two dataFrames.
    
    mapping: dict
        A dictionary mapping column names from dataFrame1 to dataFrame2.
        
    """
    
    if mapping is None:
        common_columns = dataFrame1.columns.intersection(dataFrame2.columns)
        mapping = dict(common_columns.to_series())
    else:
        common_columns = list(mapping.keys())
        
    results = pd.DataFrame(columns=['RMSE', 'R2'], index=common_columns)
    for col in common_columns:
        mapped_col = mapping.get(col, col)
        y_true_col = dataFrame1[mapped_col].values
        y_pred_col = dataFrame2[col].values
        rmse_value = rmse(y_true_col, y_pred_col)
        r2_value = rsquared(y_true_col, y_pred_col)
        results.loc[col] = [rmse_value, r2_value]
    
    return results

# dir manipulation
def rename_all_files_in_dir(dir_path, old_str, new_str):
    """
    Renames all files in the specified directory by replacing old_str with new_str in their names.
    
    Args:
        dir_path (str): The path to the directory containing the files.
        old_str (str): The substring to be replaced in the file names.
        new_str (str): The substring to replace old_str with.
    """
    if not os.path.isdir(dir_path):
        raise ValueError(f"The provided path '{dir_path}' is not a valid directory.")
    
    for filename in os.listdir(dir_path):
        if old_str in filename:
            new_filename = filename.replace(old_str, new_str)
            try:
                os.rename(os.path.join(dir_path, filename), os.path.join(dir_path, new_filename))
                print(f"Renamed '{filename}' to '{new_filename}'")
            except Exception as e:
                print(f"Error renaming '{filename}': {e}")

class osimTools():
    """A collection of utility functions for OpenSim and data processing.
    
    functions with '_' the object to be created first because they refer to self
    Example:
        tools = osimTools()
        tools._printHello()
        
        osimTools.calculate_emg_linear_envelope(x)
        # katya
        # Utility functions.
        #
        # author: Dimitar Stanev <jimstanev@gmail.com>
        ##
    
    """
    
    def __init__(self, filepath=None):
        self.filepath = filepath

    def _printHello(self):
        print("Hello from osimTools!")

    def calculate_emg_linear_envelope(x, f_sampling=1000, f_band_low=30,
                                    f_band_high=300, f_env=6, to_normalize=True,
                                    plot=False):
        """Calculates the EMG linear envelope by applying the following
        transformations to the raw signal:

        1) Remove mean
        2) Band-pass 4th order Butterworth filter to remove low and high frequencies
        3) Full rectification (use of abs)
        4) Normalization based on max value (if to_normalize=True)
        5) Low-pass filter to calculate the envelope
        6) (optional) plot the raw and envelop signals (if plot=True); does not show plot just in the background

        """
        f_nyq = f_sampling / 2
        # 1) remove mean
        y = x - x.mean()
        # 2) band-pass
        b, a = signal.butter(4, [f_band_low / f_nyq, f_band_high / f_nyq], 'band')
        y = signal.filtfilt(b, a, y)
        # 3) rectify
        y = np.abs(y)
        # 4) normalize
        if to_normalize:
            y = y / y.max()

        # 5) low-pass
        b, a = signal.butter(2, f_env / f_nyq, 'low')
        env = signal.filtfilt(b, a, y)
        if plot:
            plt.figure()
            plt.plot(y, label='raw')
            plt.plot(env, label='envelop')
            plt.legend()
            
        return env


    def normalize_interpolate_dataframe(df, interp_column='time', method='linear'):
        """Normalizes time between [0, 1] and then re-samples data frame at
        constant interval.

        """
        # normalize between 0, 1
        time_old = df.time.to_numpy()
        time_new = (time_old - time_old[0]) / (time_old[-1] - time_old[0])
        df.loc[:, 'time'] = time_new
        # re-sample time with specific interval
        df = df.set_index(interp_column)
        at = np.arange(0, 1.01, 0.01)
        df = df.reindex(df.index | at)
        df = df.interpolate(method=method).loc[at]
        df = df.reset_index()
        df = df.rename(columns={'index': interp_column})
        return df

    def osim_vector_to_list(array):
        """Convert SimTK::Vector to Python list.
        """
        temp = []
        for i in range(array.size()):
            temp.append(array[i])

        return temp


    def vector_vec3_to_nparray(vector):
        temp = []
        for i in range(vector.size()):
            temp.append([vector[i][0], vector[i][1], vector[i][2]])

        return np.array(temp)


    def osim_array_to_list(array):
        """Convert OpenSim::Array<T> to Python list.
        """
        temp = []
        for i in range(array.getSize()):
            temp.append(array.get(i))

        return temp


    def list_to_osim_array_str(self, list_str):
        """Convert Python list of strings to OpenSim::Array<string>."""
        arr = osim.ArrayStr()
        for element in list_str:
            arr.append(element)

        return arr


    def np_array_to_simtk_matrix(array):
        """Convert numpy array to SimTK::Matrix"""
        n, m = array.shape
        M = osim.Matrix(n, m)
        for i in range(n):
            for j in range(m):
                M.set(i, j, array[i, j])

        return M


    def rotate_data_table(table, axis, deg):
        """Rotate OpenSim::TimeSeriesTableVec3 entries using an axis and angle.

        Parameters
        ----------
        table: OpenSim.common.TimeSeriesTableVec3

        axis: 3x1 vector

        deg: angle in degrees

        """
        R = osim.Rotation(np.deg2rad(deg),
                          osim.Vec3(axis[0], axis[1], axis[2]))
        for i in range(table.getNumRows()):
            vec = table.getRowAtIndex(i)
            vec_rotated = R.multiply(vec)
            table.setRowAtIndex(i, vec_rotated)


    def mm_to_m(table, label):
        """Scale from units in mm for units in m.

        Parameters
        ----------
        label: string containing the name of the column you want to convert

        """
        c = table.updDependentColumn(label)
        for i in range(c.size()):
            c[i] = osim.Vec3(c[i][0] * 0.001, c[i][1] * 0.001, c[i][2] * 0.001)


    def mirror_z(table, label):
        """Mirror the z-component of the vector.

        Parameters
        ----------
        label: string containing the name of the column you want to convert

        """
        c = table.updDependentColumn(label)
        for i in range(c.size()):
            c[i] = osim.Vec3(c[i][0], c[i][1], -c[i][2])


    def lowess_bell_shape_kern(x, y, tau=0.0005):
        """lowess_bell_shape_kern(x, y, tau = .005) -> y_est Locally weighted
        regression: fits a nonparametric regression curve to a scatterplot. The
        arrays x and y contain an equal number of elements; each pair (x[i], y[i])
        defines a data point in the scatterplot. The function returns the estimated
        (smooth) values of y.  The kernel function is the bell shaped function with
        parameter tau. Larger tau will result in a smoother curve.

        """
        n = len(x)
        y_est = np.zeros(n)

        # initializing all weights from the bell shape kernel function
        w = np.array([np.exp(- (x - x[i]) ** 2 / (2 * tau)) for i in range(n)])

        # looping through all x-points
        for i in range(n):
            weights = w[:, i]
            b = np.array([np.sum(weights * y), np.sum(weights * y * x)])
            A = np.array([[np.sum(weights), np.sum(weights * x)],
                        [np.sum(weights * x), np.sum(weights * x * x)]])
            theta = np.linalg.solve(A, b)
            y_est[i] = theta[0] + theta[1] * x[i]

        return y_est

    def _storage_to_dataframe(self, sto):
        print('Converting OpenSim Storage to pandas DataFrame')
        
        # for i in range(sto.getSize()):print(sto.getStateVector(i).getTime())
        for i in range(sto.getSize()):print(sto.getData(i))
        sto.printToFile()
        
        breakpoint()
        
    def _create_opensim_storage(self, time, data, column_names):
        """Creates a OpenSim::Storage.

        Parameters
        ----------
        time: SimTK::Vector

        data: SimTK::Matrix

        column_names: list of strings

        Returns
        -------
        sto: OpenSim::Storage

        """
        sto = osim.Storage()
        sto.setColumnLabels(osimTools().list_to_osim_array_str(['time'] + column_names))
        for i in range(data.nrow()):
            row = osim.ArrayDouble()
            for j in range(data.ncol()):
                value = data.getElt(i, j)
                if np.isnan(value):
                    value = 0
                row.append(value)
            sto.append(time[i], row)
        
        # self._storage_to_dataframe(sto)
        return sto


    def annotate_plot(ax, text):
        """Annotate a figure by adding a text.
        """
        at = AnchoredText(text, frameon=True, loc='upper left')
        at.patch.set_boxstyle('round, pad=0, rounding_size=0.2')
        ax.add_artist(at)


    def rmse_metric(s1, s2):
        """Root mean squared error between two time series.

        """
        # Signals are sampled with the same sampling frequency. Here time
        # series are first aligned.
        # if s1.index[0] < 0:
        #     s1.index = s1.index - s1.index[0]

        # if s2.index[0] < 0:
        #     s2.index = s2.index - s2.index[0]

        t1_0 = s1.index[0]
        t1_f = s1.index[-1]
        t2_0 = s2.index[0]
        t2_f = s2.index[-1]
        t_0 = np.round(np.max([t1_0, t2_0]), 3)
        t_f = np.round(np.min([t1_f, t2_f]), 3)
        x = s1[(s1.index >= t_0) & (s1.index <= t_f)].to_numpy()
        y = s2[(s2.index >= t_0) & (s2.index <= t_f)].to_numpy()
        return np.round(np.sqrt(np.mean((x - y) ** 2)), 3)


    def refine_ground_reaction_wrench(self,data_table, label_triplet, stance_threshold,
                                    tau, debug=True):
        """Clean and filter raw ground reaction forces at a single leg as specified by
        label triplet. This algorithm checks when the foot is in touch with the
        ground (stance phase). When the foot is not in touch then the original data
        contain noise with very small SNR. Therefore, the data is either set to zero
        or to nan. Then, the data is interpolated in case of nan. Finally, the
        signals are low pass filtered using lowess_bell_shape_kern.

        Parameters
        ----------

        data_table: OpenSim::DataTable<Vec3> containing [force, point, moment] for
        each leg

        label_triplet: column identifiers for the wrench triplet (e.g., ['f1', 'p1', 'm1'])

        stance_threshold: values to consider the foot in touch with the ground

        tau: kernel standard divination (filtering)

        debug: Boolean to visualize filtering result

        Returns
        -------

        This function mutates the original data_table

        """
        # get data of single leg
        t = np.array(data_table.getIndependentColumn())
        f = data_table.updDependentColumn(label_triplet[0])
        p = data_table.updDependentColumn(label_triplet[1])
        m = data_table.updDependentColumn(label_triplet[2])
        f_l = self.vector_vec3_to_nparray(f)
        p_l = self.vector_vec3_to_nparray(p)
        m_l = self.vector_vec3_to_nparray(m)

        # debugging
        if debug:
            plt.figure()
            f1 = plt.gca()
            f1.plot(t, f_l)
            plt.figure()
            f2 = plt.gca()
            f2.plot(t, p_l)
            plt.figure()
            f3 = plt.gca()
            f3.plot(t, m_l)

        # remove information when the foot is not touching the ground
        t0 = None
        tf = None
        for i in range(len(f_l)):
            # remove noise
            if f_l[i, 1] < stance_threshold:
                for j in range(3):
                    f_l[i, j] = 0
                    p_l[i, j] = np.nan
                    m_l[i, j] = 0

            # detect heel strike
            if t0 is None and f_l[i, 1] >= stance_threshold:
                t0 = t[i]

            # detect toe off
            if tf is None and t0 is not None and f_l[i, 1] <= stance_threshold:
                tf = t[i]

        # interpolate nan values for points and moments
        f_l = pd.DataFrame(f_l).interpolate(limit_direction="both", kind="cubic").to_numpy()
        p_l = pd.DataFrame(p_l).interpolate(limit_direction="both", kind="cubic").to_numpy()
        m_l = pd.DataFrame(m_l).interpolate(limit_direction="both", kind="cubic").to_numpy()

        # filter data
        for j in range(3):
            # f_l[:, j] = signal.medfilt(f_l[:, j], median)
            f_l[:, j] = self.lowess_bell_shape_kern(t, f_l[:, j], tau)
            p_l[:, j] = self.lowess_bell_shape_kern(t, p_l[:, j], tau)
            m_l[:, j] = self.lowess_bell_shape_kern(t, m_l[:, j], tau)

        # debugging
        if debug:
            f1.plot(t, f_l)
            f2.plot(t, p_l)
            f3.plot(t, m_l)

        # update columns in the original data
        for i in range(f_l.shape[0]):
            f[i] = osim.Vec3(f_l[i, 0], f_l[i, 1], f_l[i, 2])
            p[i] = osim.Vec3(p_l[i, 0], p_l[i, 1], p_l[i, 2])
            m[i] = osim.Vec3(m_l[i, 0], m_l[i, 1], m_l[i, 2])

        return t0, tf, p_l.mean(axis=0)

    def read_from_storage(self, file_name, sampling_interval=0.01,
                        to_filter=False):
        """Read OpenSim.Storage files.

        Parameters
        ----------
        file_name: (string) path to file

        sampling_interval: resample the data with a given interval (0.01)

        to_filter: use low pass 4th order FIR filter with 6Hz cut off
        frequency

        Returns
        ------- 
        df: pandas data frame

        """
        sto = osim.Storage(file_name)
        sto.resampleLinear(sampling_interval)
        if to_filter:
            sto.lowpassFIR(4, 6)

        labels = self.osim_array_to_list(sto.getColumnLabels())
        time = osim.ArrayDouble()
        sto.getTimeColumn(time)
        time = self.osim_array_to_list(time)
        data = []
        for i in range(sto.getSize()):
            temp = self.osim_array_to_list(sto.getStateVector(i).getData())
            temp.insert(0, time[i])
            data.append(temp)

        df = pd.DataFrame(data, columns=labels)
        df.index = df.time
        return df


    def index_containing_substring(list_str, pattern):
        """For a given list of strings finds the index of the element that
        contains the substring.

        Parameters
        ----------
        list_str: list of str

        pattern: str
            pattern


        Returns
        -------
        indices: list of int
            the indices where the pattern matches

        """
        return [i for i, item in enumerate(list_str)
                if re.search(pattern, item)]


    def _plot_sto_file(self, file_name, plot_file, plots_per_row=4, pattern=None,
                    title_function=lambda x: x):
        """Plots the .sto file (OpenSim) by constructing a grid of subplots.

        Parameters
        ----------
        sto_file: str
            path to file
        plot_file: str
            path to store result
        plots_per_row: int
            subplot columns
        pattern: str, optional, default=None
            plot based on pattern (e.g. only pelvis coordinates)
        title_function: lambda
            callable function f(str) -> str
        """
        df = osimTools().read_from_storage(file_name)
        labels = df.columns.to_list()
        data = df.to_numpy()

        if pattern is not None:
            indices = self.index_containing_substring(labels, pattern)
        else:
            indices = range(1, len(labels))

        n = len(indices)
        ncols = int(plots_per_row)
        nrows = int(np.ceil(float(n) / plots_per_row))
        pages = int(np.ceil(float(nrows) / ncols))
        if ncols > n:
            ncols = n

        with PdfPages(plot_file) as pdf:
            for page in range(0, pages):
                fig, ax = plt.subplots(nrows=ncols, ncols=ncols,
                                    figsize=(8, 8))
                ax = ax.flatten()
                for pl, col in enumerate(indices[page * ncols ** 2:page *
                                                ncols ** 2 + ncols ** 2]):
                    ax[pl].plot(data[:, 0], data[:, col])
                    ax[pl].set_title(title_function(labels[col]))

                fig.tight_layout()
                pdf.savefig(fig)
                plt.close()


    def adjust_model_mass(model_file, mass_change):
        """Given a required mass change adjust all body masses accordingly.

        """
        rra_model = osim.Model(model_file)
        rra_model.setName('model_adjusted')
        state = rra_model.initSystem()
        current_mass = rra_model.getTotalMass(state)
        new_mass = current_mass + mass_change
        mass_scale_factor = new_mass / current_mass
        for body in rra_model.updBodySet():
            body.setMass(mass_scale_factor * body.getMass())

        # save model with adjusted body masses
        rra_model.printToXML(model_file)


    def replace_thelen_muscles_with_millard(model_file, target_folder):
        """Replaces Thelen muscles with Millard muscles so that we can disable
        tendon compliance and perform MuscleAnalysis to compute normalized
        fiber length/velocity without spikes.

        """
        model = osim.Model(model_file)
        new_force_set = osim.ForceSet()
        force_set = model.getForceSet()
        for i in range(force_set.getSize()):
            force = force_set.get(i)
            muscle = osim.Muscle.safeDownCast(force)
            millard_muscle = osim.Millard2012EquilibriumMuscle.safeDownCast(
                force)
            thelen_muscle = osim.Thelen2003Muscle.safeDownCast(force)
            if muscle is None:
                new_force_set.adoptAndAppend(force.clone())
            elif millard_muscle is not None:
                millard_muscle = millard_muscle.clone()
                millard_muscle.set_ignore_tendon_compliance(True)
                new_force_set.adoptAndAppend(millard_muscle)
            elif thelen_muscle is not None:
                millard_muscle = osim.Millard2012EquilibriumMuscle()
                # properties
                millard_muscle.set_default_activation(
                    thelen_muscle.getDefaultActivation())
                millard_muscle.set_activation_time_constant(
                    thelen_muscle.get_activation_time_constant())
                millard_muscle.set_deactivation_time_constant(
                    thelen_muscle.get_deactivation_time_constant())
                # millard_muscle.set_fiber_damping(0)
                # millard_muscle.set_tendon_strain_at_one_norm_force(
                #     thelen_muscle.get_FmaxTendonStrain())
                millard_muscle.setName(thelen_muscle.getName())
                millard_muscle.set_appliesForce(thelen_muscle.get_appliesForce())
                millard_muscle.setMinControl(thelen_muscle.getMinControl())
                millard_muscle.setMaxControl(thelen_muscle.getMaxControl())
                millard_muscle.setMaxIsometricForce(
                    thelen_muscle.getMaxIsometricForce())
                millard_muscle.setOptimalFiberLength(
                    thelen_muscle.getOptimalFiberLength())
                millard_muscle.setTendonSlackLength(
                    thelen_muscle.getTendonSlackLength())
                millard_muscle.setPennationAngleAtOptimalFiberLength(
                    thelen_muscle.getPennationAngleAtOptimalFiberLength())
                millard_muscle.setMaxContractionVelocity(
                    thelen_muscle.getMaxContractionVelocity())
                # millard_muscle.set_ignore_tendon_compliance(
                #     thelen_muscle.get_ignore_tendon_compliance())
                millard_muscle.set_ignore_tendon_compliance(True)
                millard_muscle.set_ignore_activation_dynamics(
                    thelen_muscle.get_ignore_activation_dynamics())
                # muscle path
                pathPointSet = thelen_muscle.getGeometryPath().getPathPointSet()
                geomPath = millard_muscle.updGeometryPath()
                for j in range(pathPointSet.getSize()):
                    pathPoint = pathPointSet.get(j).clone()
                    geomPath.updPathPointSet().adoptAndAppend(pathPoint)

                # append
                new_force_set.adoptAndAppend(millard_muscle)
            else:
                raise RuntimeError(
                    'cannot handle the type of muscle: ' + force.getName())

        new_force_set.printToXML(os.path.join(target_folder, 'muscle_set.xml'))


    def subject_specific_isometric_force(generic_model_file, subject_model_file,
                                        height_generic, height_subject):
        """Adjust the max isometric force of the subject-specific model based on results
        from Handsfield et al. 2014 [1] (equation from Fig. 5A). Function adapted
        from Rajagopal et al. 2015 [2].

        Given the height and mass of the generic and subject models, we can
        calculate the total muscle volume [1]:

        V_total = 47.05 * mass * height + 1289.6

        Since we can calculate the muscle volume and the optimal fiber length of the
        generic and subject model, respectively, we can calculate the force scale
        factor to scale the maximum isometric force of each muscle:

        scale_factor = (V_total_subject / V_total_generic) / (l0_subject / l0_generic)

        F_max_i = scale_factor * F_max_i

        [1] http://dx.doi.org/10.1016/j.jbiomech.2013.12.002
        [2] http://dx.doi.org/10.1109/TBME.2016.2586891

        """
        model_generic = osim.Model(generic_model_file)
        state_generic = model_generic.initSystem()
        mass_generic = model_generic.getTotalMass(state_generic)

        model_subject = osim.Model(subject_model_file)
        state_subject = model_subject.initSystem()
        mass_subject = model_subject.getTotalMass(state_subject)

        # formula for total muscle volume
        V_total_generic = 47.05 * mass_generic * height_generic + 1289.6
        V_total_subject = 47.05 * mass_subject * height_subject + 1289.6

        for i in range(0, model_subject.getMuscles().getSize()):
            muscle_generic = model_generic.updMuscles().get(i)
            muscle_subject = model_subject.updMuscles().get(i)

            l0_generic = muscle_generic.getOptimalFiberLength()
            l0_subject = muscle_subject.getOptimalFiberLength()

            force_scale_factor = (V_total_subject / V_total_generic) / (l0_subject /
                                                                        l0_generic)
            muscle_subject.setMaxIsometricForce(force_scale_factor *
                                                muscle_subject.getMaxIsometricForce())

        model_subject.printToXML(subject_model_file)

    def hide_muscles(self, model_file_path, hide = True):
        
        """Hide or show all muscles in the OpenSim model file.

        Parameters
        ----------
        model_file_path: str
            path to the OpenSim model file (.osim)
        hide: bool
            True to hide muscles, False to show muscles

        """
        model = osim.Model(model_file_path)
        for i in range(model.getMuscles().getSize()):
            muscle = model.updMuscles().get(i)
            breakpoint()

        model.printToXML(model_file_path)    
    ####
    
# CEINMS
def read_excitation_generator(file):
    """Reads a CEINMS excitation generator file and returns a dictionary
    containing the osim_muscles that match with each EMG signal

    """
    tree = ET.parse(file)
    root = tree.getroot()

    # look for '\excitationGenerator\mapping'
    excitations = root.findall('.//excitation')
    emg_to_muscles = dict()
    for excitation in excitations:
        muscle = excitation.get('id')
        try:
            emg_name = excitation.find('.//input').text
        except:
            emg_name = None
        emg_to_muscles[muscle] = emg_name

    return emg_to_muscles

# ObjectOrientation
class Plotter():
    def __init__(self):
        self.dataList = []
    
    def addDataFrame(self, dataframe):
        self.dataList.append(dataframe)

    def plotListDataFrames(self, xColumn, yColumns, labels):
        # Example plotting function
        for df, label in zip(self.dataList, labels):
            plt.plot(df[xColumn], df[yColumns], label=label)

        plt.legend()
        plt.show()

    def summaryTrials(self, trialList, xColumn, yColumns, labels):
        
        print("Creating summary plot...")
        print('Script not finished yet - work in progress')
        
        return
        
        # Example summary function
        for trial, label in zip(trialList, labels):
            mean_y = trial[yColumns].mean()
            plt.bar(label, mean_y)

        plt.show()



if __name__ == "__main__":
    
    LocalFuncs = [f for f in dir() if callable(globals()[f])]
    print("Available commands:", LocalFuncs)

    # Command loop
    while True:
        command = input("Enter command: ")

        if not command in LocalFuncs:
            print("Invalid command. Please try again.")
            continue

        try:
            globals()[command]()
        except Exception as e:
            print(f"Error executing {command}: {e}")
        
# END