#!/usr/bin/env python3
"""
Test script for the model creation pipeline.
"""

import os
import sys
import json
from pathlib import Path

def test_config_loading():
    """Test that the configuration file can be loaded."""
    config_file = "model_creation_config.json"
    
    if not os.path.exists(config_file):
        print(f"Error: Configuration file {config_file} not found.")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("✓ Configuration file loaded successfully")
        return True
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        return False

def test_directory_structure():
    """Test that the pipeline can create directories."""
    print("Testing directory creation...")
    
    # Import the pipeline class
    sys.path.insert(0, '.')
    try:
        from run_model_creation import ModelCreationPipeline
        
        # Create pipeline instance
        pipeline = ModelCreationPipeline()
        
        # Check if directories were created
        expected_dirs = [
            './tps_warping_results',
            './tps_warping_results/after_MRI',
            './tps_warping_results/control',
            './logs',
            './temp'
        ]
        
        for directory in expected_dirs:
            if os.path.exists(directory):
                print(f"✓ Directory {directory} exists")
            else:
                print(f"✗ Directory {directory} does not exist")
                return False
        
        return True
        
    except Exception as e:
        print(f"Error creating pipeline: {e}")
        return False

def test_help_command():
    """Test that the help command works."""
    print("Testing help command...")
    
    result = os.system("python run_model_creation.py --help > /dev/null 2>&1")
    if result == 0:
        print("✓ Help command works")
        return True
    else:
        print("✗ Help command failed")
        return False

def main():
    """Run all tests."""
    print("Running model creation pipeline tests...")
    print("=" * 50)
    
    tests = [
        ("Configuration loading", test_config_loading),
        ("Directory structure", test_directory_structure),
        ("Help command", test_help_command),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"Test '{test_name}' failed!")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1

if __name__ == "__main__":
    sys.exit(main())