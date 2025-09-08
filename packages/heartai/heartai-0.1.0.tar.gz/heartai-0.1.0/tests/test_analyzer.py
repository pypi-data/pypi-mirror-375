"""
Unit tests for ECGAnalyzer class
"""

import unittest
import numpy as np
import tempfile
import pandas as pd
from pathlib import Path

from heartai.core.analyzer import ECGAnalyzer
from heartai.utils.helpers import generate_sample_ecg


class TestECGAnalyzer(unittest.TestCase):
    """Test cases for ECGAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sampling_rate = 360.0
        self.duration = 5.0
        
        # Generate test ECG signal
        self.test_signal = generate_sample_ecg(
            duration=self.duration,
            sampling_rate=self.sampling_rate,
            heart_rate=75.0,
            noise_level=0.1,
            arrhythmia=False
        )
        
        # Create temporary CSV file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        time_axis = np.arange(len(self.test_signal)) / self.sampling_rate
        df = pd.DataFrame({'time': time_axis, 'ecg': self.test_signal})
        df.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_initialization_with_file(self):
        """Test ECGAnalyzer initialization with file."""
        analyzer = ECGAnalyzer(data_path=self.temp_file.name, sampling_rate=self.sampling_rate)
        
        self.assertIsNotNone(analyzer.raw_data)
        self.assertEqual(len(analyzer.raw_data), len(self.test_signal))
        self.assertEqual(analyzer.sampling_rate, self.sampling_rate)
    
    def test_initialization_without_file(self):
        """Test ECGAnalyzer initialization without file."""
        analyzer = ECGAnalyzer(sampling_rate=self.sampling_rate)
        
        self.assertIsNone(analyzer.raw_data)
        self.assertEqual(analyzer.sampling_rate, self.sampling_rate)
    
    def test_load_data_csv(self):
        """Test loading CSV data."""
        analyzer = ECGAnalyzer(sampling_rate=self.sampling_rate)
        analyzer.load_data(self.temp_file.name)
        
        self.assertIsNotNone(analyzer.raw_data)
        self.assertEqual(len(analyzer.raw_data), len(self.test_signal))
    
    def test_load_data_nonexistent_file(self):
        """Test loading non-existent file raises error."""
        analyzer = ECGAnalyzer(sampling_rate=self.sampling_rate)
        
        with self.assertRaises(FileNotFoundError):
            analyzer.load_data("nonexistent_file.csv")
    
    def test_preprocess(self):
        """Test ECG preprocessing."""
        analyzer = ECGAnalyzer(data_path=self.temp_file.name, sampling_rate=self.sampling_rate)
        processed_signal = analyzer.preprocess()
        
        self.assertIsNotNone(processed_signal)
        self.assertEqual(len(processed_signal), len(analyzer.raw_data))
        self.assertIsNotNone(analyzer.processed_data)
    
    def test_preprocess_without_data(self):
        """Test preprocessing without loaded data raises error."""
        analyzer = ECGAnalyzer(sampling_rate=self.sampling_rate)
        
        with self.assertRaises(ValueError):
            analyzer.preprocess()
    
    def test_predict(self):
        """Test arrhythmia prediction."""
        analyzer = ECGAnalyzer(data_path=self.temp_file.name, sampling_rate=self.sampling_rate)
        analyzer.preprocess()
        result = analyzer.predict()
        
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('status', result)
        self.assertIn('risk_level', result)
        
        self.assertIn(result['prediction'], [0, 1])
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
    
    def test_predict_without_preprocessing(self):
        """Test prediction automatically runs preprocessing."""
        analyzer = ECGAnalyzer(data_path=self.temp_file.name, sampling_rate=self.sampling_rate)
        result = analyzer.predict()
        
        self.assertIsNotNone(analyzer.processed_data)
        self.assertIn('prediction', result)
    
    def test_analyze_complete_pipeline(self):
        """Test complete analysis pipeline."""
        analyzer = ECGAnalyzer(data_path=self.temp_file.name, sampling_rate=self.sampling_rate)
        result = analyzer.analyze()
        
        self.assertIn('prediction', result)
        self.assertIn('confidence', result)
        self.assertIn('metadata', result)
        self.assertIsNotNone(analyzer.processed_data)
    
    def test_get_summary(self):
        """Test getting analysis summary."""
        analyzer = ECGAnalyzer(data_path=self.temp_file.name, sampling_rate=self.sampling_rate)
        analyzer.analyze()
        summary = analyzer.get_summary()
        
        self.assertTrue(summary['data_loaded'])
        self.assertTrue(summary['data_preprocessed'])
        self.assertTrue(summary['prediction_made'])
        self.assertIn('metadata', summary)
        self.assertIn('latest_prediction', summary)
    
    def test_reset(self):
        """Test analyzer reset functionality."""
        analyzer = ECGAnalyzer(data_path=self.temp_file.name, sampling_rate=self.sampling_rate)
        analyzer.analyze()
        
        # Verify data is loaded and processed
        self.assertIsNotNone(analyzer.raw_data)
        self.assertIsNotNone(analyzer.processed_data)
        
        # Reset analyzer
        analyzer.reset()
        
        # Verify data is cleared
        self.assertIsNone(analyzer.raw_data)
        self.assertIsNone(analyzer.processed_data)
        self.assertIsNone(analyzer.prediction_results)
        self.assertEqual(len(analyzer.metadata), 0)
    
    def test_repr(self):
        """Test string representation."""
        analyzer = ECGAnalyzer(sampling_rate=self.sampling_rate)
        repr_str = repr(analyzer)
        
        self.assertIn("ECGAnalyzer", repr_str)
        self.assertIn(str(self.sampling_rate), repr_str)


if __name__ == '__main__':
    unittest.main()
