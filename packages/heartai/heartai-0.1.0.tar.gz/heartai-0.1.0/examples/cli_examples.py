#!/usr/bin/env python3
"""
CLI usage examples for HeartAI library
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a CLI command and display results."""
    print(f"\n{description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print("Output:")
            print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Demonstrate CLI usage examples."""
    print("🫀 HeartAI CLI Usage Examples")
    print("=" * 40)
    
    # Check if heartai is installed
    print("First, install HeartAI in development mode:")
    print("pip install -e .")
    
    # CLI Examples
    examples = [
        {
            "cmd": "heartai info",
            "desc": "1. Display library information"
        },
        {
            "cmd": "heartai generate --duration 10 --heart-rate 75 --output sample_normal.csv --plot normal_ecg.png",
            "desc": "2. Generate normal ECG sample"
        },
        {
            "cmd": "heartai generate --duration 10 --heart-rate 95 --arrhythmia --output sample_arrhythmia.csv --plot arrhythmia_ecg.png",
            "desc": "3. Generate arrhythmia ECG sample"
        },
        {
            "cmd": "heartai predict sample_normal.csv --output normal_results.json --plot normal_prediction.png",
            "desc": "4. Predict on normal ECG"
        },
        {
            "cmd": "heartai predict sample_arrhythmia.csv --output arrhythmia_results.json --plot arrhythmia_prediction.png",
            "desc": "5. Predict on arrhythmia ECG"
        },
        {
            "cmd": "heartai analyze sample_normal.csv --output ./analysis_output",
            "desc": "6. Comprehensive analysis of normal ECG"
        },
        {
            "cmd": "heartai create-dataset --normal-samples 20 --arrhythmia-samples 20 --output-dir ./sample_dataset",
            "desc": "7. Create sample dataset"
        }
    ]
    
    print("\nCLI Command Examples:")
    print("Note: Run these commands in your terminal after installing HeartAI")
    print("=" * 60)
    
    for example in examples:
        print(f"\n{example['desc']}")
        print(f"$ {example['cmd']}")
    
    # Create a script file for easy execution
    script_content = """#!/bin/bash
# HeartAI CLI Examples Script

echo "🫀 Running HeartAI CLI Examples"
echo "=============================="

# Install HeartAI in development mode
echo "Installing HeartAI..."
pip install -e .

# Run examples
echo -e "\\n1. Display library information"
heartai info

echo -e "\\n2. Generate normal ECG sample"
heartai generate --duration 10 --heart-rate 75 --output sample_normal.csv --plot normal_ecg.png

echo -e "\\n3. Generate arrhythmia ECG sample"  
heartai generate --duration 10 --heart-rate 95 --arrhythmia --output sample_arrhythmia.csv --plot arrhythmia_ecg.png

echo -e "\\n4. Predict on normal ECG"
heartai predict sample_normal.csv --output normal_results.json --plot normal_prediction.png

echo -e "\\n5. Predict on arrhythmia ECG"
heartai predict sample_arrhythmia.csv --output arrhythmia_results.json --plot arrhythmia_prediction.png

echo -e "\\n6. Comprehensive analysis"
heartai analyze sample_normal.csv --output ./analysis_output

echo -e "\\n7. Create sample dataset"
heartai create-dataset --normal-samples 10 --arrhythmia-samples 10 --output-dir ./sample_dataset

echo -e "\\n✅ All CLI examples completed!"
echo "Check the generated files in the current directory."
"""
    
    with open('run_cli_examples.sh', 'w') as f:
        f.write(script_content)
    
    # Make script executable
    import os
    os.chmod('run_cli_examples.sh', 0o755)
    
    print(f"\n📝 Created executable script: run_cli_examples.sh")
    print("To run all examples at once, execute: ./run_cli_examples.sh")
    
    print(f"\n💡 Tips:")
    print("- Use --help with any command to see all options")
    print("- Example: heartai predict --help")
    print("- Use --verbose flag for detailed output")
    print("- Example: heartai --verbose predict sample.csv")

if __name__ == "__main__":
    main()
