"""
EMG Processing Module

This module provides classes for processing and normalizing EMG signals from OpenSim .mot files.
It includes functionality for cleaning, filtering, and amplitude normalization of EMG data.

Classes:
    ProcessEMGmot: Process individual EMG .mot files
    FilterNormaliseEMGs: Process and normalize multiple EMG files

Dependencies:
    - numpy
    - pandas  
    - opensim
    - neurokit2
    - scipy

Example usage:
    # Process a single EMG file
    processor = ProcessEMGmot(output_folder="./output", emg_mot_path="data.mot")
    
    # Process and normalize multiple EMG files
    file_paths = ["trial1.mot", "trial2.mot", "trial3.mot"]
    normalizer = FilterNormaliseEMGs(file_paths)
    normalizer.amplitude_normalise()
"""

import os
import numpy as np
import pandas as pd
import opensim as osim
import neurokit2 as nk
import scipy.signal as sig


def create_mot_file_from_dataframe(df, filename, time_column=None):
    """
    Create and save a .mot file from a pandas DataFrame using OpenSim's TimeSeriesTable
    
    Parameters:
    - df: pandas DataFrame containing your data
    - time_column: string name of the time column, or None if time is the index
    - filename: output filename (should end with .mot)
    """
    
    # Extract time vector
    if time_column is None:
        # Time is in the index
        time_vector = df.index.values
        data_columns = df.columns.tolist()
        data = df.values
    else:
        # Time is a column in the DataFrame
        time_vector = df[time_column].values
        data_columns = [col for col in df.columns if col != time_column]
        data = df[data_columns].values
    
    # Create a TimeSeriesTable
    table = osim.TimeSeriesTable()
    
    # Set column labels
    vec_labels = osim.StdVectorString()
    for label in data_columns:
        vec_labels.append(label)
    table.setColumnLabels(vec_labels)
    
    # Add data row by row
    for i, time in enumerate(time_vector):
        row = osim.RowVector(data[i, :])
        table.appendRow(float(time), row)
    
    # Write to file
    osim.STOFileAdapter.write(table, filename)
    print(f"MOT file saved as: {filename}")


class ProcessEMGmot:
    """
    Process individual EMG .mot files from OpenSim.
    
    This class loads EMG data from OpenSim TimeSeriesTable format, applies
    filtering and envelope extraction, and saves the processed data to CSV.
    
    Attributes:
        output_folder (str): Directory path for saving processed files
        emg_mot_path (str): Path to the input .mot file
        sample_rate (int): Sampling rate of the EMG data (default: 1000 Hz)
        time (np.array): Time vector from the EMG data
        emg_names (list): List of EMG channel names
        data_array (np.array): Raw EMG data array (channels x time points)
        df_filtered (pd.DataFrame): Processed EMG data as DataFrame
    """
    
    def __init__(self, output_folder, emg_mot_path, sample_rate=1000):
        """
        Initialize EMG processor and automatically process the data.
        
        Args:
            output_folder (str): Directory path for saving processed files
            emg_mot_path (str): Path to the input .mot file
            sample_rate (int): Sampling rate of the EMG data (default: 1000 Hz)
        """
        self.output_folder = output_folder
        self.emg_mot_path = emg_mot_path
        self.sample_rate = sample_rate
        self.emg_data = None
        self.load_emg_data_to_df()
        self.process_emg_mot()

    def load_emg_data_to_df(self):
        """
        Load EMG data from OpenSim TimeSeriesTable format.
        
        Extracts time vector, channel names, and data matrix from the .mot file.
        
        Raises:
            ValueError: If EMG data cannot be loaded
        """
        emg_data = osim.TimeSeriesTable(self.emg_mot_path)
        
        if emg_data is None:
            raise ValueError("EMG data not loaded. Call load_emg_data() first.")
        print(f"Loaded EMG data with {emg_data.getNumRows()} rows and {emg_data.getNumColumns()} columns.")
        
        self.time = np.array(emg_data.getIndependentColumn())
        self.emg_names = list(emg_data.getColumnLabels())
        rows, cols = len(self.time), len(self.emg_names)

        # Get the data matrix (rows x columns)
        try:
            data_matrix = emg_data.getMatrix().to_numpy()
            self.data_array = data_matrix.T  # Transpose to get (channels x time points)
        except Exception as e:
            print(f'Matrix method extraction failed: {e}')
    
    def filter_emg_signals(self):
        """
        Apply filtering to all EMG channels and create filtered DataFrame.
        
        Creates a DataFrame with time as index and filtered EMG signals as columns.
        """
        # Add time column
        filtered_data = {'time': self.time}
        
        # Filter and add EMG data column by column
        for i, emg in enumerate(self.emg_names):
            filtered_data[emg] = self.filter_emg(self.data_array[i], self.sample_rate)

        # Create a DataFrame from the filtered data
        self.df_filtered = pd.DataFrame(filtered_data)
        
        # Set the time column as index
        self.df_filtered = self.df_filtered.set_index('time')
        
    @staticmethod
    def filter_emg(signal, sample_rate, low_pass_cutoff=20):
        """
        Process EMG signal: clean, rectify, and filter to get the envelope.
        
        Args:
            signal (np.array): Raw EMG signal
            sample_rate (int): Sampling rate in Hz
            low_pass_cutoff (float): Low-pass filter cutoff frequency in Hz (default: 6)
            
        Returns:
            np.array: Processed EMG envelope
        """
        # Clean the EMG signal using NeuroKit2
        cleaned_signal = nk.emg_clean(signal, sampling_rate=sample_rate, method='biosppy')
        
        # Rectify the signal (full-wave rectification)
        rectified_signal = np.abs(cleaned_signal)
        
        # Apply low-pass filter to get envelope
        low_pass = low_pass_cutoff / (sample_rate / 2)  # Normalize frequency
        b, a = sig.butter(4, low_pass, btype='lowpass')
        emg_envelope = sig.filtfilt(b, a, rectified_signal)
        
        return emg_envelope

    def process_emg_mot(self):
        """
        Execute the complete EMG processing pipeline and save results.
        
        Returns:
            pd.DataFrame: Processed EMG data
        """
        self.filter_emg_signals()
        
        # Write to MOT file
        output_file = os.path.join(self.output_folder, 'processed_emg.mot')
        create_mot_file_from_dataframe(self.df_filtered, output_file) # alternative: self.df_filtered.to_csv(output_file)
        print(f"Processed EMG data saved to: {output_file}")
        
        return self.df_filtered


class FilterNormaliseEMGs:
    """
    Process and normalize multiple EMG files for comparative analysis.
    
    This class automatically processes multiple EMG .mot files and performs amplitude 
    normalization across all trials. All processing is done automatically during initialization.
    
    Attributes:
        list_of_paths_to_emg_mots (list): List of paths to .mot files
        sample_rate (int): Sampling rate of the EMG data
        emg_processes (list): List of ProcessEMGmot objects
        all_dfs (list): List of processed DataFrames
        max_values (pd.Series): Maximum values across all channels and trials
        summary_stats (dict): Summary statistics across all processed data
    """
    
    def __init__(self, list_of_paths_to_emg_mots, sample_rate=1000, auto_normalize=True):
        """
        Initialize the normalizer and automatically process and normalize all EMG files.
        
        Args:
            list_of_paths_to_emg_mots (list): List of paths to .mot files
            sample_rate (int): Sampling rate of the EMG data (default: 1000 Hz)
            auto_normalize (bool): Whether to automatically perform normalization (default: True)
        """
        self.list_of_paths_to_emg_mots = list_of_paths_to_emg_mots
        self.sample_rate = sample_rate
        self.emg_processes = []

        print("="*60)
        print("EMG PROCESSING AND NORMALIZATION PIPELINE")
        print("="*60)
        
        # Step 1: Process each EMG file
        print(f"\n[STEP 1/4] Processing {len(list_of_paths_to_emg_mots)} EMG files...")
        for i, emg_mot_path in enumerate(self.list_of_paths_to_emg_mots):
            print(f"  Processing file {i+1}/{len(list_of_paths_to_emg_mots)}: {os.path.basename(emg_mot_path)}")
            output_folder = os.path.dirname(emg_mot_path)
            emg_process = ProcessEMGmot(output_folder, emg_mot_path, sample_rate=self.sample_rate)
            self.emg_processes.append(emg_process)
       
        # Step 2: Collect all filtered DataFrames
        print("\n[STEP 2/4] Collecting processed data...")
        self.all_dfs = [process.df_filtered for process in self.emg_processes]
        
        # Step 3: Calculate maximum values across all trials for normalization
        print("\n[STEP 3/4] Calculating normalization factors...")
        self.max_values = pd.concat(self.all_dfs).max()
        
        # Avoid division by zero for channels with no activity
        self.max_values[self.max_values == 0] = 1
        
        print(f"  Normalization factors calculated for {len(self.max_values)} EMG channels.")
        
        # Step 4: Automatically perform normalization if requested
        if auto_normalize:
            print("\n[STEP 4/4] Performing amplitude normalization...")
            self.amplitude_normalise()
            
            # Generate summary statistics
            print("\n[BONUS] Generating summary statistics...")
            self.summary_stats = self.get_summary_statistics()
            
            print("\n" + "="*60)
            print("PROCESSING COMPLETE!")
            print("="*60)
            print(f"✓ Processed {len(self.list_of_paths_to_emg_mots)} EMG files")
            print(f"✓ Generated filtered EMG envelopes")
            print(f"✓ Applied amplitude normalization")
            print(f"✓ Saved processed and normalized data to CSV files")
            print(f"✓ Generated summary statistics")
            print("="*60)
        else:
            print(f"\n  Auto-normalization disabled. Call amplitude_normalise() manually if needed.")
            self.summary_stats = None

    def amplitude_normalise(self):
        """
        Perform amplitude normalization on all processed EMG data.
        
        Normalizes each trial by dividing by the maximum values across all trials,
        resulting in values between 0 and 1 for comparative analysis.
        """
        print("Performing amplitude normalization...")
        
        for i, table in enumerate(self.all_dfs):
            # Normalize by dividing by maximum values
            table_normalised = table / self.max_values
            
            # Save normalized data
            output_folder = os.path.dirname(self.list_of_paths_to_emg_mots[i])
            output_file = os.path.join(output_folder, 'processed_emg_normalised.mot')
            create_mot_file_from_dataframe(table_normalised, output_file)
            print(f"Normalized data saved: {output_file}")
        
        print("Amplitude normalization complete!")

    def get_summary_statistics(self):
        """
        Calculate summary statistics across all processed trials.
        
        Returns:
            dict: Dictionary containing mean, std, min, max for each EMG channel
        """
        # Combine all normalized data
        all_data = pd.concat([df / self.max_values for df in self.all_dfs])
        
        summary_stats = {
            'mean': all_data.mean(),
            'std': all_data.std(),
            'min': all_data.min(),
            'max': all_data.max(),
            'count': all_data.count()
        }
        
        return summary_stats


def main():
    """
    Example usage of the EMG processing module.
    """
    # Example usage
    print("EMG Processing Module")
    print("====================")
    
    # SIMPLE USAGE - Just provide file paths and everything is done automatically!
    # file_paths = [
    #     "path/to/trial1.mot",
    #     "path/to/trial2.mot", 
    #     "path/to/trial3.mot"
    # ]
    # 
    # # This single line does EVERYTHING:
    # # - Loads and processes all EMG files
    # # - Applies filtering and envelope extraction
    # # - Calculates normalization factors
    # # - Applies amplitude normalization
    # # - Saves all processed and normalized data
    # # - Generates summary statistics
    # processor = FilterNormaliseEMGs(file_paths)
    # 
    # # Optional: Access summary statistics
    # if processor.summary_stats:
    #     print("Mean activation across all trials:")
    #     print(processor.summary_stats['mean'])
    
    # ADVANCED USAGE - Manual control
    # processor = FilterNormaliseEMGs(file_paths, auto_normalize=False)
    # processor.amplitude_normalise()  # Call manually if needed


if __name__ == "__main__":
    main()