"""
Module for creating and processing generic subjects with different models.

This module automates the workflow for:
1. Creating a new subject with any generic model (e.g., Lernagopal, Rajagopal, etc.)
2. Rescaling/reregistering markers to the generic model
3. Creating scaled models using static trials or generic scaling
4. Creating new simulations subject and session directories
5. Copying input data from existing trials
6. Running IK, ID, MA, SO, and JRA analyses
7. Plotting results

Usage:
    python setup_generic_subject.py
"""

import os
import shutil
import utils
import openSim
import ceinms
from pathlib import Path


class GenericSubject:
    """
    Handles the setup and processing of any generic subject with different model types.
    
    This class can work with multiple model types:
    - generic_model: The base unscaled generic model (e.g., Lernagopal, Rajagopal)
    - generic_model_with_markerset: Generic model with experimental markerset added
    - scaled_model: Model scaled to subject using static trial or generic scaling
    - mri_model: MRI-based model (if available)
    """
    
    def __init__(self, 
                 target_subject='Athlete_03_Lernagopal',
                 source_subject='Athlete_03',
                 generic_model_path=None,
                 model_type='Lernagopal',
                 source_session='25_03_31',
                 target_session='25_03_31',
                 static_session='25_03_31',
                 trials=None):
        """
        Initialize GenericSubject.
        
        Args:
            target_subject: Name of the new subject to create
            source_subject: Name of the source subject to copy data from
            generic_model_path: Path to the generic model file
            model_type: Type of model (e.g., 'Lernagopal', 'Rajagopal', 'Purzel')
            source_session: Source session to copy data from
            target_session: Target session name
            static_session: Session containing static trial for scaling (optional)
            trials: List of trials to process
        """
        self.target_subject = target_subject
        self.source_subject = source_subject
        self.model_type = model_type
        self.source_session = source_session
        self.target_session = target_session
        self.static_session = static_session
        
        # Trials to process
        self.trials = trials or ['Walking_02', 'Squat_BW_01', 'Squat_35kg_01']
        self.static_trial = 'Static_01'  # Name of static trial if it exists
        
        # Paths
        self.models_dir = utils.MODELS_DIR
        self.simulations_dir = utils.SIMULATIONS_DIR
        self.setup_dir = os.path.join(utils.CODE_DIR, 'setupFiles', model_type)
        
        # Model paths - different types of models
        if generic_model_path is None:
            print(f"✗ Generic model path must be provided.")
            return
        
        self.generic_model = generic_model_path
        self.scaled_model = None  # Will be set after scaling
        self.mri_model = None  # Optional MRI-based model
        
        # Source and target model paths
        self.source_model_dir = os.path.join(self.models_dir, self.source_subject)
        self.target_model_dir = os.path.join(self.models_dir, self.target_subject)
        
        # Source and target simulation paths
        self.source_sim_dir = os.path.join(self.simulations_dir, self.source_subject, self.source_session)
        self.target_sim_dir = os.path.join(self.simulations_dir, self.target_subject, self.target_session)
        
        # Static trial paths (if using static for scaling)
        self.static_sim_dir = os.path.join(self.simulations_dir, self.source_subject, self.static_session)
        
        # Active model for analyses (defaults to scaled_model when available)
        self.active_model = 'scaled.osim'
        
        # Processing flags
        self.replace = True  # Whether to replace existing files
    
    def create_generic_model_with_markerset(self, source_model_path=None):
        print(f"\n{'='*60}")
        print('✗ not implemented: create_generic_model_with_markerset')
        print(f"{'='*60}\n")

        return False
    
    def create_scaled_model_from_static(self, static_trial_path=None):
        """
        Create scaled model using static trial.
        
        Args:
            static_trial_path: Path to static trial directory (uses default if None)
        """
        print(f"\n{'='*60}")
        print(f"Creating scaled model from static trial")
        print(f"{'='*60}\n")
        
        if static_trial_path is None:
            static_trial_path = os.path.join(self.static_sim_dir, self.static_trial)
        
        if not os.path.exists(static_trial_path):
            print(f"✗ Static trial not found: {static_trial_path}")
            print(f"  Will use generic scaling instead")
            return self.create_scaled_model_generic()
        
        try:
            # Use the Analyse class to handle scaling
            static_analysis = utils.Analyse(static_trial_path)
            
            # Get static marker file
            static_markers = os.path.join(static_trial_path, 'marker_experimental.trc')
            if not os.path.exists(static_markers):
                print(f"✗ Static markers not found: {static_markers}")
                return False
            else:
                print(f"  Using static markers: {static_markers}")
                # Copy static trial folder to target subject
                source_static_dir = os.path.join(self.static_sim_dir, self.static_trial)
                target_static_dir = os.path.join(self.target_sim_dir, self.static_trial)

                if os.path.exists(source_static_dir) and not os.path.exists(target_static_dir):
                    shutil.copytree(source_static_dir, target_static_dir)
                    print(f"  ✓ Copied static trial folder to target subject")
                elif os.path.exists(target_static_dir):
                    print(f"  ✓ Static trial folder already exists in target subject")
                       
            # Create scale setup and run scaling
            session_model_dir = os.path.join(self.target_model_dir, self.target_session)
            if not os.path.exists(session_model_dir):
                os.makedirs(session_model_dir)
            
            scaled_output = os.path.join(session_model_dir, 'scaled.osim')
            
            # Use OpenSim scaling (you may need to implement this in openSim.py)
            print(f"  Base model: {self.generic_model}")
            print(f"  Static markers: {static_markers}")
            print(f"  Output: {scaled_output}")
            
            # Run scaling
            breakpoint()
            if self.generic_model:
                openSim.scale_model(
                    osim_modelPath=self.generic_model,
                    setup_xml_path=os.path.join(static_trial_path, 'setup_scale.xml'),
                    scaled_model_path=scaled_output
                )
            else:
                print(f"✗ Cannot create scaled model - no markerset model available")
                return False
            
            self.scaled_model = scaled_output
            self.active_model = 'scaled.osim'
            print(f"✓ Scaled model created: {scaled_output}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to create scaled model: {str(e)}")
            return False
    
    def create_scaled_model_generic(self):
        """
        Create scaled model using generic scaling (without static trial).
        """
        print(f"\n{'='*60}")
        print(f"Creating scaled model with generic scaling")
        print(f"{'='*60}\n")
        
        session_model_dir = os.path.join(self.target_model_dir, self.target_session)
        if not os.path.exists(session_model_dir):
            os.makedirs(session_model_dir)
        
        scaled_output = os.path.join(session_model_dir, 'scaled.osim')
        
        # Use model with markerset if available
        if self.generic_model_with_markerset:
            shutil.copy2(self.generic_model_with_markerset, scaled_output)
            print(f"✓ Copied model with markerset as scaled model")
        else:
            shutil.copy2(self.generic_model, scaled_output)
            print(f"⚠ Copied generic model as scaled (needs markerset and scaling)")
        
        self.scaled_model = scaled_output
        self.active_model = 'scaled.osim'
        return True
    
    def set_mri_model(self, mri_model_path):
        """
        Set MRI-based model path.
        
        Args:
            mri_model_path: Path to MRI-based model
        """
        if os.path.exists(mri_model_path):
            self.mri_model = mri_model_path
            print(f"✓ MRI model set: {mri_model_path}")
            return True
        else:
            print(f"✗ MRI model not found: {mri_model_path}")
            return False
    
    def get_active_model_path(self):
        """Get path to the currently active model."""
        return os.path.join(self.target_model_dir, self.target_session, self.active_model)
        
    def create_directory_structure(self):
        """Create the directory structure for the new subject."""
        print(f"\n{'='*60}")
        print(f"Creating directory structure for {self.target_subject}")
        print(f"{'='*60}\n")
        
        # Create model directory with session subdirectory
        session_model_dir = os.path.join(self.target_model_dir, self.target_session)
        if not os.path.exists(session_model_dir):
            os.makedirs(session_model_dir)
            print(f"✓ Created model directory: {session_model_dir}")
        else:
            print(f"✓ Model directory already exists: {session_model_dir}")
        
        # Create session directory
        if not os.path.exists(self.target_sim_dir):
            os.makedirs(self.target_sim_dir)
            print(f"✓ Created simulation directory: {self.target_sim_dir}")
        else:
            print(f"✓ Simulation directory already exists: {self.target_sim_dir}")
        
        # Create trial directories
        for trial in self.trials:
            trial_dir = os.path.join(self.target_sim_dir, trial)
            if not os.path.exists(trial_dir):
                os.makedirs(trial_dir)
                print(f"✓ Created trial directory: {trial}")
            else:
                print(f"✓ Trial directory already exists: {trial}")
    
    def setup_models(self, use_static=True):
        """
        Setup all model types.
        
        Args:
            use_static: Whether to use static trial for scaling
        """
        print(f"\n{'='*60}")
        print(f"Setting up models for {self.target_subject}")
        print(f"{'='*60}\n")
        
        # Step 1: Create generic model with experimental markerset
        if not self.create_generic_model_with_markerset():
            print(f"⚠ Warning: Could not create model with markerset")
        
        # Step 2: Create scaled model
        if use_static:
            # Try to use static trial for scaling
            if not self.create_scaled_model_from_static():
                print(f"⚠ Warning: Static scaling failed, using generic scaling")
        else:
            self.create_scaled_model_generic()
        
        # Step 3: Check for MRI model (optional)
        mri_model_path = os.path.join(self.target_model_dir, self.target_session, 'mri_scaled.osim')
        if os.path.exists(mri_model_path):
            self.set_mri_model(mri_model_path)
        
        return True
    
    def copy_trial_data(self):
        """Copy input data (.trc, .mot, setup files) from source trials."""
        print(f"\n{'='*60}")
        print(f"Copying trial input data")
        print(f"{'='*60}\n")
        
        files_to_copy = [
            'marker_experimental.trc',
            'c3dfile.c3d',
            'GRF.xml',
            'grf.mot',
        ]
        
        for trial in self.trials:
            print(f"\nProcessing trial: {trial}")
            source_trial_dir = os.path.join(self.source_sim_dir, trial)
            target_trial_dir = os.path.join(self.target_sim_dir, trial)
            
            if not os.path.exists(source_trial_dir):
                print(f"  ✗ Source trial directory not found: {source_trial_dir}")
                continue
            
            # Copy files
            for file in files_to_copy:
                source_file = os.path.join(source_trial_dir, file)
                target_file = os.path.join(target_trial_dir, file)
                
                if os.path.exists(source_file):
                    shutil.copy2(source_file, target_file)
                    print(f"  ✓ Copied {file}")
                else:
                    print(f"  ⚠ File not found: {file}")
            
            # Copy setup files from setupFiles/Lernagopal
            self._copy_setup_files(target_trial_dir)
    
    def _copy_setup_files(self, trial_dir):
        """Copy setup XML files from model setupFiles directory."""
        setup_files = [
            'setup_IK.xml',
            'setup_ID.xml',
            'setup_MA.xml',
            'setup_SO.xml',
            'setup_JRA.xml',
            'actuators_so.xml',
        ]
        
        for setup_file in setup_files:
            source_file = os.path.join(self.setup_dir, setup_file)
            target_file = os.path.join(trial_dir, setup_file)
            
            if os.path.exists(source_file):
                shutil.copy2(source_file, target_file)
                print(f"  ✓ Copied setup file: {setup_file}")
    
    def run_ik_all_trials(self):
        """Run Inverse Kinematics for all trials."""
        print(f"\n{'='*60}")
        print(f"Running Inverse Kinematics")
        print(f"{'='*60}\n")
        
        for trial in self.trials:
            print(f"\n→ Processing {trial}")
            trial_path = os.path.join(self.target_sim_dir, trial)
            
            try:
                analysis = utils.Analyse(trial_path)
                analysis.replace = self.replace
                
                # Update model to active model
                model_path = self.get_active_model_path()
                analysis.update_model(model_path)
                
                print(f"  Model: {analysis.model_dir}")
                print(f"  Time range: {analysis.time_range}")
                
                analysis.run_ik()
                print(f"  ✓ IK completed for {trial}")
            except Exception as e:
                print(f"  ✗ IK failed for {trial}: {str(e)}")
    
    def run_id_all_trials(self):
        """Run Inverse Dynamics for all trials."""
        print(f"\n{'='*60}")
        print(f"Running Inverse Dynamics")
        print(f"{'='*60}\n")
        
        for trial in self.trials:
            print(f"\n→ Processing {trial}")
            trial_path = os.path.join(self.target_sim_dir, trial)
            
            try:
                analysis = utils.Analyse(trial_path)
                analysis.replace = self.replace
                
                # Update model
                model_path = self.get_active_model_path()
                analysis.update_model(model_path)
                
                analysis.run_id()
                print(f"  ✓ ID completed for {trial}")
            except Exception as e:
                print(f"  ✗ ID failed for {trial}: {str(e)}")
    
    def run_ma_all_trials(self):
        """Run Muscle Analysis for all trials."""
        print(f"\n{'='*60}")
        print(f"Running Muscle Analysis")
        print(f"{'='*60}\n")
        
        for trial in self.trials:
            print(f"\n→ Processing {trial}")
            trial_path = os.path.join(self.target_sim_dir, trial)
            
            try:
                analysis = utils.Analyse(trial_path)
                analysis.replace = self.replace
                
                # Update model
                model_path = self.get_active_model_path()
                analysis.update_model(model_path)
                
                analysis.run_ma()
                print(f"  ✓ MA completed for {trial}")
            except Exception as e:
                print(f"  ✗ MA failed for {trial}: {str(e)}")
    
    def run_so_all_trials(self):
        """Run Static Optimization for all trials."""
        print(f"\n{'='*60}")
        print(f"Running Static Optimization")
        print(f"{'='*60}\n")
        
        for trial in self.trials:
            print(f"\n→ Processing {trial}")
            trial_path = os.path.join(self.target_sim_dir, trial)
            
            try:
                analysis = utils.Analyse(trial_path)
                analysis.replace = self.replace
                
                # Update model
                model_path = self.get_active_model_path()
                analysis.update_model(model_path)
                
                analysis.run_so()
                print(f"  ✓ SO completed for {trial}")
            except Exception as e:
                print(f"  ✗ SO failed for {trial}: {str(e)}")
    
    def run_jra_all_trials(self):
        """Run Joint Reaction Analysis for all trials."""
        print(f"\n{'='*60}")
        print(f"Running Joint Reaction Analysis")
        print(f"{'='*60}\n")
        
        for trial in self.trials:
            print(f"\n→ Processing {trial}")
            trial_path = os.path.join(self.target_sim_dir, trial)
            
            try:
                analysis = utils.Analyse(trial_path)
                analysis.replace = self.replace
                
                # Update model
                model_path = self.get_active_model_path()
                analysis.update_model(model_path)
                
                analysis.run_jra()
                print(f"  ✓ JRA completed for {trial}")
            except Exception as e:
                print(f"  ✗ JRA failed for {trial}: {str(e)}")
    
    def plot_results(self):
        """Plot results for all trials."""
        print(f"\n{'='*60}")
        print(f"Plotting Results")
        print(f"{'='*60}\n")
        
        for trial in self.trials:
            print(f"\n→ Plotting {trial}")
            trial_path = os.path.join(self.target_sim_dir, trial)
            
            try:
                analysis = utils.Analyse(trial_path)
                
                # Plot IK
                try:
                    analysis.plot_ik()
                    print(f"  ✓ IK plots created")
                except Exception as e:
                    print(f"  ⚠ IK plotting failed: {str(e)}")
                
                # Plot ID
                try:
                    analysis.plot_id()
                    print(f"  ✓ ID plots created")
                except Exception as e:
                    print(f"  ⚠ ID plotting failed: {str(e)}")
                
                # Plot SO
                try:
                    analysis.plot_so()
                    print(f"  ✓ SO plots created")
                except Exception as e:
                    print(f"  ⚠ SO plotting failed: {str(e)}")
                
                # Plot JRA
                try:
                    analysis.plot_jra()
                    print(f"  ✓ JRA plots created")
                except Exception as e:
                    print(f"  ⚠ JRA plotting failed: {str(e)}")
                
                # Plot summary
                try:
                    analysis.plot_summary()
                    print(f"  ✓ Summary plots created")
                except Exception as e:
                    print(f"  ⚠ Summary plotting failed: {str(e)}")
                    
            except Exception as e:
                print(f"  ✗ Plotting failed for {trial}: {str(e)}")
    
    def run_full_pipeline(self, skip_setup=False, use_static=True):
        """
        Run the complete pipeline.
        
        Args:
            skip_setup (bool): If True, skip directory creation and file copying.
            use_static (bool): If True, use static trial for model scaling.
        """
        print(f"\n{'#'*60}")
        print(f"# {self.target_subject.upper()} SETUP AND PROCESSING")
        print(f"{'#'*60}\n")
        
        if not skip_setup:
            # Setup phase
            self.create_directory_structure()
            if not self.setup_models(use_static=use_static):
                print("\n✗ Model setup failed.")
                return
            self.copy_trial_data()
        
        # Analysis phase
        self.run_ik_all_trials()
        self.run_id_all_trials()
        self.run_ma_all_trials()
        self.run_so_all_trials()
        self.run_jra_all_trials()
        
        # Visualization phase
        self.plot_results()
        
        print(f"\n{'#'*60}")
        print(f"# PROCESSING COMPLETE")
        print(f"{'#'*60}\n")
        print(f"Results saved to: {self.target_sim_dir}")
        
        # Print model summary
        print(f"\nModel Summary:")
        print(f"  Generic model: {self.generic_model}")
        print(f"  Generic + markerset: {self.generic_model_with_markerset}")
        print(f"  Scaled model: {self.scaled_model}")
        print(f"  Active model: {self.get_active_model_path()}")
        if self.mri_model:
            print(f"  MRI model: {self.mri_model}")


class LernagopalSubjectSetup(GenericSubject):
    """Convenience class for Lernagopal-specific setup (inherits from GenericSubject)."""
    
    def __init__(self):
        super().__init__(
            target_subject='Athlete_03_Lernagopal',
            source_subject='Athlete_03',
            generic_model_path=os.path.join(utils.MODELS_DIR, 'Lernagopal', 'Lernagopal_41_OUF_PowerlifitingMarkers.osim'),
            model_type='Lernagopal',
            source_session='25_03_31',
            target_session='25_03_31',
            static_session='25_03_31',
            trials=['Walking_02', 'Squat_BW_01', 'Squat_35kg_01']
        )


class InteractiveGenericSetup:
    """Interactive interface for selective processing."""
    
    def __init__(self, subject_setup=None):
        self.setup = subject_setup or LernagopalSubjectSetup()
    
    def show_menu(self):
        """Display interactive menu."""
        print(f"\n{'='*60}")
        print(f"{self.setup.target_subject} Setup Menu")
        print(f"{'='*60}")
        print("Model Setup:")
        print("  1. Create directory structure")
        print("  2. Create generic model with markerset")
        print("  3. Create scaled model (with static)")
        print("  4. Create scaled model (without static)")
        print("  5. Copy trial input data")
        print("\nAnalyses:")
        print("  6. Run IK for all trials")
        print("  7. Run ID for all trials")
        print("  8. Run MA for all trials")
        print("  9. Run SO for all trials")
        print("  10. Run JRA for all trials")
        print("\nVisualization:")
        print("  11. Plot results")
        print("\nPipelines:")
        print("  12. Run full pipeline (with static)")
        print("  13. Run full pipeline (without static)")
        print("  14. Run full pipeline (skip setup)")
        print("\n  0. Exit")
        print(f"{'='*60}")
    
    def run(self):
        """Run interactive menu."""
        while True:
            self.show_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.setup.create_directory_structure()
            elif choice == '2':
                self.setup.create_generic_model_with_markerset()
            elif choice == '3':
                self.setup.create_scaled_model_from_static()
            elif choice == '4':
                self.setup.create_scaled_model_generic()
            elif choice == '5':
                self.setup.copy_trial_data()
            elif choice == '6':
                self.setup.run_ik_all_trials()
            elif choice == '7':
                self.setup.run_id_all_trials()
            elif choice == '8':
                self.setup.run_ma_all_trials()
            elif choice == '9':
                self.setup.run_so_all_trials()
            elif choice == '10':
                self.setup.run_jra_all_trials()
            elif choice == '11':
                self.setup.plot_results()
            elif choice == '12':
                self.setup.run_full_pipeline(skip_setup=False, use_static=True)
            elif choice == '13':
                self.setup.run_full_pipeline(skip_setup=False, use_static=False)
            elif choice == '14':
                self.setup.run_full_pipeline(skip_setup=True)
            elif choice == '0':
                print("\nExiting...")
                break
            else:
                print("\n✗ Invalid option. Please try again.")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command-line arguments
        arg = sys.argv[1].lower()
        
        # Allow specifying different subject types
        if '--subject' in sys.argv:
            idx = sys.argv.index('--subject')
            subject_type = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else 'Lernagopal'
        else:
            subject_type = 'Lernagopal'
        
        # Create appropriate setup based on subject type
        if subject_type.lower() == 'lernagopal':
            setup = LernagopalSubjectSetup()
        else:
            # Generic setup - user can customize
            setup = GenericSubject(
                target_subject=f'Athlete_03_{subject_type}',
                model_type=subject_type
            )
        
        # Execute command
        if arg == 'full':
            setup.run_full_pipeline(skip_setup=False, use_static=True)
        elif arg == 'full-no-static':
            setup.run_full_pipeline(skip_setup=False, use_static=False)
        elif arg == 'analysis':
            setup.run_full_pipeline(skip_setup=True)
        elif arg == 'setup':
            setup.create_directory_structure()
            setup.setup_models(use_static=True)
            setup.copy_trial_data()
        elif arg == 'models':
            setup.create_directory_structure()
            setup.setup_models(use_static=True)
        elif arg == 'ik':
            setup.run_ik_all_trials()
        elif arg == 'id':
            setup.run_id_all_trials()
        elif arg == 'ma':
            setup.run_ma_all_trials()
        elif arg == 'so':
            setup.run_so_all_trials()
        elif arg == 'jra':
            setup.run_jra_all_trials()
        elif arg == 'plot':
            setup.plot_results()
        else:
            print("Usage:")
            print("  python setup_generic_subject.py [option] [--subject MODEL_TYPE]")
            print("\nOptions:")
            print("  full            - Run full pipeline (with static scaling)")
            print("  full-no-static  - Run full pipeline (without static scaling)")
            print("  analysis        - Run analysis only (skip setup)")
            print("  setup           - Setup only (dirs + models + data)")
            print("  models          - Create models only")
            print("  ik              - Run IK only")
            print("  id              - Run ID only")
            print("  ma              - Run MA only")
            print("  so              - Run SO only")
            print("  jra             - Run JRA only")
            print("  plot            - Generate plots only")
            print("  (none)          - Interactive menu")
            print("\nSubject Types:")
            print("  --subject Lernagopal  (default)")
            print("  --subject Rajagopal")
            print("  --subject Purzel")
            print("  --subject [custom]")
    else:
        # Interactive mode
        interactive = InteractiveGenericSetup()
        interactive.run()

# END
