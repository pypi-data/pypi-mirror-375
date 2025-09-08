#!/usr/bin/env python3
"""
Basic usage example for HeartAI library
"""

import numpy as np
from heartai import ECGAnalyzer
from heartai.utils.helpers import generate_sample_ecg
from heartai.visualization.plotter import ECGPlotter

def main():
    """Demonstrate basic HeartAI usage."""
    print("🫀 HeartAI Basic Usage Example")
    print("=" * 40)
    
    # 1. Generate sample ECG data
    print("\n1. Generating sample ECG data...")
    ecg_signal = generate_sample_ecg(
        duration=10.0,
        sampling_rate=360.0,
        heart_rate=75.0,
        noise_level=0.1,
        arrhythmia=False
    )
    print(f"Generated ECG signal: {len(ecg_signal)} samples")
    
    # 2. Save sample data to CSV for demonstration
    import pandas as pd
    time_axis = np.arange(len(ecg_signal)) / 360.0
    df = pd.DataFrame({'time': time_axis, 'ecg': ecg_signal})
    df.to_csv('sample_ecg.csv', index=False)
    print("Saved sample data to 'sample_ecg.csv'")
    
    # 3. Initialize ECG analyzer
    print("\n2. Initializing ECG analyzer...")
    analyzer = ECGAnalyzer(data_path='sample_ecg.csv', sampling_rate=360.0)
    
    # 4. Preprocess the signal
    print("\n3. Preprocessing ECG signal...")
    processed_signal = analyzer.preprocess()
    print(f"Processed signal shape: {processed_signal.shape}")
    
    # 5. Make prediction
    print("\n4. Making arrhythmia prediction...")
    prediction_result = analyzer.predict()
    
    print(f"Status: {prediction_result['status']}")
    print(f"Confidence: {prediction_result['confidence']:.1%}")
    print(f"Risk Level: {prediction_result['risk_level']}")
    
    # 6. Create visualizations
    print("\n5. Creating visualizations...")
    plotter = ECGPlotter()
    
    # Plot original ECG
    fig1 = plotter.plot_ecg(processed_signal, sampling_rate=360.0, 
                           title="Sample ECG Signal")
    fig1.savefig('ecg_plot.png', dpi=150, bbox_inches='tight')
    print("Saved ECG plot to 'ecg_plot.png'")
    
    # Plot prediction result
    fig2 = plotter.plot_prediction_result(processed_signal, prediction_result, 
                                         sampling_rate=360.0)
    fig2.savefig('prediction_result.png', dpi=150, bbox_inches='tight')
    print("Saved prediction plot to 'prediction_result.png'")
    
    # 7. Get complete analysis summary
    print("\n6. Getting analysis summary...")
    summary = analyzer.get_summary()
    print(f"Analysis complete! Data loaded: {summary['data_loaded']}")
    print(f"Data preprocessed: {summary['data_preprocessed']}")
    print(f"Prediction made: {summary['prediction_made']}")
    
    print("\n✅ Basic usage example completed successfully!")
    print("Generated files:")
    print("  - sample_ecg.csv: Sample ECG data")
    print("  - ecg_plot.png: ECG signal visualization")
    print("  - prediction_result.png: Prediction results")


if __name__ == "__main__":
    main()
