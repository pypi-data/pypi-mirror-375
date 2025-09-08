"""
Machine learning models for arrhythmia detection
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from pathlib import Path
import logging
from typing import Tuple, Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class ArrhythmiaDetector:
    """
    Lightweight machine learning model for arrhythmia detection.
    
    Uses feature extraction from ECG signals and a Random Forest classifier
    for binary classification (Normal vs Arrhythmia).
    """
    
    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        """
        Initialize arrhythmia detector.
        
        Args:
            model_path: Path to pre-trained model file
        """
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.feature_names = [
            'mean_amplitude', 'std_amplitude', 'skewness', 'kurtosis',
            'mean_rr_interval', 'std_rr_interval', 'rmssd', 'pnn50',
            'heart_rate_mean', 'heart_rate_std', 'signal_energy',
            'zero_crossings', 'peak_count', 'amplitude_range'
        ]
        
        if model_path:
            self.load_model(model_path)
        else:
            self._initialize_default_model()
    
    def _initialize_default_model(self):
        """Initialize default pre-trained model with synthetic parameters."""
        # Create a simple Random Forest model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        # Initialize scaler
        self.scaler = StandardScaler()
        
        # Create synthetic training data for demonstration
        # In a real implementation, this would be trained on actual ECG data
        self._create_synthetic_model()
    
    def _create_synthetic_model(self):
        """Create a synthetic pre-trained model for demonstration."""
        # Generate synthetic feature data
        np.random.seed(42)
        n_samples = 1000
        
        # Normal rhythm features (class 0)
        normal_features = np.random.normal(0, 1, (n_samples // 2, len(self.feature_names)))
        normal_labels = np.zeros(n_samples // 2)
        
        # Arrhythmia features (class 1) - slightly different distribution
        arrhythmia_features = np.random.normal(0.5, 1.5, (n_samples // 2, len(self.feature_names)))
        arrhythmia_labels = np.ones(n_samples // 2)
        
        # Combine data
        X = np.vstack([normal_features, arrhythmia_features])
        y = np.hstack([normal_labels, arrhythmia_labels])
        
        # Train the model
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Fit scaler and model
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
        
        self.is_trained = True
        logger.info("Initialized synthetic pre-trained model for demonstration")
    
    def extract_features(self, ecg_signal: np.ndarray, sampling_rate: float = 360.0) -> np.ndarray:
        """
        Extract features from ECG signal for classification.
        
        Args:
            ecg_signal: Preprocessed ECG signal
            sampling_rate: Sampling rate in Hz
            
        Returns:
            Feature vector
        """
        features = []
        
        # Statistical features
        features.append(np.mean(ecg_signal))  # mean_amplitude
        features.append(np.std(ecg_signal))   # std_amplitude
        features.append(self._calculate_skewness(ecg_signal))  # skewness
        features.append(self._calculate_kurtosis(ecg_signal))  # kurtosis
        
        # Heart rate variability features
        r_peaks = self._detect_r_peaks_simple(ecg_signal, sampling_rate)
        if len(r_peaks) > 1:
            rr_intervals = np.diff(r_peaks) / sampling_rate
            features.append(np.mean(rr_intervals))  # mean_rr_interval
            features.append(np.std(rr_intervals))   # std_rr_interval
            features.append(self._calculate_rmssd(rr_intervals))  # rmssd
            features.append(self._calculate_pnn50(rr_intervals))  # pnn50
            features.append(60.0 / np.mean(rr_intervals))  # heart_rate_mean
            features.append(np.std(60.0 / rr_intervals))   # heart_rate_std
        else:
            # Default values if no R-peaks detected
            features.extend([1.0, 0.1, 0.05, 0.0, 75.0, 5.0])
        
        # Signal characteristics
        features.append(np.sum(ecg_signal ** 2))  # signal_energy
        features.append(self._count_zero_crossings(ecg_signal))  # zero_crossings
        features.append(len(r_peaks))  # peak_count
        features.append(np.max(ecg_signal) - np.min(ecg_signal))  # amplitude_range
        
        return np.array(features)
    
    def predict(self, ecg_signal: np.ndarray, sampling_rate: float = 360.0) -> Tuple[int, float]:
        """
        Predict arrhythmia from ECG signal.
        
        Args:
            ecg_signal: Preprocessed ECG signal
            sampling_rate: Sampling rate in Hz
            
        Returns:
            Tuple of (prediction, confidence)
        """
        if not self.is_trained:
            raise ValueError("Model is not trained. Load a pre-trained model or train the model first.")
        
        # Extract features
        features = self.extract_features(ecg_signal, sampling_rate)
        features = features.reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Make prediction
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = np.max(probabilities)
        
        return int(prediction), float(confidence)
    
    def train(self, X: np.ndarray, y: np.ndarray, 
              test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        """
        Train the arrhythmia detection model.
        
        Args:
            X: Feature matrix
            y: Labels (0: normal, 1: arrhythmia)
            test_size: Fraction of data for testing
            random_state: Random seed
            
        Returns:
            Training results dictionary
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate model
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        # Predictions for detailed metrics
        y_pred = self.model.predict(X_test_scaled)
        
        results = {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': dict(zip(self.feature_names, self.model.feature_importances_))
        }
        
        logger.info(f"Model trained successfully. Test accuracy: {test_score:.3f}")
        return results
    
    def save_model(self, model_path: Union[str, Path]):
        """
        Save trained model to file.
        
        Args:
            model_path: Path to save model
        """
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, model_path)
        logger.info(f"Model saved to {model_path}")
    
    def load_model(self, model_path: Union[str, Path]):
        """
        Load pre-trained model from file.
        
        Args:
            model_path: Path to model file
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        model_data = joblib.load(model_path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {model_path}")
    
    # Helper methods for feature extraction
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of the data."""
        mean_val = np.mean(data)
        std_val = np.std(data)
        if std_val == 0:
            return 0.0
        return np.mean(((data - mean_val) / std_val) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of the data."""
        mean_val = np.mean(data)
        std_val = np.std(data)
        if std_val == 0:
            return 0.0
        return np.mean(((data - mean_val) / std_val) ** 4) - 3
    
    def _detect_r_peaks_simple(self, ecg_signal: np.ndarray, sampling_rate: float) -> np.ndarray:
        """Simple R-peak detection using local maxima."""
        from scipy.signal import find_peaks
        
        # Find peaks with minimum distance constraint
        min_distance = int(0.6 * sampling_rate)  # Minimum 0.6s between peaks
        peaks, _ = find_peaks(
            ecg_signal,
            distance=min_distance,
            prominence=np.std(ecg_signal) * 0.3
        )
        return peaks
    
    def _calculate_rmssd(self, rr_intervals: np.ndarray) -> float:
        """Calculate RMSSD (Root Mean Square of Successive Differences)."""
        if len(rr_intervals) < 2:
            return 0.0
        diff_rr = np.diff(rr_intervals)
        return np.sqrt(np.mean(diff_rr ** 2))
    
    def _calculate_pnn50(self, rr_intervals: np.ndarray) -> float:
        """Calculate pNN50 (percentage of successive RR intervals that differ by more than 50ms)."""
        if len(rr_intervals) < 2:
            return 0.0
        diff_rr = np.abs(np.diff(rr_intervals))
        return np.sum(diff_rr > 0.05) / len(diff_rr) * 100  # 50ms = 0.05s
    
    def _count_zero_crossings(self, signal: np.ndarray) -> int:
        """Count zero crossings in the signal."""
        return np.sum(np.diff(np.sign(signal)) != 0)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance from trained model.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_trained or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        return dict(zip(self.feature_names, self.model.feature_importances_))
