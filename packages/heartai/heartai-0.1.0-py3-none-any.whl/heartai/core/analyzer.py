"""
Core ECG analyzer class for signal processing and arrhythmia detection
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union, Optional, Dict, Any, Tuple
import logging

from .preprocessing import ECGPreprocessor
from .models import ArrhythmiaDetector
from ..utils.validators import validate_ecg_data

logger = logging.getLogger(__name__)


class ECGAnalyzer:
    """
    Main class for ECG signal analysis and arrhythmia detection.
    
    This class provides a high-level interface for loading ECG data,
    preprocessing signals, and making predictions about arrhythmia risk.
    """
    
    def __init__(self, data_path: Optional[Union[str, Path]] = None, 
                 sampling_rate: float = 360.0):
        """
        Initialize ECG analyzer.
        
        Args:
            data_path: Path to ECG data file (CSV, TXT, or NPY)
            sampling_rate: Sampling rate of ECG signal in Hz (default: 360 Hz)
        """
        self.data_path = Path(data_path) if data_path else None
        self.sampling_rate = sampling_rate
        
        # Initialize components
        self.preprocessor = ECGPreprocessor(sampling_rate=sampling_rate)
        self.detector = ArrhythmiaDetector()
        
        # Data storage
        self.raw_data = None
        self.processed_data = None
        self.metadata = {}
        self.prediction_results = None
        
        # Load data if path provided
        if self.data_path:
            self.load_data(self.data_path)
    
    def load_data(self, data_path: Union[str, Path]) -> None:
        """
        Load ECG data from file.
        
        Args:
            data_path: Path to ECG data file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        data_path = Path(data_path)
        self.data_path = data_path
        
        if not data_path.exists():
            raise FileNotFoundError(f"ECG data file not found: {data_path}")
        
        logger.info(f"Loading ECG data from: {data_path}")
        
        try:
            if data_path.suffix.lower() == '.csv':
                df = pd.read_csv(data_path)
                # Assume first column is ECG signal or look for common column names
                if 'ecg' in df.columns.str.lower():
                    self.raw_data = df['ecg'].values
                elif 'signal' in df.columns.str.lower():
                    self.raw_data = df['signal'].values
                else:
                    self.raw_data = df.iloc[:, 0].values
                    
            elif data_path.suffix.lower() == '.txt':
                # Try to load as space/comma separated values
                try:
                    self.raw_data = np.loadtxt(data_path)
                except ValueError:
                    # If that fails, try pandas
                    df = pd.read_csv(data_path, sep=None, engine='python')
                    self.raw_data = df.iloc[:, 0].values
                    
            elif data_path.suffix.lower() == '.npy':
                self.raw_data = np.load(data_path)
                
            else:
                raise ValueError(f"Unsupported file format: {data_path.suffix}")
            
            # Validate loaded data
            self.raw_data = validate_ecg_data(self.raw_data)
            
            # Store metadata
            self.metadata.update({
                'file_path': str(data_path),
                'data_length': len(self.raw_data),
                'duration_seconds': len(self.raw_data) / self.sampling_rate,
                'sampling_rate': self.sampling_rate
            })
            
            logger.info(f"Successfully loaded ECG data: {len(self.raw_data)} samples, "
                       f"{self.metadata['duration_seconds']:.2f} seconds")
                       
        except Exception as e:
            logger.error(f"Error loading ECG data: {e}")
            raise
    
    def preprocess(self, **kwargs) -> np.ndarray:
        """
        Preprocess the loaded ECG signal.
        
        Args:
            **kwargs: Additional preprocessing parameters
            
        Returns:
            Preprocessed ECG signal
            
        Raises:
            ValueError: If no data is loaded
        """
        if self.raw_data is None:
            raise ValueError("No ECG data loaded. Use load_data() first.")
        
        logger.info("Preprocessing ECG signal...")
        
        # Apply preprocessing pipeline
        self.processed_data = self.preprocessor.process(self.raw_data, **kwargs)
        
        # Update metadata
        self.metadata.update({
            'preprocessed': True,
            'preprocessing_params': kwargs
        })
        
        logger.info("ECG preprocessing completed")
        return self.processed_data
    
    def predict(self, confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Predict arrhythmia risk from processed ECG signal.
        
        Args:
            confidence_threshold: Minimum confidence for positive prediction
            
        Returns:
            Dictionary containing prediction results
            
        Raises:
            ValueError: If no processed data available
        """
        if self.processed_data is None:
            logger.warning("No preprocessed data found. Running preprocessing...")
            self.preprocess()
        
        logger.info("Predicting arrhythmia risk...")
        
        # Make prediction
        prediction, confidence = self.detector.predict(self.processed_data)
        
        # Interpret results
        risk_level = "High" if prediction == 1 and confidence >= confidence_threshold else "Low"
        status = "Potential arrhythmia detected" if prediction == 1 else "Normal rhythm"
        
        self.prediction_results = {
            'prediction': int(prediction),
            'confidence': float(confidence),
            'risk_level': risk_level,
            'status': status,
            'threshold': confidence_threshold,
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        logger.info(f"Prediction completed: {status} (confidence: {confidence:.1%})")
        return self.prediction_results
    
    def analyze(self, **preprocessing_kwargs) -> Dict[str, Any]:
        """
        Complete analysis pipeline: preprocess and predict.
        
        Args:
            **preprocessing_kwargs: Parameters for preprocessing
            
        Returns:
            Complete analysis results
        """
        if self.raw_data is None:
            raise ValueError("No ECG data loaded. Use load_data() first.")
        
        # Run complete pipeline
        self.preprocess(**preprocessing_kwargs)
        results = self.predict()
        
        # Add metadata to results
        results['metadata'] = self.metadata.copy()
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of current analysis state.
        
        Returns:
            Summary dictionary
        """
        summary = {
            'data_loaded': self.raw_data is not None,
            'data_preprocessed': self.processed_data is not None,
            'prediction_made': self.prediction_results is not None,
            'metadata': self.metadata.copy()
        }
        
        if self.prediction_results:
            summary['latest_prediction'] = self.prediction_results.copy()
        
        return summary
    
    def reset(self) -> None:
        """Reset analyzer state, keeping only configuration."""
        self.raw_data = None
        self.processed_data = None
        self.prediction_results = None
        self.metadata.clear()
        logger.info("ECG analyzer state reset")
    
    def __repr__(self) -> str:
        status = []
        if self.raw_data is not None:
            status.append(f"data_length={len(self.raw_data)}")
        if self.processed_data is not None:
            status.append("preprocessed=True")
        if self.prediction_results is not None:
            status.append(f"prediction={self.prediction_results['status']}")
        
        status_str = ", ".join(status) if status else "no_data"
        return f"ECGAnalyzer(sampling_rate={self.sampling_rate}, {status_str})"
