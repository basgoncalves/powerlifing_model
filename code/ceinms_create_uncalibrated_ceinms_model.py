import os 
import xml.etree.ElementTree as ET
import opensim as osim
import paths
import utils

def create_subject_uncalibrated(save_path=None, osimModelFile=None, leg='r'):
    if osimModelFile == None:
        print("\033[93mNo OpenSim model not file provided. FAILED!!\033[0m")
        return None
    else:
        try:
            model = osim.Model(osimModelFile)
            coordinate_set = model.getCoordinateSet()
            muscles = model.getMuscles() # ForceSet
        except Exception as e:
            print(f"Error loading OpenSim model: {e}")
            return None
    
    osim_model_file_name = os.path.basename(osimModelFile) 
    root = ET.Element("subject", attrib={"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance"})
    
    mtu_default = ET.SubElement(root, "mtuDefault")
    ET.SubElement(mtu_default, "emDelay").text = "0.015"
    ET.SubElement(mtu_default, "percentageChange").text = "0.15"
    ET.SubElement(mtu_default, "damping").text = "0.1"
    
    curves = [
        {
            "name": "activeForceLength",
            "xPoints": "-5 0 0.401 0.402 0.4035 0.52725 0.62875 0.71875 0.86125 1.045 1.2175 1.4387 1.6187 1.62 1.621 2.2 5",
            "yPoints": "0 0 0 0 0 0.22667 0.63667 0.85667 0.95 0.99333 0.77 0.24667 0 0 0 0 0"
        },
        {
            "name": "passiveForceLength",
            "xPoints": "-5 0.998 0.999 1 1.1 1.2 1.3 1.4 1.5 1.6 1.601 1.602 5",
            "yPoints": "0 0 0 0 0.035 0.12 0.26 0.55 1.17 2 2 2 2"
        },
        {
            "name": "forceVelocity",
            "xPoints": "-10 -1 -0.6 -0.3 -0.1 0 0.1 0.3 0.6 0.8 10",
            "yPoints": "0 0 0.08 0.2 0.55 1 1.4 1.6 1.7 1.75 1.75"
        },
        {
            "name": "tendonForceStrain",
            "xPoints": "0 0.001 0.002 0.003 0.004 0.005 0.006 0.007 0.008 0.009 0.01 0.011 0.012 0.013 0.014 0.015 0.016 0.017 0.018 0.019 0.02 0.021 0.022 0.023 0.024 0.025 0.026 0.027 0.028 0.029 0.03 0.031 0.032 0.033 0.034 0.035 0.036 0.037 0.038 0.039 0.04 0.041 0.042 0.043 0.044 0.045 0.046 0.047 0.048 0.049 0.05 0.051 0.052 0.053 0.054 0.055 0.056 0.057 0.058 0.059 0.06 0.061 0.062 0.063 0.064 0.065 0.066 0.067 0.068 0.069 0.07 0.071 0.072 0.073 0.074 0.075 0.076 0.077 0.078 0.079 0.08 0.081 0.082 0.083 0.084 0.085 0.086 0.087 0.088 0.089 0.09 0.091 0.092 0.093 0.094 0.095 0.096 0.097 0.098 0.099 0.1",
            "yPoints": "0 0.0012652 0.0073169 0.016319 0.026613 0.037604 0.049078 0.060973 0.073315 0.086183 0.099678 0.11386 0.12864 0.14386 0.15928 0.17477 0.19041 0.20658 0.22365 0.24179 0.26094 0.28089 0.30148 0.32254 0.34399 0.36576 0.38783 0.41019 0.43287 0.45591 0.4794 0.50344 0.52818 0.55376 0.58022 0.60747 0.63525 0.66327 0.69133 0.71939 0.74745 0.77551 0.80357 0.83163 0.85969 0.88776 0.91582 0.94388 0.97194 1 1.0281 1.0561 1.0842 1.1122 1.1403 1.1684 1.1964 1.2245 1.2526 1.2806 1.3087 1.3367 1.3648 1.3929 1.4209 1.449 1.477 1.5051 1.5332 1.5612 1.5893 1.6173 1.6454 1.6735 1.7015 1.7296 1.7577 1.7857 1.8138 1.8418 1.8699 1.898 1.926 1.9541 1.9821 2.0102 2.0383 2.0663 2.0944 2.1224 2.1505 2.1786 2.2066 2.2347 2.2628 2.2908 2.3189 2.3469 2.375 2.4031 2.4311"
        }
    ]
    
    for curve in curves:
        curve_element = ET.SubElement(mtu_default, "curve")
        ET.SubElement(curve_element, "name").text = curve["name"]
        ET.SubElement(curve_element, "xPoints").text = curve["xPoints"]
        ET.SubElement(curve_element, "yPoints").text = curve["yPoints"]
    
    mtu_set = ET.SubElement(root, "mtuSet")
    try:
        mtus = []
        for muscle in muscles:
            mtu = {
                "name": muscle.getName(),
                "c1": "-0.5",
                "c2": "-0.5",
                "shapeFactor": "0.1",
                "optimalFibreLength": str(muscle.getOptimalFiberLength()),
                "pennationAngle": str(muscle.getPennationAngleAtOptimalFiberLength()),
                "tendonSlackLength": str(muscle.getTendonSlackLength()),
                "maxIsometricForce": str(muscle.getMaxIsometricForce()),
                "strengthCoefficient": "1"
            }
            mtus.append(mtu)
    except Exception as e:
        print(f"Error adding OpenSim muscles: {e}")
        return None
                    
    for mtu in mtus:
        mtu_element = ET.SubElement(mtu_set, "mtu")
        ET.SubElement(mtu_element, "name").text = mtu["name"]
        ET.SubElement(mtu_element, "c1").text = mtu["c1"]
        ET.SubElement(mtu_element, "c2").text = mtu["c2"]
        ET.SubElement(mtu_element, "shapeFactor").text = mtu["shapeFactor"]
        ET.SubElement(mtu_element, "optimalFibreLength").text = mtu["optimalFibreLength"]
        ET.SubElement(mtu_element, "pennationAngle").text = mtu["pennationAngle"]
        ET.SubElement(mtu_element, "tendonSlackLength").text = mtu["tendonSlackLength"]
        ET.SubElement(mtu_element, "maxIsometricForce").text = mtu["maxIsometricForce"]
        ET.SubElement(mtu_element, "strengthCoefficient").text = mtu["strengthCoefficient"]
    
    dof_set = ET.SubElement(root, "dofSet")

    dofs = [
                {"name": f"hip_adduction_{leg}", 
                    "mtuNameSet": f"add_brev_{leg} add_long_{leg} add_mag1_{leg} add_mag2_{leg} add_mag3_{leg} bifemlh_{leg} grac_{leg} pect_{leg} semimem_{leg} semiten_{leg} glut_max1_{leg} glut_med1_{leg} glut_med2_{leg} glut_med3_{leg} glut_min1_{leg} glut_min2_{leg} glut_min3_{leg} peri_{leg} sar_{leg} tfl_{leg}"},
                {"name": f"hip_rotation_{leg}", 
                    "mtuNameSet": f"glut_med1_{leg} glut_min1_{leg} iliacus_{leg} psoas_{leg} tfl_{leg} gem_{leg} glut_med3_{leg} glut_min3_{leg} peri_{leg} quad_fem_{leg}"},
                {"name": f"hip_flexion_{leg}", 
                    "mtuNameSet": f"add_brev_{leg} add_long_{leg} add_mag1_{leg} add_mag2_{leg} add_mag3_{leg} bifemlh_{leg} glut_max1_{leg} glut_max2_{leg} glut_max3_{leg} glut_med1_{leg} glut_med3_{leg} glut_min1_{leg} glut_min3_{leg} grac_{leg} iliacus_{leg} pect_{leg} psoas_{leg} rect_fem_{leg} sar_{leg} semimem_{leg} semiten_{leg} tfl_{leg} "},
                {"name": f"knee_angle_{leg}", 
                    "mtuNameSet": f"bifemlh_{leg} bifemsh_{leg} grac_{leg} lat_gas_{leg} med_gas_{leg} sar_{leg} semimem_{leg} semiten_{leg} rect_fem_{leg} vas_int_{leg} vas_lat_{leg} vas_med_{leg}"},
                {"name": f"ankle_angle_{leg}", 
                    "mtuNameSet": f"ext_dig_{leg} ext_hal_{leg} per_tert_{leg} tib_ant_{leg} flex_dig_{leg} flex_hal_{leg} lat_gas_{leg} med_gas_{leg} per_brev_{leg} per_long_{leg} soleus_{leg} tib_post_{leg}"}
            ]

    for dof in dofs:
        dof_element = ET.SubElement(dof_set, "dof")
        ET.SubElement(dof_element, "name").text = dof["name"]
        ET.SubElement(dof_element, "mtuNameSet").text = dof["mtuNameSet"]
    
    
    calibration_info = ET.SubElement(root, "calibrationInfo")
    uncalibrated = ET.SubElement(calibration_info, "uncalibrated")
    ET.SubElement(uncalibrated, "subjectID").text = osim_model_file_name
    ET.SubElement(uncalibrated, "additionalInfo").text = "TendonSlackLength and OptimalFibreLength scaled with Winby-Modenese"
    
    ET.SubElement(root, "opensimModelFile").text = osim_model_file_name
    
    tree = ET.ElementTree(root)
    if save_path is not None:
        utils.save_pretty_xml(tree, save_path)
        print(f"XML file created at: {save_path}")
    
    return tree

if __name__ == "__main__":

    save_path = paths.UNCALIBRATED_MODEL_PATH
    osim_model_file = paths.USED_MODEL
    leg = 'r'  # or 'l' for left leg
    
    tree = create_subject_uncalibrated(save_path=save_path, osimModelFile=osim_model_file, leg=leg)
    
    if tree is not None:
        print("Uncalibrated CEINMS model XML created successfully.")
    else:
        print("Failed to create uncalibrated CEINMS model XML.")