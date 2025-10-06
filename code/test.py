import os
import time
from matplotlib import pyplot as plt
import numpy as np
import opensim as osim

import pandas as pd

try:
    import utils
    import paths
except ImportError:
    from . import utils
    from . import paths


    muscle_name = muscle.getName()
    coordinates = coordinates_per_muscle(osimModel, muscle_name)
    print(f"Coordinates for muscle {muscle_name}: {coordinates}")

    moment_arms = checkMuscleMomentArms(osim_modelPath=osimModel,
                                        ik_output=trial.outputFiles['IK'].abspath(),
                                        leg='l',
                                        threshold=0.005)
    save_path = os.path.join(trial.path,'moment_arms' ,f"{muscle_name}.sto")
    utils.write_sto_file(moment_arms, save_path)
    print(f"Moment arms for muscle {muscle_name} saved to {save_path}")