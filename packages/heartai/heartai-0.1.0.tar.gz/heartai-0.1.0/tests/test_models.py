"""
Unit tests for ArrhythmiaDetector model
"""

import unittest
import numpy as np
import tempfile
from pathlib import Path

from heartai.core.models import ArrhythmiaDetector
from heartai.utils.helpers import generate_sample_ecg, create_sample_dataset


class TestArrhythmiaDetector(unittest.TestCase):
    """Test cases for ArrhythmiaDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = ArrhythmiaDetector()
        self.sampling_rate = 360.0
        
        # Generate test signals
        self.normal_signal = generate_sample_ecg(
            duration=8.0,
            sampling_rate=self.sampling_rate,
            heart_rate=75.0,
            arrhythmia=False
        )
        
        self.arrhythmia_signal = generate_sample_ecg(
            duration=8.0,
            sampling_rate=self.sampling_rate,
            heart_rate=85.0,
            arrhythmia=True
        )
    
    def test_initialization(self):
        """Test detector initialization."""
        self.assertTrue(self.detector.is_trained)
        self.assertIsNotNone(self.detector.model)
        self.assertIsNotNone(self.detector.scaler)
        self.assertEqual(len(self.detector.feature_names), 14)
    
    def test_extract_features(self):
        """Test feature extraction."""
        features = self.detector.extract_features(self.normal_signal, self.sampling_rate)
        
        self.assertEqual(len(features), len(self.detector.feature_names))
        self.assertIsInstance(features, np.ndarray)
        self.assertTrue(np.all(np.isfinite(features)))
    
    def test_predict_normal(self):
        """Test prediction on normal signal."""
        prediction, confidence = self.detector.predict(self.normal_signal, self.sampling_rate)
        
        self.assertIn(prediction, [0, 1])
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_predict_arrhythmia(self):
        """Test prediction on arrhythmia signal."""
        prediction, confidence = self.detector.predict(self.arrhythmia_signal, self.sampling_rate)
        
        self.assertIn(prediction, [0, 1])
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_train_model(self):
        """Test model training."""
        # Create small training dataset
        signals, labels = create_sample_dataset(
            n_normal=20,
            n_arrhythmia=20,
            duration=5.0,
            sampling_rate=self.sampling_rate
        )
        
        # Extract features
        features = []
        for signal in signals:
            feature_vector = self.detector.extract_features(signal, self.sampling_rate)
            features.append(feature_vector)
        
        features = np.array(features)
        
        # Train model
        results = self.detector.train(features, labels, test_size=0.3)
        
        self.assertIn('train_accuracy', results)
        self.assertIn('test_accuracy', results)
        self.assertGreaterEqual(results['train_accuracy'], 0.0)
        self.assertLessEqual(results['train_accuracy'], 1.0)
        self.assertTrue(self.detector.is_trained)
    
    def test_save_load_model(self):
        """Test model saving and loading."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save model
            self.detector.save_model(temp_path)
            self.assertTrue(Path(temp_path).exists())
            
            # Create new detector and load model
            new_detector = ArrhythmiaDetector()
            new_detector.load_model(temp_path)
            
            self.assertTrue(new_detector.is_trained)
            self.assertEqual(new_detector.feature_names, self.detector.feature_names)
            
        finally:
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
    
    def test_get_feature_importance(self):
        """Test feature importance extraction."""
        importance = self.detector.get_feature_importance()
        
        self.assertIsInstance(importance, dict)
        self.assertEqual(len(importance), len(self.detector.feature_names))
        
        # Check all values are numeric and non-negative
        for feature, score in importance.items():
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0.0)
    
    def test_helper_methods(self):
        """Test helper methods for feature extraction."""
        test_data = np.array([1, 2, 3, 4, 5, 4, 3, 2, 1])
        
        # Test skewness calculation
        skewness = self.detector._calculate_skewness(test_data)
        self.assertIsInstance(skewness, float)
        
        # Test kurtosis calculation
        kurtosis = self.detector._calculate_kurtosis(test_data)
        self.assertIsInstance(kurtosis, float)
        
        # Test zero crossings
        zero_crossings = self.detector._count_zero_crossings(test_data - np.mean(test_data))
        self.assertIsInstance(zero_crossings, (int, np.integer))
    
    def test_rr_interval_calculations(self):
        """Test RR interval related calculations."""
        # Mock RR intervals (in seconds)
        rr_intervals = np.array([0.8, 0.85, 0.82, 0.78, 0.83, 0.81])
        
        # Test RMSSD
        rmssd = self.detector._calculate_rmssd(rr_intervals)
        self.assertIsInstance(rmssd, float)
        self.assertGreaterEqual(rmssd, 0.0)
        
        # Test pNN50
        pnn50 = self.detector._calculate_pnn50(rr_intervals)
        self.assertIsInstance(pnn50, float)
        self.assertGreaterEqual(pnn50, 0.0)
        self.assertLessEqual(pnn50, 100.0)


if __name__ == '__main__':
    unittest.main()
