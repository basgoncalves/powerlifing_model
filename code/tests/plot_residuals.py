import pandas as pd
from tkinter import Tk, filedialog
import matplotlib.pyplot as plt
import os
import msk_modelling_python as msk
import paths


force_path = paths.FORCES_OUTPUT

forces = msk.bops.import_sto_data(force_path)
plt.figure(figsize=(10, 6))
for i in range(len(forces)):
    
    if forces[i].name == 'time':
        continue
    
    