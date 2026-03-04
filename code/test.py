import utils
import os
import xml.etree.ElementTree as ET

import opensim as osim
import os
import openSim
import ceinms

def find_non_zero_mom_arm_muscles(osim_model_path) -> list:
        '''
        Find the muscles that have non-zero moment arms in the given OpenSim model.
        '''
        
        # Load the OpenSim model
        model = osim.Model(osim_model_path)
        model.initSystem()

        coordinates = model.getCoordinateSet()


if __name__ == "__main__":

        # Example usage
        muscle_names = ['quad_fem_r', 'obt_internus1_r', 'obt_internus2_r', 'obt_internus3_r', 'obt_externus1_r', 'obt_externus2_r', 'obt_externus3_r', 'gemelli_sup_r', 'gemelli_inf_r', 'pect_r', 'quad_fem_l', 'obt_internus1_l', 'obt_internus2_l', 'obt_internus3_l', 'obt_externus1_l', 'obt_externus2_l', 'obt_externus3_l', 'gemelli_sup_l', 'gemelli_inf_l', 'pect_l']

        source_model_path = r"C:\Git\powerlifing_model_clean\models\Catelli-V4.0_PowerliftingMarkers.osim"

        source_model_path = r"C:\Git\powerlifing_model_clean\models\Catelli_high_hip_Flexion_V4.0\Catelli-V4.0_PowerliftingMarkers.osim"
        target_model_path = r"C:\Git\powerlifing_model_clean\models\Lernagopal\Lernagopal_41_OUF_PowerlifitingMarkers.osim"

        # add_bodies_and_joints(source_model_path, target_model_path, skip_existing=True)
        # open_gui_osim()
        # load_models_osim_gui([source_model_path, target_model_path])

        # openSim.add_wrapping_surfaces(reference_model_path=source_model_path,
        #                                 target_model_path=target_model_path, output_model_path=target_model_path.replace('.osim', '_with_wrapping_surfaces.osim'))

        # openSim.increase_isometric_force(osim_modelPath=target_model_path, factor=3.00)


        calibration_trials = ['Walking_02']

        subject  = 'Athlete_03_Lernagopal_optimised' # Athlete_03_Lernagopal Athlete_03_MRI_Katya Athlete_03_Lernagopal_optimised Athlete_03_GPK Athlete_03_Uhlrich
        session = '25_03_31'
        trialList = ['Squat_BW_01', 'Walking_03', 'Squat_35kg_02'] #'Squat_BW_01' Squat_35kg_01 Walking_02
    
        analysis = utils.Analyse(trialPath=os.path.join(utils.SIMULATIONS_DIR, subject, session, trialList[0]))

        ana