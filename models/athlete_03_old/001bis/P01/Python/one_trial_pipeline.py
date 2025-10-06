import opensim as osim
import os
import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt

from scipy.interpolate import CubicSpline

from interpDFrame import *
from simFunctions import *
from stan_utils import *
from plot_utils import *
from muscle_moment_arm import *

class RunAnalysesPipeline:
    def __init__(self, individual_tag, model_name, model_folder, input_dir, trc_file_name, 
                 grf_mot_file_name, step_data_file_name,  
                 tempalte_dir, actuator_file,
                 output_dir = None, first_foot_file_name = None):
        
        self.ing = individual_tag
        self.model_path = os.path.join(model_folder, model_name)
        self.input_dir  = input_dir
        self.trc_path = os.path.join(input_dir, trc_file_name)
        self.template_path = tempalte_dir
        self.grf_mot_path = os.path.join(input_dir, grf_mot_file_name)
        self.actuator_file = os.path.join(self.template_path, actuator_file)
        
        if first_foot_file_name:
            self.first_foot_file_path = os.path.join(input_dir, first_foot_file_name)
        else: self.first_foot_file_path = None

        if output_dir:
            self.output_path = output_dir
        else: self.output_path = input_dir        

        self.step_data_df = pd.read_csv(os.path.join(input_dir, step_data_file_name))
        self.obtain_step_times()
        self.obtain_recording_times()
        self.obtain_first_foot()
        self.setup_grf_xml()


    def obtain_step_times(self):
        self.first_heel_strike, self.last_toe_off = (list(self.step_data_df['t0'].dropna())[0]-0.05, list(self.step_data_df['tf'].dropna())[-1]+0.05)
    
    def obtain_recording_times(self):
        marker_data = osim.MarkerData(self.trc_path)
        self.recording_start, self.recording_stop = (marker_data.getStartFrameTime(), marker_data.getLastFrameTime())

    def obtain_first_foot(self):
        print('obtain_first_foot started')
        if self.first_foot_file_path:
            with open(self.first_foot_file_path) as f:
                lines = f.readlines()
            if len(lines) == 1:
                self.first_foot = lines[0].split()[0]
            if len(lines) > 1:
                self.first_foot = lines[0].strip()
        else:
            print('plate_touch_points started')
            plate_touch_points = self.step_data_df['p_l'].to_list()
            text_to_float = lambda text: [float(x) for x in text.split()]
            plate_touch_array = np.array([text_to_float(entry[1:-1]) for entry in plate_touch_points])
            z_coords = plate_touch_array[:,2]
            print(z_coords)
            left_foot = np.where(z_coords == min(z_coords))[0][0]
            print('left_foot', left_foot)
            if left_foot%2 == 0:
                self.first_foot = 'l'
            else: self.first_foot = 'r'
        if self.first_foot == 'r': self.second_foot = 'l'
        else: self.second_foot = 'r'
        print('first_foot', self.first_foot)
            
    def setup_grf_xml(self):
        # parse grf_mot file
        table_grf = osim.TimeSeriesTable(self.grf_mot_path)
        table_grf.getIndependentColumn()[-1]
        cols = table_grf.getColumnLabels()
        if len(cols)/9 == 3:
            self.number_of_force_plates = 3
        elif len(cols)/9 == 5:
            self.number_of_force_plates = 5
        else: print('number of force plates is neither 3 nor 5')

        # find contact plates
        count = 1
        list_of_non_zero_plates = []
        while count <= len(cols):
            temp = table_grf.getDependentColumnAtIndex(count).to_numpy()
            if max(temp) > 60:
                pl = cols[count].split('_')[0]
                list_of_non_zero_plates.append(pl)
            count += 9
        
        # create GRX xml file
        external_loads = osim.ExternalLoads()
        foot = self.first_foot
        for plate in list_of_non_zero_plates:
            f = osim.ExternalForce()
            f.setName(plate)
            f.set_applied_to_body(f'calcn_{foot}')
            f.set_force_expressed_in_body('ground')
            f.set_point_expressed_in_body('ground')
            f.set_force_identifier(f'{plate}_ground_force_v')
            f.set_point_identifier(f'{plate}_ground_force_p')
            f.set_torque_identifier(f'{plate}_ground_torque_')
            next_foot = 'r' if 'r' != foot else 'l'
            foot = next_foot
            external_loads.cloneAndAppend(f)
        external_loads.setDataFileName(self.grf_mot_path)
        external_loads.printToXML(os.path.join(self.output_path, "GRF_setup_local.xml"))

    def setup_ik_xml(self):
        output_motion_file = os.path.join(self.output_path, 'IK_results.mot')

        inverse_kinematics_tool = osim.InverseKinematicsTool(os.path.join(self.template_path, 'IK_setup.xml'))
        time_start = self.recording_start
        time_stop = self.recording_stop

        inverse_kinematics_tool.set_model_file(self.model_path)
        inverse_kinematics_tool.set_marker_file(self.trc_path)
        inverse_kinematics_tool.set_output_motion_file(output_motion_file)
        inverse_kinematics_tool.setStartTime(time_start)
        inverse_kinematics_tool.setEndTime(time_stop)
        inverse_kinematics_tool.set_results_directory(self.output_path)
        inverse_kinematics_tool.printToXML(os.path.join(self.output_path, 'IK_setup_local.xml'))
    
    def run_ik(self):
        self.setup_ik_xml()
        # Run IK
        cmdprog = 'opensim-cmd'
        cmdtool = 'run-tool'
        cmdfile = os.path.join(self.output_path, 'IK_setup_local.xml')
        cmdfull = [cmdprog, cmdtool, cmdfile]
        rc = runProgram(cmdfull)
        # plot
        plot_sto_file(os.path.join(self.output_path, 'IK_results.mot'),
                    os.path.join(self.output_path, 'IK_results.pdf'), 3)

    def setup_id_xml(self):
        kinematics_path = os.path.join(self.output_path, 'IK_results.mot')
        time_start = self.first_heel_strike
        time_stop = self.last_toe_off
        grf_setup = os.path.join(self.output_path, 'GRF_setup_local.xml')
        output_motion_file = os.path.join(self.output_path, 'ID_results.mot')

        id_tool = osim.InverseDynamicsTool(os.path.join(self.template_path, 'ID_setup.xml'))
        id_tool.setModelFileName(self.model_path)
        id_tool.setStartTime(time_start)
        id_tool.setEndTime(time_stop)
        id_tool.setCoordinatesFileName(kinematics_path)
        id_tool.set_results_directory(self.output_path)
        id_tool.setOutputGenForceFileName(output_motion_file)
        id_tool.setExternalLoadsFileName(grf_setup)
        id_tool.printToXML(os.path.join(self.output_path, 'ID_setup_local.xml'))

    def run_id(self):
        self.setup_id_xml()
        cmdprog = 'opensim-cmd'
        cmdtool = 'run-tool'
        cmdfile = os.path.join(self.output_path, 'ID_setup_local.xml')
        cmdfull = [cmdprog, cmdtool, cmdfile]
        rc = runProgram(cmdfull)
        # plot
        plot_sto_file(os.path.join(self.output_path, 'ID_results.mot'),
                    os.path.join(self.output_path, 'ID_results.pdf'), 3)
        

    def setup_so_xml(self):
        grf_setup = os.path.join(self.output_path, 'GRF_setup_local.xml')
        kinematic_file = os.path.join(self.output_path, 'IK_results.mot')
        actuatorfile = self.actuator_file
        time_start = self.first_heel_strike
        time_stop = self.last_toe_off
 
        # Define a StaticOptimization object.
        so = osim.StaticOptimization()
        so.setStartTime(time_start)
        so.setEndTime(time_stop)
        so.setInDegrees(True)
        so.setUseMusclePhysiology(True)
        so.setUseModelForceSet(True)
        so.setActivationExponent(2)
        so.setConvergenceCriterion(0.0001)
        so.setMaxIterations(100)

        # Create analyze tool for static optimization.
        so_analyze_tool = osim.AnalyzeTool()
        so_analyze_tool.setName("SO")

        # Set model file, motion files and external load file names.
        so_analyze_tool.setModelFilename(os.path.abspath(self.model_path))
        so_analyze_tool.setCoordinatesFileName(os.path.abspath(kinematic_file))
        so_analyze_tool.setExternalLoadsFileName(grf_setup)

        # Add analyses.
        so_analyze_tool.updAnalysisSet().cloneAndAppend(so)

        # Configure analyze tool.
        so_analyze_tool.setReplaceForceSet(False)
        so_analyze_tool.setStartTime(time_start)
        so_analyze_tool.setFinalTime(time_stop)
        so_analyze_tool.setLowpassCutoffFrequency(6)

        actuatorFilesArray = osim.ArrayStr()
        actuatorFilesArray.append(actuatorfile)
        so_analyze_tool.setForceSetFiles(actuatorFilesArray)

        # Directory where results are stored.
        so_analyze_tool.setResultsDir(os.path.join(self.output_path, "SO_Results"))

        # Print configuration of analyze tool to a xml file.
        so_analyze_tool.printToXML(os.path.join(self.output_path, "SO_Setup_local.xml"))

    def run_so(self):
        # create configuration
        self.setup_so_xml()
        # create log
        osim.Logger.removeFileSink()
        osim.Logger.addFileSink(os.path.join(self.output_path, "opensim-log.log"))

        # Load configuration 
        so_analyze_tool = osim.AnalyzeTool(os.path.join(self.output_path, "SO_Setup_local.xml"), True)
        # Run static optimization.
        so_analyze_tool.run()
        # plot so
        plot_sto_file(os.path.join(self.output_path, 'SO_Results\SO_StaticOptimization_activation.sto'),
              os.path.join(self.output_path, 'SO_Results\SO_StaticOptimization_activation.pdf'), 3)

    def setup_jr_xml(self):
        grf_setup = os.path.join(self.output_path, 'GRF_setup_local.xml')
        kinematic_file = os.path.join(self.output_path, 'IK_results.mot')
        actuatorfile = self.actuator_file
        time_start = self.first_heel_strike
        time_stop = self.last_toe_off
 
        # Define a JointReaction object.
        jr = osim.JointReaction()
        jr.setName('JointReaction')
        
        # Set start and end times for the analysis.
        jr.setStartTime(time_start)
        jr.setEndTime(time_stop)
        jr.setInDegrees(True)
        jr.setForcesFileName(os.path.join(self.output_path, 'SO_results', 'SO_StaticOptimization_force.sto'))
        
        express = osim.ArrayStr()
        express.append('child')
        jr.setInFrame(osim.ArrayStr(express))

        # Create analyze tool for static optimization.
        analyze_tool = osim.AnalyzeTool()
        analyze_tool.setName("JR")

        # Set model file, motion files and external load file names.
        analyze_tool.setModelFilename(os.path.abspath(self.model_path))
        analyze_tool.setCoordinatesFileName(os.path.abspath(kinematic_file))
        analyze_tool.setExternalLoadsFileName(grf_setup)

        # Add analyses.
        analyze_tool.updAnalysisSet().cloneAndAppend(jr)

        # Configure analyze tool.
        analyze_tool.setReplaceForceSet(False)
        analyze_tool.setStartTime(time_start)
        analyze_tool.setFinalTime(time_stop)
        analyze_tool.setLowpassCutoffFrequency(6)

        actuatorFilesArray = osim.ArrayStr()
        actuatorFilesArray.append(actuatorfile)
        analyze_tool.setForceSetFiles(actuatorFilesArray)

        # Directory where results are stored.
        analyze_tool.setResultsDir(os.path.join(self.output_path, "SO_Results"))

        # Print configuration of analyze tool to a xml file.
        analyze_tool.printToXML(os.path.join(self.output_path, "JR_Setup_local.xml"))

    def run_jr(self):
        # create configuration
        self.setup_jr_xml()
        # Load configuration 
        jr_analyze_tool = osim.AnalyzeTool(os.path.join(self.output_path, "JR_Setup_local.xml"), True)
        # Run static optimization.
        jr_analyze_tool.run()
        # plot
        plot_sto_file(os.path.join(self.output_path, 'SO_Results\JR_JointReaction_ReactionLoads.sto'),
                    os.path.join(self.output_path, 'SO_Results\JR_JointReaction_ReactionLoads.pdf'), 3)

    def run_muscle_moment_arms(self):
        from muscle_moment_arm import MuscleMomentArms
        ma_output_dir = os.path.join(self.output_path, 'muscle_moment_arms')
        if not os.path.exists(ma_output_dir):
            print(ma_output_dir)
            os.makedirs(ma_output_dir)
        ma_calculator = MuscleMomentArms(self. output_path, 'IK_results.mot', self.model_path, ma_output_dir, self.first_heel_strike, self.last_toe_off)
        ma_calculator.compute_hip_muscle_moment_arms()
        ma_calculator.compute_knee_muscle_moment_arms()
        ma_calculator.compute_ankle_muscle_moment_arms()

    def basic(self):
        self.run_ik()
        self.run_id()
        self.run_muscle_moment_arms()
        

class OneTrialSteps:
    def __init__(self, path_to_ik, input_dir, steps_csv_file_name, first_foot_file_name=None):
        self.path_to_ik = path_to_ik
        self.path_to_steps = os.path.join(input_dir, steps_csv_file_name)
        self.table_ik = (osim.TableProcessor(path_to_ik)).process()
        self.x_time = self.table_ik.getIndependentColumn()
        self.step_data_df = pd.read_csv(self.path_to_steps, index_col=0)
        self.first_foot_file_path = os.path.join(input_dir, first_foot_file_name) if first_foot_file_name else None
        self.first_foot = None
        self.second_foot = None
        self.obtain_first_foot()

    def obtain_first_foot(self):
        if self.first_foot_file_path:
            with open(self.first_foot_file_path) as f:
                lines = f.readlines()
                self.first_foot = lines[0].strip().split()[0] if lines else None
        else:
            self._determine_first_foot_from_plate_touch_points()

        if self.first_foot:
            self.second_foot = 'l' if self.first_foot == 'r' else 'r'
        else:
            print("Error: Unable to determine the first foot.")
        print(f'first_foot: {self.first_foot}')

    def _determine_first_foot_from_plate_touch_points(self):
        print('plate_touch_points started')
        plate_touch_points = self.step_data_df['p_l'].to_list()
        plate_touch_array = np.array([self._text_to_float(entry[1:-1]) for entry in plate_touch_points])
        z_coords = plate_touch_array[:, 2]
        left_foot_index = np.argmin(z_coords)
        print(f'z_coords: {z_coords}, left_foot_index: {left_foot_index}')
        self.first_foot = 'l' if left_foot_index % 2 == 0 else 'r'

    @staticmethod
    def _text_to_float(text):
        return [float(x) for x in text.split()]

    def define_heel_strikes(self, foot):
        print('table', self.step_data_df.dropna())
        step_data_cleaned = self.step_data_df.dropna()

        heel_strike_times = []
        is_first_foot = (foot == self.first_foot)
        print(f'Heel strikes for {foot}')
  
        if step_data_cleaned.shape[0] < 2:
            print('Insufficient data to calculate step time.')
            self.one_step_time = None
        else:
            self.one_step_time = step_data_cleaned.iloc[1]['tf'] - step_data_cleaned.iloc[0]['tf']
        print('one step data',self.one_step_time)

        for i, index in enumerate(step_data_cleaned.index):
            if (i % 2 == 0 and is_first_foot) or (i % 2 == 1 and not is_first_foot):
                time = step_data_cleaned.at[index, 't0']
                heel_strike_times.append(time)

        if len(heel_strike_times) < step_data_cleaned.shape[0] / 2:
            last_time = self.locate_the_last_heel_strike(heel_strike_times)
            if last_time is not None:
                heel_strike_times.append(last_time)

        return heel_strike_times

    def locate_the_last_heel_strike(self, heel_strike_times):
        if not heel_strike_times or self.one_step_time is None:
            return None
        t0 = heel_strike_times[-1]
        t1 = t0 + 2*self.one_step_time
        pelvis_list = (self.table_ik.getDependentColumn('pelvis_list')).to_numpy()
        t0_index = self.table_ik.getNearestRowIndexForTime(t0)
        t1_index = self.table_ik.getNearestRowIndexForTime(t1)

        try:
            if abs(pelvis_list[t0_index] - pelvis_list[t1_index]) < abs(min(pelvis_list) - max(pelvis_list)) / 4:
                print('estimated second heel strike t1=', t1)
                return t1
        except IndexError:
            print('Kinematics index out of range or unexpected data.')
        return None

    def def_right_heel_strike(self):
        self.right_heel_strike_times = self.define_heel_strikes('r')
        return self.right_heel_strike_times

    def def_left_heel_strike(self):
        self.left_heel_strike_times = self.define_heel_strikes('l')
        return self.left_heel_strike_times

    def full_cycle(self):
        self.right_cycle = self._generate_cycles(self.right_heel_strike_times)
        self.left_cycle = self._generate_cycles(self.left_heel_strike_times)

    def _generate_cycles(self, strike_times):
        if (len(strike_times) < 2) or (strike_times[0]==0) or strike_times[1]>self.x_time[-1]:
            return []
        return [(strike_times[i], strike_times[i + 1]) for i in range(len(strike_times) - 1)][:2]


class ResampleAndAverageSteps:
    def __init__(self, path_to_time_series, right_time_tuples=None, left_time_tuples=None):
        self.path_to_time_series = path_to_time_series
        self.right_time_tuples = right_time_tuples
        self.left_time_tuples = left_time_tuples
        self.right_df = pd.DataFrame()
        self.left_df = pd.DataFrame()
        self.get_mean_steps_per_trial()

    @staticmethod
    def resample(y, target_points=100):
        x = np.linspace(0, 1, num=len(y))
        new_x = np.linspace(0, 1, num=target_points)
        spline = CubicSpline(x, y)
        return spline(new_x)

    def trim_and_resample(self, osim_datatable, time_tuple):
        start, end = time_tuple
        trimmed_table = osim_datatable.clone()
        trimmed_table.trim(start - 0.005, end + 0.005)
        data_matrix = self._extract_matrix_from_datatable(trimmed_table)
        return np.apply_along_axis(self.resample, axis=0, arr=data_matrix)

    @staticmethod
    def _extract_matrix_from_datatable(datatable):
        matrix = datatable.getMatrix()
        return np.array([[matrix.getElt(i, j) for j in range(matrix.ncol())] for i in range(matrix.nrow())])

    @staticmethod
    def create_storage_from_dataframe(df):
        time = list(df.index)
        column_names = list(df.columns)
        data = df.to_numpy()
        mx = np_array_to_simtk_matrix(data)
        return osim.TimeSeriesTable(time, mx, column_names)

    def get_mean_steps_per_trial(self):
        datatable = self._load_time_series()
        filtered_datatable = self._apply_lowpass_filter(datatable, cutoff_frequency=6)
        cols = filtered_datatable.getColumnLabels()

        if self.right_time_tuples:
            self.right_df = self._compute_mean_cycle(filtered_datatable, self.right_time_tuples, cols)
        if self.left_time_tuples:
            self.left_df = self._compute_mean_cycle(filtered_datatable, self.left_time_tuples, cols)

    def _load_time_series(self):
        if self.path_to_time_series.endswith('.csv'):
            pandas_df = pd.read_csv(self.path_to_time_series, index_col=0)
            return self.create_storage_from_dataframe(pandas_df)
        return osim.TimeSeriesTable(self.path_to_time_series)

    @staticmethod
    def _apply_lowpass_filter(datatable, cutoff_frequency):
        filter_util = osim.TableUtilities()
        filter_util.filterLowpass(datatable, cutoff_frequency)
        return datatable

    def _compute_mean_cycle(self, datatable, time_tuples, column_labels):
        aggregated_data = np.zeros((100, datatable.getNumColumns()))
        for time_tuple in time_tuples:
            resampled = self.trim_and_resample(datatable, time_tuple)
            aggregated_data += resampled
        averaged_data = aggregated_data / len(time_tuples)
        return pd.DataFrame(averaged_data, index=range(1, 101), columns=column_labels)

    def plot_steps_one_trial(self, ind_folder_name, output_path):
        n, column_names = self._get_plot_dimensions_and_columns()
        fig, axs = self._initialize_plot(n, ind_folder_name)
        self._plot_columns(axs, n, column_names)
        self._add_legend(fig)
        self._finalize_plot(fig, ind_folder_name, output_path)

    def _get_plot_dimensions_and_columns(self):
        if not self.right_df.empty:
            return self.right_df.shape[1], self.right_df.columns
        if not self.left_df.empty:
            return self.left_df.shape[1], self.left_df.columns
        return 0, []

    def _initialize_plot(self, n, ind_folder_name):
        cols = 4
        rows = (n + cols - 1) // cols
        fig, axs = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3), constrained_layout=True)
        fig.suptitle(f'{ind_folder_name} Normalized per Step', fontsize=18)
        return fig, axs

    def _plot_columns(self, axs, n, column_names):
        count = 0
        rows, cols = axs.shape if isinstance(axs, np.ndarray) else (1, len(axs))
        for count, name in enumerate(column_names):
            i, j = divmod(count, cols)
            if self.right_time_tuples:
                axs[i, j].plot(self.right_df.index, self.right_df[name], label=name, color='b')
            if self.left_time_tuples:
                axs[i, j].plot(self.left_df.index, self.left_df[name], label=name, color='r')
            axs[i, j].set_title(self._two_line_label(name))
            axs[i, j].set_axis_on()
        for remaining in range(count + 1, rows * cols):
            axs.flat[remaining].set_visible(False)

    @staticmethod
    def _two_line_label(x):
        tag = x.split('_')
        n = len(tag)
        if n <= 3:
            return ' '.join(tag)
        midpoint = n // 2
        first_half = ' '.join(tag[:midpoint])
        second_half = ' '.join(tag[midpoint:])  
        return f"{first_half}\n{second_half}"

    def _add_legend(self, fig):
        custom_lines = []
        if self.right_time_tuples:
            custom_lines.append(plt.Line2D([0], [0], color='b', lw=2, label='Right Heel Strike'))
        if self.left_time_tuples:
            custom_lines.append(plt.Line2D([0], [0], color='r', lw=2, label='Left Heel Strike'))
        fig.legend(handles=custom_lines, loc='lower right', prop={'size': 13}, borderaxespad=0.1, ncol=6)

    @staticmethod
    def _finalize_plot(fig, ind_folder_name, output_path):
        fig.get_layout_engine().set(h_pad=0.2)
        plt.savefig(os.path.join(output_path, f'{ind_folder_name}_one_step_plot.svg'), format='svg')


class ComputePersonalMeanAndSd:
    def __init__(self, list_of_folders, list_of_csv_files, input_path='.', path_extension='.', output_path="."):
        self.list_of_folders = list_of_folders
        self.list_of_csv_files = list_of_csv_files
        self.input_path = input_path
        self.path_extension = path_extension
        self.output_path = output_path
        self.table_names = [name[:-4] for name in self.list_of_csv_files]

    def plot_mean_sd_step(self, means_df, std_df, table_name, color):
        column_names = means_df.columns
        n = len(column_names)

        cols = 4
        rows = -(-n // cols)  # Ceiling division for rows

        fig, axs = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3), constrained_layout=True)
        fig.suptitle(f'{table_name} Normalized per Step', fontsize=18)
        axs = axs.flatten()

        for idx, name in enumerate(column_names):
            axs[idx].plot(means_df.index, means_df[name], label=name, color=color)
            axs[idx].fill_between(
                means_df.index,
                means_df[name] + std_df[name],
                means_df[name] - std_df[name],
                facecolor=color,
                alpha=0.5
            )
            axs[idx].set_title(two_line_label(name))

        # Hide any unused subplots
        for idx in range(len(column_names), len(axs)):
            axs[idx].set_visible(False)

        custom_lines = [
            plt.Line2D([0], [0], color=color, lw=2),
            plt.Line2D([0], [0], color=color, lw=18, alpha=0.5)
        ]
        fig.legend(custom_lines, ['Mean', 'Standard Deviation'], loc='lower right',
                   prop={'size': 13}, borderaxespad=0.1, ncol=6, labelspacing=0.)

        plt.savefig(os.path.join(self.output_path, f'{table_name}_one_step_plot.svg'), format='svg')

    def average_trials(self, plot=False):
        for i, name in enumerate(self.table_names):
            valid_arrays = []
            colnames, rownames = None, None

            for folder in self.list_of_folders:
                try:
                    file_path = os.path.join(self.input_path, folder, self.path_extension, self.list_of_csv_files[i])
                    imported = pd.read_csv(file_path)
                    imported_np = imported.to_numpy()

                    if not imported_np.any():
                        print(f'Folder {folder} has no valid {name} data')
                        continue

                    if colnames is None:
                        colnames, rownames = imported.columns, imported.index
                    valid_arrays.append(imported_np)

                except Exception as e:
                    print(f'Folder {folder} has no valid {name} data: {e}')

            if valid_arrays:
                arrays = np.array(valid_arrays)
                means = np.mean(arrays, axis=0)
                stds = np.std(arrays, axis=0)

                means_df = pd.DataFrame(means, columns=colnames, index=rownames)
                std_df = pd.DataFrame(stds, columns=colnames, index=rownames)

                means_df.to_csv(os.path.join(self.output_path, f'means_{name}.csv'))
                std_df.to_csv(os.path.join(self.output_path, f'std_{name}.csv'))

                if plot:
                    color = 'r' if 'left' in name else 'b'
                    self.plot_mean_sd_step(means_df, std_df, name, color)


def plot_step_right_left(path_to_data, right_means_file_name):
    # Determine file names
    name_parts = right_means_file_name.split('_')
    left_means_file_name = '_'.join(['left'] + name_parts[1:])
    right_std_file_name = '_'.join(['std'] + name_parts)
    left_std_file_name = '_'.join(['std', 'left'] + name_parts[1:])

    # Load data
    right_means_df = pd.read_csv(os.path.join(path_to_data, right_means_file_name), index_col=0)
    right_std_df = pd.read_csv(os.path.join(path_to_data, right_std_file_name), index_col=0)
    left_means_df = pd.read_csv(os.path.join(path_to_data, left_means_file_name), index_col=0)
    left_std_df = pd.read_csv(os.path.join(path_to_data, left_std_file_name), index_col=0)

    # Determine table name
    table_name = ' '.join(name_parts[2:]).split('.')[0]

    # Setup subplots
    column_names = [col for col in right_means_df.columns if 'Unnamed' not in col]
    n = len(column_names)
    cols = 4
    rows = -(-n // cols)  # Ceiling division

    fig, axs = plt.subplots(rows, cols, figsize=(cols * 3, rows * 3), constrained_layout=True)
    fig.suptitle(f'{table_name} Normalized per Step', fontsize=18)
    axs = axs.flatten()

    for idx, name in enumerate(column_names):
        axs[idx].plot(right_means_df.index, right_means_df[name], label=name, color='b')
        axs[idx].fill_between(
            right_means_df.index,
            right_means_df[name] + right_std_df[name],
            right_means_df[name] - right_std_df[name],
            facecolor='b',
            alpha=0.3
        )
        axs[idx].plot(left_means_df.index, left_means_df[name], label=name, color='r')
        axs[idx].fill_between(
            left_means_df.index,
            left_means_df[name] + left_std_df[name],
            left_means_df[name] - left_std_df[name],
            facecolor='r',
            alpha=0.3
        )
        axs[idx].set_title(two_line_label(name))

    # Hide unused subplots
    for idx in range(len(column_names), len(axs)):
        axs[idx].set_visible(False)

    # Add legend
    custom_lines = [
        plt.Line2D([0], [0], color='b', lw=2),
        plt.Line2D([0], [0], color='b', lw=18, alpha=0.3),
        plt.Line2D([0], [0], color='r', lw=2),
        plt.Line2D([0], [0], color='r', lw=18, alpha=0.3)
    ]
    fig.legend(custom_lines, ['Right Mean', 'Right Std Dev', 'Left Mean', 'Left Std Dev'], loc='lower right',
               prop={'size': 13}, borderaxespad=0.1, ncol=2)

    # Save the plot
    plt.savefig(os.path.join(path_to_data, f'{table_name}_one_step_r_l.svg'), format='svg')
