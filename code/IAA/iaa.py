import os
import sys
print(sys.executable)
import opensim as osim

current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)


def run_from_setup():
    setup_file_path = input("Enter the path to the IAA setup file (.xml): ").strip('"')
    analise3 = osim.AnalyzeTool(setup_file_path)

    iaa = analise3.getAnalysisSet().get(0)
    CS = iaa.updPropertyByName('ConstraintSet')
    CSo = CS.updValueAsObject()
    CS_obj = CSo.updPropertyByIndex(1) # <objects>
    constraintR = CS_obj.updValueAsObject(0) #<RollingOnSurface ... >
    constraintL = CS_obj.updValueAsObject(1) #<RollingOnSurface ... >
    propriedade = constraintR.updPropertyByName('socket_rolling_body')
    osim.PropertyHelper.setValueString('/bodyset/calcn_r', propriedade)
    propriedade = constraintR.updPropertyByName('socket_surface_body')
    osim.PropertyHelper.setValueString('/ground', propriedade)

    propriedade = constraintL.updPropertyByName('socket_rolling_body')
    osim.PropertyHelper.setValueString('/bodyset/calcn_l', propriedade)
    propriedade = constraintL.updPropertyByName('socket_surface_body')
    osim.PropertyHelper.setValueString('/ground', propriedade)

    #analise3.verifyControlsStates() ## ok, i passes

    analise3.run() # fails

if __name__ == "__main__":
    run_from_setup()
