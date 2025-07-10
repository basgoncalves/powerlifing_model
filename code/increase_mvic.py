import os
import opensim as osim
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Open window to select an OpenSim model file
def select_osim_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select OpenSim Model File",
        filetypes=[("OpenSim Model Files", "*.osim")]
    )
    root.destroy()
    return file_path

# User selects a factor to increase the max isometric force of muscles
def get_factor():
    root = tk.Tk()
    root.withdraw()
    factor = simpledialog.askfloat(
        "Increase Factor",
        "Enter factor to multiply max isometric force (e.g., 1.2):",
        minvalue=0.0
    )
    root.destroy()
    return factor

def main():
    root = tk.Tk() # prevent the main window from appearing
    root.withdraw()
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # change directory to the script's directory
    
    osim_file = select_osim_file()
    if not osim_file:
        messagebox.showinfo("Cancelled", "No file selected.")
        return

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

    new_file = osim_file.replace('.osim', f'_increased_{factor:.2f}.osim')
    model.printToXML(new_file)
    messagebox.showinfo("Done", f"Saved new model to:\n{new_file}")

if __name__ == "__main__":
    main()