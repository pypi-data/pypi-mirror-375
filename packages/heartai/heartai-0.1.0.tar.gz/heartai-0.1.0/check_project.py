#!/usr/bin/env python3
"""
Project structure and code quality checker for HeartAI
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """Check if all required files exist."""
    print("📁 Checking project structure...")
    
    required_files = [
        "heartai/__init__.py",
        "heartai/core/__init__.py", 
        "heartai/core/analyzer.py",
        "heartai/core/preprocessing.py",
        "heartai/core/models.py",
        "heartai/utils/__init__.py",
        "heartai/utils/helpers.py",
        "heartai/utils/validators.py",
        "heartai/visualization/__init__.py",
        "heartai/visualization/plotter.py",
        "heartai/cli.py",
        "setup.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "INSTALL.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    else:
        print("\n✅ All required files present")
        return True

def check_code_syntax():
    """Check Python syntax in all files."""
    print("\n🔍 Checking Python syntax...")
    
    python_files = []
    for root, dirs, files in os.walk("heartai"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    # Add other Python files
    python_files.extend(["setup.py", "test_project.py"])
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path}")
        except SyntaxError as e:
            print(f"❌ {file_path}: {e}")
            syntax_errors.append((file_path, str(e)))
        except Exception as e:
            print(f"⚠️  {file_path}: {e}")
    
    if syntax_errors:
        print(f"\n❌ Syntax errors found in {len(syntax_errors)} files")
        return False
    else:
        print(f"\n✅ All {len(python_files)} Python files have valid syntax")
        return True

def check_imports_structure():
    """Check import structure without actually importing."""
    print("\n📦 Checking import structure...")
    
    # Check __init__.py files have proper exports
    init_files = {
        "heartai/__init__.py": ["ECGAnalyzer", "ECGPreprocessor", "ArrhythmiaDetector", "ECGPlotter"],
        "heartai/core/__init__.py": ["ECGAnalyzer", "ECGPreprocessor", "ArrhythmiaDetector"],
        "heartai/utils/__init__.py": ["validate_ecg_data", "generate_sample_ecg"],
        "heartai/visualization/__init__.py": ["ECGPlotter"]
    }
    
    all_good = True
    for file_path, expected_exports in init_files.items():
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            for export in expected_exports:
                if export in content:
                    print(f"✅ {file_path} exports {export}")
                else:
                    print(f"❌ {file_path} missing export {export}")
                    all_good = False
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            all_good = False
    
    return all_good

def check_setup_configuration():
    """Check setup.py configuration."""
    print("\n⚙️ Checking setup.py configuration...")
    
    try:
        with open("setup.py", 'r') as f:
            content = f.read()
        
        required_fields = [
            "name=",
            "version=",
            "author=",
            "description=",
            "url=",
            "packages=",
            "install_requires=",
            "entry_points="
        ]
        
        all_present = True
        for field in required_fields:
            if field in content:
                print(f"✅ {field} configured")
            else:
                print(f"❌ {field} missing")
                all_present = False
        
        # Check GitHub URL
        if "github.com/ahmetxhero/AhmetX-HeartAi" in content:
            print("✅ Correct GitHub URL configured")
        else:
            print("❌ GitHub URL not properly configured")
            all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"❌ Error checking setup.py: {e}")
        return False

def generate_installation_instructions():
    """Generate installation instructions."""
    print("\n📋 Installation Instructions:")
    print("=" * 50)
    
    instructions = """
# HeartAI Installation Guide

## Method 1: Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv heartai_env
source heartai_env/bin/activate  # On macOS/Linux
# heartai_env\\Scripts\\activate  # On Windows

# Install dependencies
pip install numpy scipy pandas scikit-learn matplotlib seaborn click rich pydantic joblib

# Install HeartAI
pip install -e .

# Test installation
heartai info
```

## Method 2: User Installation
```bash
# Install dependencies for user only
pip install --user numpy scipy pandas scikit-learn matplotlib seaborn click rich pydantic joblib

# Install HeartAI for user only
pip install --user -e .
```

## Method 3: System Installation (if allowed)
```bash
# Install dependencies system-wide
pip install --break-system-packages numpy scipy pandas scikit-learn matplotlib seaborn click rich pydantic joblib

# Install HeartAI
pip install --break-system-packages -e .
```

## Verify Installation
```bash
python3 -c "import heartai; print('HeartAI installed successfully!')"
heartai info
python examples/basic_usage.py
```
"""
    
    print(instructions)
    
    # Save to file
    with open("QUICK_INSTALL.md", "w") as f:
        f.write(instructions)
    print("💾 Saved installation instructions to QUICK_INSTALL.md")

def main():
    """Run all checks."""
    print("🫀 HeartAI Project Health Check")
    print("=" * 40)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Python Syntax", check_code_syntax),
        ("Import Structure", check_imports_structure),
        ("Setup Configuration", check_setup_configuration)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        success = check_func()
        results.append((check_name, success))
    
    # Summary
    print(f"\n{'='*40}")
    print("📊 Health Check Results:")
    print("=" * 40)
    
    passed = 0
    for check_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{check_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 Project structure is perfect!")
        print("The HeartAI library is properly structured and ready for use.")
        print("\n📝 Next steps:")
        print("1. Install dependencies (see instructions below)")
        print("2. Test the library with examples")
        print("3. Run unit tests")
    else:
        print(f"\n⚠️  {len(results) - passed} check(s) failed.")
        print("Please fix the issues above before proceeding.")
    
    # Always generate installation instructions
    generate_installation_instructions()

if __name__ == "__main__":
    main()
