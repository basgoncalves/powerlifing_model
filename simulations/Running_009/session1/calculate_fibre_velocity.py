import os 
import msk_modelling_python as msk
import numpy as np
import tkinter as tk

msk.plot.get_screen_size()

root = tk.Tk()
screen_width = root.winfo_vrootwidth() / root.winfo_fpixels('1i')
screen_height = root.winfo_vrootheight() / root.winfo_fpixels('1i')
root.destroy()
print(f"Screen size: {screen_width}x{screen_height}")

path = r"C:\Users\Bas\ucloud\ceinms_troubleshoot\ceinms-nn\runA1\muscleAnalysis\_MuscleAnalysis_FiberLength.sto"
fig, axs = msk.bops.plot_line_df(path)
msk.bops.plt.tight_layout()
fig.subplots_adjust(hspace=1, wspace=0.5)
fig.set_size_inches(screen_height, screen_height, forward=True)
msk.bops.plt.show()
exit()
length = msk.bops.import_sto_data(r"C:\Users\Bas\ucloud\ceinms_troubleshoot\ceinms-nn\runA1\muscleAnalysis\_MuscleAnalysis_Length.sto")
fiber_length = msk.bops.import_sto_data(r"C:\Users\Bas\ucloud\ceinms_troubleshoot\ceinms-nn\runA1\muscleAnalysis\_MuscleAnalysis_FiberLength.sto")
fiber_velocity = msk.bops.import_sto_data(r"C:\Users\Bas\ucloud\ceinms_troubleshoot\ceinms-nn\runA1\muscleAnalysis\_MuscleAnalysis_FiberVelocity.sto")

# Assuming the columns are named appropriately in the imported data
fiber_force = msk.bops.import_sto_data(r"C:\Users\Bas\ucloud\ceinms_troubleshoot\ceinms-nn\runA1\muscleAnalysis\_MuscleAnalysis_FiberForce.sto")

# Extract numpy arrays for calculations
fiber_length_arr = fiber_length['value'].to_numpy()
fiber_velocity_arr = fiber_velocity['value'].to_numpy()
fiber_force_arr = fiber_force['value'].to_numpy()

# Find indices where fiber velocity is positive or negative
positive_index = np.where(fiber_velocity_arr > 0)[0]
negative_index = np.where(fiber_velocity_arr < 0)[0]

# Calculate work using trapezoidal integration
positive_work = np.trapz(fiber_force_arr[positive_index], fiber_length_arr[positive_index])
negative_work = np.trapz(fiber_force_arr[negative_index], fiber_length_arr[negative_index])

print(f"Positive work: {positive_work}")
print(f"Negative work: {negative_work}")
