#!/usr/bin/env python3
"""
Example usage of the model creation pipeline.
"""

import os
import sys
import json

def main():
    """Demonstrate the model creation pipeline usage."""
    print("Model Creation Pipeline - Example Usage")
    print("=" * 50)
    
    # 1. Show available configuration
    print("\n1. Current Configuration:")
    with open('model_creation_config.json', 'r') as f:
        config = json.load(f)
    
    print(f"   Participant ID: {config['model_creation_config']['participant_id']}")
    print(f"   Processing Steps: {len(config['model_creation_config']['processing_steps'])}")
    
    # 2. Show available steps
    print("\n2. Available Processing Steps:")
    for i, step in enumerate(config['model_creation_config']['processing_steps'], 1):
        print(f"   {i}. {step}")
    
    # 3. Show usage examples
    print("\n3. Usage Examples:")
    print("   # Run complete pipeline:")
    print("   python run_model_creation.py")
    print()
    print("   # Install requirements only:")
    print("   python run_model_creation.py --steps install_requirements")
    print()
    print("   # Run specific steps:")
    print("   python run_model_creation.py --steps morph_bones_from_mri,tps_processing")
    print()
    print("   # Use custom configuration:")
    print("   python run_model_creation.py --config custom_config.json")
    
    # 4. Show configuration customization
    print("\n4. Configuration Customization:")
    print("   Edit 'model_creation_config.json' to:")
    print("   - Change input/output paths")
    print("   - Modify processing parameters")
    print("   - Add/remove processing steps")
    print("   - Configure requirements")
    
    # 5. Show directory structure
    print("\n5. Generated Directory Structure:")
    directories = [
        "./tps_warping_results/",
        "./tps_warping_results/after_MRI/",
        "./tps_warping_results/control/",
        "./logs/",
        "./temp/"
    ]
    for directory in directories:
        exists = "✓" if os.path.exists(directory) else "✗"
        print(f"   {exists} {directory}")
    
    print("\n" + "=" * 50)
    print("For more information, see README_PIPELINE.md")

if __name__ == "__main__":
    main()