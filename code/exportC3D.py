import os
import time
import opensim as osim
import paths
import utils

def main(c3dfilepath=None):
    
    c3dData = osim.C3DFileAdapter().read(c3dfilepath)
    breakpoint()  # This will pause the execution for debugging
    

         
if __name__ == '__main__':
    
    c3dfilepath = askopenfilename(
        title="Select C3D file",
    
    main(c3dfilepath=trial.inputFiles['C3D'].abspath())
    
    