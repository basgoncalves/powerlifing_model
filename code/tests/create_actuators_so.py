"""
Script to create actuators_so.xml file for Static Optimization from an OpenSim model.

This script generates reserve actuators and residual actuators (point and torque actuators 
on the pelvis) based on the coordinates in an OpenSim model.
"""

import opensim as osim
import argparse
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np


class ActuatorForceEditor:
    """GUI for editing optimal forces for actuators"""
    
    def __init__(self, coordinates_list, default_force=800, calculated_forces=None):
        """
        Parameters
        ----------
        coordinates_list : list of dict
            List of coordinate dictionaries with 'name' and 'type' keys
        default_force : float
            Default optimal force value
        calculated_forces : dict, optional
            Pre-calculated forces from inverse dynamics
        """
        self.coordinates = coordinates_list
        self.default_force = default_force
        self.calculated_forces = calculated_forces or {}
        self.result = None
        self.entries = {}
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Edit Actuator Optimal Forces")
        self.root.geometry("700x600")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all GUI widgets"""
        
        # Header
        header = ttk.Label(
            self.root, 
            text="Edit Optimal Forces for Actuators",
            font=('Arial', 14, 'bold')
        )
        header.pack(pady=10)
        
        # Instructions
        instructions = ttk.Label(
            self.root,
            text="Modify the optimal force values for each actuator below:",
            font=('Arial', 10)
        )
        instructions.pack(pady=5)
        
        # Create frame with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas and scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Info about residual actuators
        residual_info = ttk.Label(
            scrollable_frame,
            text="Residual Actuators (Pelvis) - Fixed at optimal_force = 1.0",
            font=('Arial', 11, 'bold'),
            foreground='blue'
        )
        residual_info.grid(row=0, column=0, columnspan=3, pady=(5, 10), sticky='w')
        
        row = 1
        
        # Reserve Actuators Section
        reserve_label = ttk.Label(
            scrollable_frame,
            text="Reserve Actuators (Coordinates)",
            font=('Arial', 11, 'bold')
        )
        reserve_label.grid(row=row, column=0, columnspan=3, pady=(5, 5), sticky='w')
        row += 1
        
        # Column headers
        ttk.Label(scrollable_frame, text="Coordinate", font=('Arial', 9, 'bold'), width=25).grid(row=row, column=0, padx=5, pady=2, sticky='w')
        ttk.Label(scrollable_frame, text="Type", font=('Arial', 9, 'bold'), width=35).grid(row=row, column=1, padx=5, pady=2, sticky='w')
        ttk.Label(scrollable_frame, text="Optimal Force", font=('Arial', 9, 'bold'), width=10).grid(row=row, column=2, padx=5, pady=2)
        row += 1
        
        # Add coordinate actuators
        for coord in self.coordinates:
            name = coord['name']
            coord_type = coord.get('type', 'Coordinate')
            reserve_name = f"{name}_reserve"
            
            # Use calculated force if available, otherwise default
            force_value = self.calculated_forces.get(reserve_name, self.default_force)
            
            ttk.Label(scrollable_frame, text=name, width=25).grid(row=row, column=0, padx=5, pady=2, sticky='w')
            ttk.Label(scrollable_frame, text=coord_type, width=35).grid(row=row, column=1, padx=5, pady=2, sticky='w')
            entry = ttk.Entry(scrollable_frame, width=10)
            entry.insert(0, str(force_value))
            entry.grid(row=row, column=2, padx=5, pady=2)
            self.entries[reserve_name] = entry
            row += 1
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons frame at bottom
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Apply all button
        apply_all_frame = ttk.Frame(button_frame)
        apply_all_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(apply_all_frame, text="Set all to:").pack(side=tk.LEFT, padx=5)
        self.apply_all_entry = ttk.Entry(apply_all_frame, width=10)
        self.apply_all_entry.insert(0, str(self.default_force))
        self.apply_all_entry.pack(side=tk.LEFT, padx=5)
        
        apply_all_btn = ttk.Button(
            apply_all_frame,
            text="Apply to All",
            command=self._apply_to_all
        )
        apply_all_btn.pack(side=tk.LEFT, padx=5)
        
        # OK and Cancel buttons
        ok_btn = ttk.Button(
            button_frame,
            text="OK",
            command=self._on_ok,
            width=15
        )
        ok_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=15
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
    def _apply_to_all(self):
        """Apply the same value to all entries"""
        try:
            value = float(self.apply_all_entry.get())
            for entry in self.entries.values():
                entry.delete(0, tk.END)
                entry.insert(0, str(value))
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
    
    def _on_ok(self):
        """Validate and save results"""
        try:
            self.result = {}
            for name, entry in self.entries.items():
                value = float(entry.get())
                if value <= 0:
                    messagebox.showerror("Invalid Input", f"Force for {name} must be positive")
                    return
                self.result[name] = value
            self.root.quit()
        except ValueError:
            messagebox.showerror("Invalid Input", "All values must be valid numbers")
    
    def _on_cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.root.quit()
    
    def show(self):
        """Show the dialog and return the result"""
        self.root.mainloop()
        self.root.destroy()
        return self.result


def read_inverse_dynamics_moments(id_file_path, moment_percentage=10.0):
    """
    Read inverse dynamics output and calculate optimal forces from moments.
    
    Parameters
    ----------
    id_file_path : str or Path
        Path to inverse dynamics .sto file
    moment_percentage : float
        Percentage of max moment to use as optimal force (default: 10%)
    
    Returns
    -------
    dict
        Dictionary mapping coordinate names to optimal forces
    """
    id_file_path = Path(id_file_path)
    if not id_file_path.exists():
        print(f"Warning: Inverse dynamics file not found: {id_file_path}")
        return {}
    
    print(f"Reading inverse dynamics moments from: {id_file_path}")
    
    # Read the .sto file
    storage = osim.Storage(str(id_file_path))
    
    # Get column labels
    labels = []
    for i in range(storage.getColumnLabels().getSize()):
        labels.append(storage.getColumnLabels().get(i))
    
    # Extract data
    moments = {}
    for label in labels:
        if label.lower() == 'time':
            continue
        
        # Get data for this column
        state_vector = osim.ArrayDouble()
        storage.getDataColumn(label, state_vector)
        
        # Convert to numpy array and get max absolute value
        data = np.array([state_vector.get(i) for i in range(state_vector.getSize())])
        max_moment = np.max(np.abs(data))
        
        # Calculate optimal force as percentage of max moment
        optimal_force = max_moment * (moment_percentage / 100.0)
        
        # Store with reserve suffix
        coord_name = label.replace('_moment', '').replace('_force', '')
        moments[f"{coord_name}_reserve"] = max(optimal_force, 1.0)  # Minimum of 1.0
        
        print(f"  {coord_name}: max moment = {max_moment:.2f}, optimal force = {optimal_force:.2f}")
    
    return moments


def create_actuators_so(model_path, output_path=None, optimal_force=800, 
                        pelvis_body_name="pelvis", pelvis_com_offset=None,
                        exclude_coordinates=None, use_gui=True, 
                        inverse_dynamics_output=None, moment_percentage=10.0):
    """
    Create actuators_so.xml file for Static Optimization.
    
    Parameters
    ----------
    model_path : str or Path
        Path to the OpenSim model (.osim file)
    output_path : str or Path, optional
        Path for the output XML file. If None, saves to same directory as model
    optimal_force : float, optional
        Default optimal force value for reserve actuators (default: 800)
    pelvis_body_name : str, optional
        Name of the pelvis body in the model (default: "pelvis")
    pelvis_com_offset : list or tuple, optional
        COM offset [x, y, z] for point actuators. If None, uses model's pelvis COM
    exclude_coordinates : list, optional
        List of coordinate names to exclude from reserve actuators
    use_gui : bool, optional
        If True, opens GUI to edit optimal forces (default: True)
    inverse_dynamics_output : str or Path, optional
        Path to inverse dynamics .sto file. If provided, uses moments to calculate optimal forces
    moment_percentage : float, optional
        Percentage of max moment to use as optimal force (default: 10%)
    
    Returns
    -------
    str
        Path to the created actuators file
    """
    model_path = Path(model_path)
    
    # Load the model
    print(f"Loading model: {model_path}")
    model = osim.Model(str(model_path))
    model.initSystem()
    
    # Get pelvis body and COM
    pelvis = model.getBodySet().get(pelvis_body_name)
    if pelvis_com_offset is None:
        com = pelvis.get_mass_center()
        pelvis_com_offset = [com.get(0), com.get(1), com.get(2)]
    
    # Get all coordinates first to show in GUI
    coord_set = model.getCoordinateSet()
    exclude_coordinates = exclude_coordinates or []
    
    # Common coordinates to exclude (locked or prescribed motion)
    default_excludes = [
        'pelvis_tilt', 'pelvis_list', 'pelvis_rotation',
        'pelvis_tx', 'pelvis_ty', 'pelvis_tz'
    ]
    exclude_coordinates.extend(default_excludes)
    
    # Build list of coordinates for GUI
    coordinates_list = []
    for i in range(coord_set.getSize()):
        coord = coord_set.get(i)
        coord_name = coord.getName()
        
        # Skip excluded coordinates
        if coord_name in exclude_coordinates:
            continue
        
        # Skip locked coordinates
        if coord.getLocked(model.getWorkingState()):
            continue
        
        coordinates_list.append({
            'name': coord_name,
            'type': 'Reserve Actuator'
        })
    
    # Calculate forces from inverse dynamics if provided
    calculated_forces = {}
    if inverse_dynamics_output:
        calculated_forces = read_inverse_dynamics_moments(inverse_dynamics_output, moment_percentage)
    
    # Show GUI if requested
    if use_gui:
        print("\nOpening GUI to edit optimal forces...")
        editor = ActuatorForceEditor(coordinates_list, default_force=optimal_force, calculated_forces=calculated_forces)
        gui_forces = editor.show()
        
        if gui_forces is None:
            print("Operation cancelled by user.")
            return None
        
        # Use GUI values for reserves only
        calculated_forces.update(gui_forces)
    elif not calculated_forces:
        # No GUI and no inverse dynamics - use default for all
        for coord in coordinates_list:
            calculated_forces[f"{coord['name']}_reserve"] = optimal_force
    
    # Create ForceSet
    force_set = osim.ForceSet()
    force_set.setName("LowerBody_RRA")
    
    # Add Point Actuators (FX, FY, FZ) on pelvis
    print("Creating residual actuators...")
    directions = [
        ("FX", [1, 0, 0]),
        ("FY", [0, 1, 0]),
        ("FZ", [0, 0, 1])
    ]
    
    for name, direction in directions:
        actuator = osim.PointActuator()
        actuator.setName(name)
        actuator.set_body(pelvis_body_name)
        actuator.set_point(osim.Vec3(pelvis_com_offset[0], 
                                      pelvis_com_offset[1], 
                                      pelvis_com_offset[2]))
        actuator.set_direction(osim.Vec3(direction[0], direction[1], direction[2]))
        
        # Pelvis residuals are always set to 1.0
        actuator.set_optimal_force(1.0)
        actuator.setMinControl(-float('inf'))
        actuator.setMaxControl(float('inf'))
        force_set.cloneAndAppend(actuator)
    
    # Add Torque Actuators (MX, MY, MZ) on pelvis
    torque_axes = [
        ("MX", [1, 0, 0]),
        ("MY", [0, 1, 0]),
        ("MZ", [0, 0, 1])
    ]
    
    for name, axis in torque_axes:
        actuator = osim.TorqueActuator()
        actuator.setName(name)
        actuator.setBodyA(pelvis)
        actuator.setBodyB(model.getGround())
        actuator.set_axis(osim.Vec3(axis[0], axis[1], axis[2]))
        
        # Pelvis residuals are always set to 1.0
        actuator.set_optimal_force(1.0)
        actuator.setMinControl(-float('inf'))
        actuator.setMaxControl(float('inf'))
        force_set.cloneAndAppend(actuator)
    
    # Add Coordinate Actuators (reserves) for each coordinate
    print("Creating reserve actuators...")
    
    reserve_count = 0
    for i in range(coord_set.getSize()):
        coord = coord_set.get(i)
        coord_name = coord.getName()
        
        # Skip excluded coordinates
        if coord_name in exclude_coordinates:
            print(f"  Skipping: {coord_name}")
            continue
        
        # Skip locked coordinates
        if coord.getLocked(model.getWorkingState()):
            print(f"  Skipping locked: {coord_name}")
            continue
        
        # Create reserve actuator
        actuator = osim.CoordinateActuator()
        reserve_name = f"{coord_name}_reserve"
        actuator.setName(reserve_name)
        actuator.setCoordinate(coord)
        
        # Use calculated force from inverse dynamics or GUI, otherwise use default
        force = calculated_forces.get(reserve_name, optimal_force)
        actuator.set_optimal_force(force)
        actuator.setMinControl(-1.0)
        actuator.setMaxControl(1.0)
        force_set.cloneAndAppend(actuator)
        reserve_count += 1
        print(f"  Created reserve: {reserve_name} (force: {force:.2f})")
    
    print(f"\nCreated {reserve_count} reserve actuators")
    
    # Determine output path
    if output_path is None:
        output_path = model_path.parent / "actuators_so.xml"
    else:
        output_path = Path(output_path)
    
    # Write to XML file
    print(f"\nSaving to: {output_path}")
    force_set.printToXML(str(output_path))
    
    print("✓ Actuators file created successfully!")
    return str(output_path)



if __name__ == "__main__":
    
    model_path = input("Enter path to OpenSim model (.osim): ").strip('"')
    output_path = input("Enter output path for actuators file (or press Enter to save in model directory): ").strip('"')
    
    id_output = input("Enter path to inverse dynamics .sto file (or press Enter to skip): ").strip('"')
    
    if id_output:
        moment_pct = input("Enter percentage of max moment for optimal force (default 10): ").strip()
        moment_pct = float(moment_pct) if moment_pct else 10.0
        optimal_force = 1.0  # Fallback value for coordinates not in ID file
    else:
        moment_pct = 10.0
        optimal_force = input("Enter default optimal force for actuators (default 800): ").strip()
        optimal_force = float(optimal_force) if optimal_force else 800
    
    use_gui_input = input("Use GUI to edit forces? (y/n, default y): ").strip().lower()
    use_gui = use_gui_input != 'n'

    result = create_actuators_so(
        model_path=model_path,
        output_path=output_path if output_path else None,
        optimal_force=optimal_force,
        use_gui=use_gui,
        inverse_dynamics_output=id_output if id_output else None,
        moment_percentage=moment_pct
    )
    
    if result:
        print(f"\n✓ Success! File saved to: {result}")
    else:
        print("\n✗ Operation cancelled or failed.")
