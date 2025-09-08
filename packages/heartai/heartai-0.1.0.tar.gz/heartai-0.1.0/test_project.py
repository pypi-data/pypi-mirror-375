#!/usr/bin/env python3
"""
Simple test script to verify HeartAI project functionality
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported."""
    print("🧪 Testing HeartAI imports...")
    
    try:
        # Test core imports
        import numpy as np
        print("✅ NumPy imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import scipy
        print("✅ SciPy imported successfully")
        
        import sklearn
        print("✅ Scikit-learn imported successfully")
        
        import matplotlib
        print("✅ Matplotlib imported successfully")
        
        # Test HeartAI imports
        import heartai
        print("✅ HeartAI main package imported")
        
        from heartai import ECGAnalyzer
        print("✅ ECGAnalyzer imported")
        
        from heartai.utils.helpers import generate_sample_ecg
        print("✅ Helper functions imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    print("\n🔬 Testing basic functionality...")
    
    try:
        from heartai.utils.helpers import generate_sample_ecg
        from heartai import ECGAnalyzer
        import tempfile
        import pandas as pd
        import numpy as np
        
        # Generate sample ECG
        print("Generating sample ECG...")
        ecg_signal = generate_sample_ecg(duration=5.0, sampling_rate=360.0)
        print(f"✅ Generated ECG signal: {len(ecg_signal)} samples")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            time_axis = np.arange(len(ecg_signal)) / 360.0
            df = pd.DataFrame({'time': time_axis, 'ecg': ecg_signal})
            df.to_csv(f.name, index=False)
            temp_file = f.name
        
        # Test ECGAnalyzer
        print("Testing ECGAnalyzer...")
        analyzer = ECGAnalyzer(data_path=temp_file, sampling_rate=360.0)
        print("✅ ECGAnalyzer initialized")
        
        # Test preprocessing
        processed = analyzer.preprocess()
        print(f"✅ Signal preprocessed: {len(processed)} samples")
        
        # Test prediction
        result = analyzer.predict()
        print(f"✅ Prediction made: {result['status']} (confidence: {result['confidence']:.1%})")
        
        # Clean up
        os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_availability():
    """Test if CLI is available."""
    print("\n🖥️  Testing CLI availability...")
    
    try:
        from heartai.cli import main
        print("✅ CLI module imported successfully")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🫀 HeartAI Project Test Suite")
    print("=" * 40)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Project path: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Functionality Test", test_basic_functionality),
        ("CLI Test", test_cli_availability)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print(f"\n{'='*40}")
    print("📊 Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! HeartAI project is working correctly.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install package: pip install -e .")
        print("3. Try CLI: heartai info")
        print("4. Run examples: python examples/basic_usage.py")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check dependencies.")
        print("\nTo fix issues:")
        print("1. Install missing dependencies")
        print("2. Check Python version (requires 3.8+)")

if __name__ == "__main__":
    main()
