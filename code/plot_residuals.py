import pandas as pd
from tkinter import Tk, filedialog
import matplotlib.pyplot as plt
import os
import msk_modelling_python as msk

current_path = os.path.dirname(os.path.abspath(__file__))
athlete = 'Athlete_03'

force_path = r'D:\athlete_03\simulations\Athlete_03\dl_70\Output\SO\_StaticOptimization_force.sto'

forces = msk.bops.import_sto_data(force_path)
plt.figure(figsize=(10, 6))
for i in range(len(forces)):
    
    if forces[i].name == 'time':
        continue
    
    