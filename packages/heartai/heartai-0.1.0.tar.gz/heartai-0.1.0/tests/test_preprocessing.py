"""
Unit tests for ECG preprocessing functions
"""

import unittest
import numpy as np
from heartai.core.preprocessing import ECGPreprocessor
from heartai.utils.helpers import generate_sample_ecg


class TestECGPreprocessor(unittest.TestCase):
    """Test cases for ECGPreprocessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sampling_rate = 360.0
        self.preprocessor = ECGPreprocessor(sampling_rate=self.sampling_rate)
        
        # Generate test signal
        self.test_signal = generate_sample_ecg(
            duration=10.0,
            sampling_rate=self.sampling_rate,
            heart_rate=75.0,
            noise_level=0.2
        )
    
    def test_initialization(self):
        """Test preprocessor initialization."""
        self.assertEqual(self.preprocessor.sampling_rate, self.sampling_rate)
        self.assertEqual(self.preprocessor.nyquist_freq, self.sampling_rate / 2.0)
    
    def test_highpass_filter(self):
        """Test high-pass filtering."""
        filtered = self.preprocessor.highpass_filter(self.test_signal, cutoff=0.5)
        
        self.assertEqual(len(filtered), len(self.test_signal))
        self.assertIsInstance(filtered, np.ndarray)
    
    def test_lowpass_filter(self):
        """Test low-pass filtering."""
        filtered = self.preprocessor.lowpass_filter(self.test_signal, cutoff=40.0)
        
        self.assertEqual(len(filtered), len(self.test_signal))
        self.assertIsInstance(filtered, np.ndarray)
    
    def test_notch_filter(self):
        """Test notch filtering."""
        filtered = self.preprocessor.notch_filter(self.test_signal, freq=50.0)
        
        self.assertEqual(len(filtered), len(self.test_signal))
        self.assertIsInstance(filtered, np.ndarray)
    
    def test_bandpass_filter(self):
        """Test band-pass filtering."""
        filtered = self.preprocessor.bandpass_filter(self.test_signal, 0.5, 40.0)
        
        self.assertEqual(len(filtered), len(self.test_signal))
        self.assertIsInstance(filtered, np.ndarray)
    
    def test_normalize_zscore(self):
        """Test z-score normalization."""
        normalized = self.preprocessor.normalize(self.test_signal, method='zscore')
        
        self.assertEqual(len(normalized), len(self.test_signal))
        self.assertAlmostEqual(np.mean(normalized), 0.0, places=10)
        self.assertAlmostEqual(np.std(normalized), 1.0, places=10)
    
    def test_normalize_minmax(self):
        """Test min-max normalization."""
        normalized = self.preprocessor.normalize(self.test_signal, method='minmax')
        
        self.assertEqual(len(normalized), len(self.test_signal))
        self.assertAlmostEqual(np.min(normalized), 0.0, places=10)
        self.assertAlmostEqual(np.max(normalized), 1.0, places=10)
    
    def test_normalize_robust(self):
        """Test robust normalization."""
        normalized = self.preprocessor.normalize(self.test_signal, method='robust')
        
        self.assertEqual(len(normalized), len(self.test_signal))
        self.assertIsInstance(normalized, np.ndarray)
    
    def test_remove_artifacts(self):
        """Test artifact removal."""
        # Add some artificial artifacts
        signal_with_artifacts = self.test_signal.copy()
        signal_with_artifacts[100] = 10.0  # Large spike
        signal_with_artifacts[200] = -10.0  # Large negative spike
        
        cleaned = self.preprocessor.remove_artifacts(signal_with_artifacts)
        
        self.assertEqual(len(cleaned), len(signal_with_artifacts))
        self.assertLess(np.abs(cleaned[100]), np.abs(signal_with_artifacts[100]))
        self.assertLess(np.abs(cleaned[200]), np.abs(signal_with_artifacts[200]))
    
    def test_detect_r_peaks(self):
        """Test R-peak detection."""
        # Preprocess signal first
        processed = self.preprocessor.process(self.test_signal)
        peaks = self.preprocessor.detect_r_peaks(processed)
        
        self.assertIsInstance(peaks, np.ndarray)
        self.assertGreater(len(peaks), 0)  # Should detect some peaks
        
        # Check peaks are within signal bounds
        self.assertTrue(np.all(peaks >= 0))
        self.assertTrue(np.all(peaks < len(processed)))
    
    def test_calculate_heart_rate(self):
        """Test heart rate calculation."""
        # Create mock R-peaks
        r_peaks = np.array([360, 720, 1080, 1440, 1800])  # 1-second intervals
        hr_stats = self.preprocessor.calculate_heart_rate(r_peaks)
        
        self.assertIn('mean_hr', hr_stats)
        self.assertIn('std_hr', hr_stats)
        self.assertAlmostEqual(hr_stats['mean_hr'], 60.0, places=1)  # 60 BPM
    
    def test_segment_signal(self):
        """Test signal segmentation."""
        segments = self.preprocessor.segment_signal(
            self.test_signal, 
            segment_length=2.0, 
            overlap=0.5
        )
        
        self.assertIsInstance(segments, np.ndarray)
        self.assertEqual(segments.ndim, 2)
        self.assertEqual(segments.shape[1], int(2.0 * self.sampling_rate))
    
    def test_complete_processing_pipeline(self):
        """Test complete preprocessing pipeline."""
        processed = self.preprocessor.process(self.test_signal)
        
        self.assertEqual(len(processed), len(self.test_signal))
        self.assertIsInstance(processed, np.ndarray)
        
        # Check normalization worked (should be roughly zero mean, unit variance)
        self.assertLess(np.abs(np.mean(processed)), 0.1)
        self.assertLess(np.abs(np.std(processed) - 1.0), 0.1)


if __name__ == '__main__':
    unittest.main()
