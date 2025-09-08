#!/usr/bin/env python3
"""
Advanced analysis example for HeartAI library
"""

import numpy as np
import pandas as pd
from pathlib import Path
from heartai import ECGAnalyzer, ECGPreprocessor, ArrhythmiaDetector, ECGPlotter
from heartai.utils.helpers import generate_sample_ecg, create_sample_dataset

def demonstrate_preprocessing():
    """Demonstrate advanced preprocessing features."""
    print("\n🔧 Advanced Preprocessing Demo")
    print("-" * 40)
    
    # Generate noisy ECG signal
    ecg_signal = generate_sample_ecg(
        duration=15.0,
        sampling_rate=360.0,
        heart_rate=85.0,
        noise_level=0.3,  # High noise
        arrhythmia=True
    )
    
    # Initialize preprocessor
    preprocessor = ECGPreprocessor(sampling_rate=360.0)
    
    # Apply different preprocessing steps
    print("Original signal stats:")
    print(f"  Mean: {np.mean(ecg_signal):.3f}")
    print(f"  Std: {np.std(ecg_signal):.3f}")
    print(f"  Range: {np.max(ecg_signal) - np.min(ecg_signal):.3f}")
    
    # Step-by-step preprocessing
    filtered_signal = preprocessor.bandpass_filter(ecg_signal, 0.5, 40.0)
    clean_signal = preprocessor.remove_artifacts(filtered_signal)
    normalized_signal = preprocessor.normalize(clean_signal, method='zscore')
    
    print("\nAfter preprocessing:")
    print(f"  Mean: {np.mean(normalized_signal):.3f}")
    print(f"  Std: {np.std(normalized_signal):.3f}")
    print(f"  Range: {np.max(normalized_signal) - np.min(normalized_signal):.3f}")
    
    # Detect R-peaks and calculate heart rate
    r_peaks = preprocessor.detect_r_peaks(normalized_signal)
    hr_stats = preprocessor.calculate_heart_rate(r_peaks)
    
    print(f"\nHeart Rate Analysis:")
    print(f"  R-peaks detected: {len(r_peaks)}")
    print(f"  Mean HR: {hr_stats['mean_hr']:.1f} BPM")
    print(f"  HR variability: {hr_stats['std_hr']:.1f} BPM")
    
    # Create visualization
    plotter = ECGPlotter()
    fig = plotter.plot_with_peaks(normalized_signal, r_peaks, 
                                 sampling_rate=360.0, 
                                 title="ECG with R-peak Detection")
    fig.savefig('advanced_preprocessing.png', dpi=150, bbox_inches='tight')
    print("Saved preprocessing visualization to 'advanced_preprocessing.png'")
    
    return normalized_signal, r_peaks, hr_stats

def demonstrate_model_training():
    """Demonstrate custom model training."""
    print("\n🤖 Model Training Demo")
    print("-" * 40)
    
    # Create training dataset
    print("Creating training dataset...")
    signals, labels = create_sample_dataset(
        n_normal=50,
        n_arrhythmia=50,
        duration=8.0,
        sampling_rate=360.0
    )
    
    # Extract features for all signals
    detector = ArrhythmiaDetector()
    features = []
    
    print("Extracting features...")
    for signal in signals:
        feature_vector = detector.extract_features(signal, sampling_rate=360.0)
        features.append(feature_vector)
    
    features = np.array(features)
    print(f"Feature matrix shape: {features.shape}")
    
    # Train model
    print("Training model...")
    training_results = detector.train(features, labels, test_size=0.3)
    
    print(f"Training Results:")
    print(f"  Train Accuracy: {training_results['train_accuracy']:.3f}")
    print(f"  Test Accuracy: {training_results['test_accuracy']:.3f}")
    
    # Show feature importance
    importance = detector.get_feature_importance()
    print(f"\nTop 5 Important Features:")
    sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for feature, score in sorted_features[:5]:
        print(f"  {feature}: {score:.3f}")
    
    # Save trained model
    detector.save_model('trained_arrhythmia_model.pkl')
    print("Saved trained model to 'trained_arrhythmia_model.pkl'")
    
    return detector, training_results

def demonstrate_comprehensive_analysis():
    """Demonstrate comprehensive ECG analysis."""
    print("\n📊 Comprehensive Analysis Demo")
    print("-" * 40)
    
    # Generate test signals with different characteristics
    test_cases = [
        {"name": "Normal Rhythm", "hr": 72, "arrhythmia": False, "noise": 0.1},
        {"name": "Tachycardia", "hr": 110, "arrhythmia": False, "noise": 0.15},
        {"name": "Bradycardia", "hr": 45, "arrhythmia": False, "noise": 0.1},
        {"name": "Arrhythmia", "hr": 85, "arrhythmia": True, "noise": 0.2}
    ]
    
    results = []
    plotter = ECGPlotter()
    
    for i, case in enumerate(test_cases):
        print(f"\nAnalyzing: {case['name']}")
        
        # Generate signal
        signal = generate_sample_ecg(
            duration=12.0,
            sampling_rate=360.0,
            heart_rate=case['hr'],
            noise_level=case['noise'],
            arrhythmia=case['arrhythmia']
        )
        
        # Save to temporary file
        temp_file = f"temp_ecg_{i}.csv"
        time_axis = np.arange(len(signal)) / 360.0
        df = pd.DataFrame({'time': time_axis, 'ecg': signal})
        df.to_csv(temp_file, index=False)
        
        # Analyze with ECGAnalyzer
        analyzer = ECGAnalyzer(data_path=temp_file, sampling_rate=360.0)
        analysis_result = analyzer.analyze()
        
        # Store results
        analysis_result['case_name'] = case['name']
        analysis_result['true_arrhythmia'] = case['arrhythmia']
        results.append(analysis_result)
        
        print(f"  Status: {analysis_result['status']}")
        print(f"  Confidence: {analysis_result['confidence']:.1%}")
        print(f"  True Label: {'Arrhythmia' if case['arrhythmia'] else 'Normal'}")
        
        # Create individual plot
        fig = plotter.plot_prediction_result(
            analyzer.processed_data, 
            analysis_result, 
            sampling_rate=360.0
        )
        fig.savefig(f"analysis_{case['name'].lower().replace(' ', '_')}.png", 
                   dpi=150, bbox_inches='tight')
        
        # Clean up
        Path(temp_file).unlink()
    
    # Create summary comparison
    print(f"\n📈 Analysis Summary:")
    correct_predictions = 0
    for result in results:
        predicted_arrhythmia = result['prediction'] == 1
        true_arrhythmia = result['true_arrhythmia']
        correct = predicted_arrhythmia == true_arrhythmia
        if correct:
            correct_predictions += 1
        
        print(f"  {result['case_name']}: "
              f"Predicted={'Arrhythmia' if predicted_arrhythmia else 'Normal'}, "
              f"Actual={'Arrhythmia' if true_arrhythmia else 'Normal'}, "
              f"{'✓' if correct else '✗'}")
    
    accuracy = correct_predictions / len(results)
    print(f"\nOverall Accuracy: {accuracy:.1%} ({correct_predictions}/{len(results)})")
    
    return results

def demonstrate_visualization_features():
    """Demonstrate advanced visualization features."""
    print("\n📈 Advanced Visualization Demo")
    print("-" * 40)
    
    # Generate ECG with arrhythmia
    ecg_signal = generate_sample_ecg(
        duration=20.0,
        sampling_rate=360.0,
        heart_rate=78.0,
        noise_level=0.15,
        arrhythmia=True
    )
    
    # Preprocess signal
    preprocessor = ECGPreprocessor(sampling_rate=360.0)
    processed_signal = preprocessor.process(ecg_signal)
    
    # Detect R-peaks for HRV analysis
    r_peaks = preprocessor.detect_r_peaks(processed_signal)
    rr_intervals = np.diff(r_peaks) / 360.0
    
    plotter = ECGPlotter()
    
    # 1. Basic ECG plot with time range
    fig1 = plotter.plot_ecg(processed_signal, sampling_rate=360.0,
                           title="ECG Signal - First 10 seconds",
                           time_range=(0, 10))
    fig1.savefig('ecg_time_range.png', dpi=150, bbox_inches='tight')
    
    # 2. Raw vs processed comparison
    fig2 = plotter.plot_comparison(ecg_signal, processed_signal, 
                                  sampling_rate=360.0,
                                  title="Signal Processing Comparison")
    fig2.savefig('signal_comparison.png', dpi=150, bbox_inches='tight')
    
    # 3. Heart rate variability analysis
    if len(rr_intervals) > 10:
        fig3 = plotter.plot_heart_rate_variability(rr_intervals,
                                                   title="Heart Rate Variability Analysis")
        fig3.savefig('hrv_analysis.png', dpi=150, bbox_inches='tight')
        print("Created HRV analysis plot")
    
    # 4. Frequency domain analysis
    fig4 = plotter.plot_frequency_analysis(processed_signal, sampling_rate=360.0,
                                          title="ECG Frequency Domain Analysis")
    fig4.savefig('frequency_analysis.png', dpi=150, bbox_inches='tight')
    
    print("Created advanced visualization plots:")
    print("  - ecg_time_range.png: Time-limited ECG view")
    print("  - signal_comparison.png: Raw vs processed comparison")
    print("  - hrv_analysis.png: Heart rate variability")
    print("  - frequency_analysis.png: Frequency domain analysis")

def main():
    """Run all advanced analysis demonstrations."""
    print("🫀 HeartAI Advanced Analysis Examples")
    print("=" * 50)
    
    try:
        # Run all demonstrations
        demonstrate_preprocessing()
        demonstrate_model_training()
        demonstrate_comprehensive_analysis()
        demonstrate_visualization_features()
        
        print("\n✅ All advanced analysis examples completed successfully!")
        print("\nGenerated files:")
        print("  - advanced_preprocessing.png")
        print("  - trained_arrhythmia_model.pkl")
        print("  - analysis_*.png (multiple analysis results)")
        print("  - ecg_time_range.png")
        print("  - signal_comparison.png")
        print("  - hrv_analysis.png")
        print("  - frequency_analysis.png")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
