from logging import root
from tkinter import ttk
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

import paths
import utils

class TestGUI(utils.Settings):
    def __init__(self):
        super().__init__()
        
        self.root = ctk.CTk()
        self.root.title("Test GUI")
        
class PowerliftingAnalysisGUI(utils.Settings):
    def __init__(self):

        self.root = ctk.CTk()
        self.root = self.root
        self.root.title("Powerlifting Analysis Tool")
        self.root.geometry("800x600")
        
        self.data = None
        self.simulation_dir = paths.SIMULATION_DIR
        self.results_dir = paths.RESULTS_DIR
        self.subjectList = []
        self.setup_ui()
        
    
    def input_frame_ui(self, text='Input File', command=None, location=(0,0)):
        ''' add a simple text box with a search 
        button to select a file if needed 
        (make background red if file not found)'''
        
        input_frame = ctk.CTkFrame(self.root)
        input_frame.grid(row=location[0], column=location[1], sticky=(ctk.W, ctk.E, ctk.N, ctk.S), padx=5, pady=5)

        label = ctk.CTkLabel(input_frame, text=text)
        label.grid(row=0, column=0, padx=5, pady=5)

        self.file_entry = ctk.CTkEntry(input_frame)
        self.file_entry.grid(row=0, column=0, sticky=(ctk.W, ctk.E))

        ctk.CTkButton(input_frame, text="Select file", command=command).grid(row=0, column=1, padx=5)
        
        return input_frame

    def setup_ui(self):
        # Configure grid weights for centering
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky=(ctk.W, ctk.E, ctk.N, ctk.S))
        
        # Square for inputs(model, markers, grf, emg)
        # self.input_frame_ui(title="Load Powerlifting Data", command=self.increase_muscle_force())
        self.input_frame_ui(text="Load Powerlifting Data", command=self.select_file)
        
        # Quit button at bottom center
        quit_button = ctk.CTkButton(self.root, text="Quit", command=self.root.quit)
        quit_button.grid(row=1, column=0, pady=10)
        
        
    def select_file(self):
        file_path = ctk.filedialog.askopenfilename(
            title="Select powerlifting data file",
            filetypes=[("All files", "*.*")]
        )
        if file_path:
            self.file_entry.delete(0, ctk.END)
            self.file_entry.insert(0, file_path)
            self.file_entry.config(fg_color="white")
        else:
            self.file_entry.config(fg_color="red")
    
    def increase_muscle_force(self, model_file_path, factor=1):
        utils.increase_muscle_force(model_file_path, factor)
    
    def load_data(self):
        file_path = filedialog.askopenfilename(
            title="Select powerlifting data file",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.data = pd.read_excel(file_path)
                
                self.file_label.config(text=f"Loaded: {file_path.split('/')[-1]} ({len(self.data)} rows)")
                messagebox.showinfo("Success", f"Data loaded successfully!\nRows: {len(self.data)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def plot_distribution(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        self.ax.clear()
        # Assuming columns like 'squat', 'bench', 'deadlift'
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            self.data[numeric_cols[0]].hist(bins=20, ax=self.ax, alpha=0.7)
            self.ax.set_title(f"Distribution of {numeric_cols[0]}")
            self.ax.set_xlabel(numeric_cols[0])
            self.ax.set_ylabel("Frequency")
        
        self.canvas.draw()
    
    def plot_progress(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        self.ax.clear()
        # Simple time series plot
        if 'date' in self.data.columns:
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                self.ax.plot(self.data['date'], self.data[numeric_cols[0]], marker='o')
                self.ax.set_title("Progress Over Time")
                self.ax.set_xlabel("Date")
                self.ax.set_ylabel(numeric_cols[0])
        else:
            self.ax.text(0.5, 0.5, "No date column found", ha='center', va='center', transform=self.ax.transAxes)
        
        self.canvas.draw()
    
    def plot_correlations(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        self.ax.clear()
        numeric_data = self.data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) >= 2:
            corr_matrix = numeric_data.corr()
            im = self.ax.imshow(corr_matrix, cmap='coolwarm', aspect='auto')
            self.ax.set_xticks(range(len(corr_matrix.columns)))
            self.ax.set_yticks(range(len(corr_matrix.columns)))
            self.ax.set_xticklabels(corr_matrix.columns, rotation=45)
            self.ax.set_yticklabels(corr_matrix.columns)
            self.ax.set_title("Correlation Matrix")
            plt.colorbar(im, ax=self.ax)
        
        self.canvas.draw()
    
    def plot_weight_class(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        self.ax.clear()
        # Assuming there's a weight class column
        if 'weight_class' in self.data.columns:
            weight_class_counts = self.data['weight_class'].value_counts()
            weight_class_counts.plot(kind='bar', ax=self.ax)
            self.ax.set_title("Athletes by Weight Class")
            self.ax.set_xlabel("Weight Class")
            self.ax.set_ylabel("Count")
        else:
            self.ax.text(0.5, 0.5, "No weight_class column found", ha='center', va='center', transform=self.ax.transAxes)
        
        self.canvas.draw()
    
    def show_summary(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        self.ax.clear()
        summary = self.data.describe()
        
        # Display summary as text
        summary_text = summary.to_string()
        self.ax.text(0.05, 0.95, summary_text, transform=self.ax.transAxes, 
                    fontfamily='monospace', fontsize=8, verticalalignment='top')
        self.ax.set_title("Summary Statistics")
        self.ax.axis('off')
        
        self.canvas.draw()

if __name__ == "__main__":
    
    app = PowerliftingAnalysisGUI()
    app.root.mainloop()