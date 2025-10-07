import os 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import utils
start_time = time.time()

class OsimPlotter(utils):
    def __init__(self, fileDict:dict = None):
        self.fileDict = fileDict

    def lines_multiple_files(self):
        pass
    
    def manual_plotter(self):
        
        
        for filePath, df in self.fileDict.items():
            if data is None:
                print(f"No data loaded for file: {filePath}. Skipping.")
                continue
            
            if 'time' not in df.columns:
                print(f"'time' column not found in data from {filePath}. Skipping.")
                continue
            
            time_data = df['time']
            
            plt.figure(figsize=(10, 6))
            for col in self.columns_to_plot:
                if col in df.columns:
                    plt.plot(time_data, df[col], label=col)
                else:
                    print(f"Column '{col}' not found in data from {filePath}.")
            
            plt.title(f"Data from {os.path.basename(filePath)}")
            plt.xlabel("Time (s)")
            plt.ylabel("Value")
            plt.legend()
            plt.grid()
            plt.show()
        
    def input_multiple_files(self):
        self.fileDict = {}

        while True:
            file_path = input("Enter the path to a data file (or press Enter to finish): ").strip()
            if not file_path:
                break
            if os.path.exists(file_path):
                self.fileDict[file_path] = utils.load_any_data_file(file_path)
                self.fileDict[file_path] = utils.time_normalise_df(self.fileDict[file_path])
                print(f"Loaded data from: {file_path}")
            else:
                print(f"File not found: {file_path}. Please try again.")

        return self.fileDict

if __name__ == "__main__":
    
    plotter = OsimPlotter()
    plotter.input_multiple_files()
    
    plotter.columns_to_plot = ['hip_flexion_r', 'knee_angle_r', 'ankle_angle_r']
    
    
    

    end_time = time.time()
    elapsed_time = end_time - start_time
    utils.print_to_log(f"Total plotting time: {elapsed_time:.2f} seconds \n \n")