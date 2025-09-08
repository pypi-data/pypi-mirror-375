"""
ECG signal preprocessing functions for noise filtering, normalization, and segmentation
"""

import numpy as np
from scipy import signal
from scipy.signal import butter, filtfilt, find_peaks
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ECGPreprocessor:
    """
    ECG signal preprocessing pipeline for noise filtering and normalization.
    """
    
    def __init__(self, sampling_rate: float = 360.0):
        """
        Initialize ECG preprocessor.
        
        Args:
            sampling_rate: Sampling rate of ECG signal in Hz
        """
        self.sampling_rate = sampling_rate
        self.nyquist_freq = sampling_rate / 2.0
        
        # Default filter parameters
        self.default_params = {
            'highpass_cutoff': 0.5,  # Hz - remove baseline drift
            'lowpass_cutoff': 40.0,  # Hz - remove high-frequency noise
            'notch_freq': 50.0,      # Hz - power line interference (50Hz for EU, 60Hz for US)
            'filter_order': 4,
            'normalize': True,
            'remove_artifacts': True
        }
    
    def process(self, ecg_signal: np.ndarray, **kwargs) -> np.ndarray:
        """
        Complete preprocessing pipeline.
        
        Args:
            ecg_signal: Raw ECG signal
            **kwargs: Preprocessing parameters
            
        Returns:
            Preprocessed ECG signal
        """
        # Merge default parameters with user parameters
        params = {**self.default_params, **kwargs}
        
        processed_signal = ecg_signal.copy()
        
        logger.debug(f"Starting preprocessing with params: {params}")
        
        # Step 1: Remove baseline drift (high-pass filter)
        if params.get('highpass_cutoff'):
            processed_signal = self.highpass_filter(
                processed_signal, 
                cutoff=params['highpass_cutoff'],
                order=params['filter_order']
            )
        
        # Step 2: Remove high-frequency noise (low-pass filter)
        if params.get('lowpass_cutoff'):
            processed_signal = self.lowpass_filter(
                processed_signal,
                cutoff=params['lowpass_cutoff'], 
                order=params['filter_order']
            )
        
        # Step 3: Remove power line interference (notch filter)
        if params.get('notch_freq'):
            processed_signal = self.notch_filter(
                processed_signal,
                freq=params['notch_freq'],
                quality_factor=30
            )
        
        # Step 4: Remove artifacts
        if params.get('remove_artifacts'):
            processed_signal = self.remove_artifacts(processed_signal)
        
        # Step 5: Normalize signal
        if params.get('normalize'):
            processed_signal = self.normalize(processed_signal)
        
        logger.debug("Preprocessing pipeline completed")
        return processed_signal
    
    def highpass_filter(self, signal_data: np.ndarray, cutoff: float, order: int = 4) -> np.ndarray:
        """
        Apply high-pass Butterworth filter to remove baseline drift.
        
        Args:
            signal_data: Input signal
            cutoff: Cutoff frequency in Hz
            order: Filter order
            
        Returns:
            Filtered signal
        """
        if cutoff >= self.nyquist_freq:
            logger.warning(f"Cutoff frequency {cutoff} >= Nyquist frequency {self.nyquist_freq}")
            return signal_data
        
        normalized_cutoff = cutoff / self.nyquist_freq
        b, a = butter(order, normalized_cutoff, btype='high', analog=False)
        filtered_signal = filtfilt(b, a, signal_data)
        
        logger.debug(f"Applied high-pass filter: cutoff={cutoff}Hz, order={order}")
        return filtered_signal
    
    def lowpass_filter(self, signal_data: np.ndarray, cutoff: float, order: int = 4) -> np.ndarray:
        """
        Apply low-pass Butterworth filter to remove high-frequency noise.
        
        Args:
            signal_data: Input signal
            cutoff: Cutoff frequency in Hz
            order: Filter order
            
        Returns:
            Filtered signal
        """
        if cutoff >= self.nyquist_freq:
            logger.warning(f"Cutoff frequency {cutoff} >= Nyquist frequency {self.nyquist_freq}")
            cutoff = self.nyquist_freq * 0.95
        
        normalized_cutoff = cutoff / self.nyquist_freq
        b, a = butter(order, normalized_cutoff, btype='low', analog=False)
        filtered_signal = filtfilt(b, a, signal_data)
        
        logger.debug(f"Applied low-pass filter: cutoff={cutoff}Hz, order={order}")
        return filtered_signal
    
    def notch_filter(self, signal_data: np.ndarray, freq: float, quality_factor: float = 30) -> np.ndarray:
        """
        Apply notch filter to remove power line interference.
        
        Args:
            signal_data: Input signal
            freq: Frequency to remove (50Hz or 60Hz)
            quality_factor: Quality factor of the notch filter
            
        Returns:
            Filtered signal
        """
        if freq >= self.nyquist_freq:
            logger.warning(f"Notch frequency {freq} >= Nyquist frequency {self.nyquist_freq}")
            return signal_data
        
        # Design notch filter
        b, a = signal.iirnotch(freq, quality_factor, fs=self.sampling_rate)
        filtered_signal = filtfilt(b, a, signal_data)
        
        logger.debug(f"Applied notch filter: freq={freq}Hz, Q={quality_factor}")
        return filtered_signal
    
    def bandpass_filter(self, signal_data: np.ndarray, 
                       low_cutoff: float, high_cutoff: float, order: int = 4) -> np.ndarray:
        """
        Apply band-pass filter.
        
        Args:
            signal_data: Input signal
            low_cutoff: Low cutoff frequency in Hz
            high_cutoff: High cutoff frequency in Hz
            order: Filter order
            
        Returns:
            Filtered signal
        """
        if high_cutoff >= self.nyquist_freq:
            high_cutoff = self.nyquist_freq * 0.95
        
        low_norm = low_cutoff / self.nyquist_freq
        high_norm = high_cutoff / self.nyquist_freq
        
        b, a = butter(order, [low_norm, high_norm], btype='band', analog=False)
        filtered_signal = filtfilt(b, a, signal_data)
        
        logger.debug(f"Applied band-pass filter: {low_cutoff}-{high_cutoff}Hz, order={order}")
        return filtered_signal
    
    def remove_artifacts(self, signal_data: np.ndarray, threshold_factor: float = 3.0) -> np.ndarray:
        """
        Remove artifacts using statistical outlier detection.
        
        Args:
            signal_data: Input signal
            threshold_factor: Factor for outlier detection (standard deviations)
            
        Returns:
            Signal with artifacts removed
        """
        # Calculate statistics
        mean_val = np.mean(signal_data)
        std_val = np.std(signal_data)
        threshold = threshold_factor * std_val
        
        # Identify outliers
        outliers = np.abs(signal_data - mean_val) > threshold
        
        if np.any(outliers):
            # Replace outliers with interpolated values
            clean_signal = signal_data.copy()
            outlier_indices = np.where(outliers)[0]
            
            for idx in outlier_indices:
                # Simple linear interpolation between neighboring points
                if idx > 0 and idx < len(signal_data) - 1:
                    clean_signal[idx] = (signal_data[idx-1] + signal_data[idx+1]) / 2
                elif idx == 0:
                    clean_signal[idx] = signal_data[idx+1]
                else:
                    clean_signal[idx] = signal_data[idx-1]
            
            logger.debug(f"Removed {np.sum(outliers)} artifacts")
            return clean_signal
        
        return signal_data
    
    def normalize(self, signal_data: np.ndarray, method: str = 'zscore') -> np.ndarray:
        """
        Normalize ECG signal.
        
        Args:
            signal_data: Input signal
            method: Normalization method ('zscore', 'minmax', 'robust')
            
        Returns:
            Normalized signal
        """
        if method == 'zscore':
            # Z-score normalization
            mean_val = np.mean(signal_data)
            std_val = np.std(signal_data)
            if std_val > 0:
                normalized = (signal_data - mean_val) / std_val
            else:
                normalized = signal_data - mean_val
                
        elif method == 'minmax':
            # Min-max normalization to [0, 1]
            min_val = np.min(signal_data)
            max_val = np.max(signal_data)
            if max_val > min_val:
                normalized = (signal_data - min_val) / (max_val - min_val)
            else:
                normalized = np.zeros_like(signal_data)
                
        elif method == 'robust':
            # Robust normalization using median and MAD
            median_val = np.median(signal_data)
            mad = np.median(np.abs(signal_data - median_val))
            if mad > 0:
                normalized = (signal_data - median_val) / mad
            else:
                normalized = signal_data - median_val
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        logger.debug(f"Applied {method} normalization")
        return normalized
    
    def segment_signal(self, signal_data: np.ndarray, 
                      segment_length: float = 10.0, 
                      overlap: float = 0.5) -> np.ndarray:
        """
        Segment ECG signal into fixed-length windows.
        
        Args:
            signal_data: Input signal
            segment_length: Length of each segment in seconds
            overlap: Overlap between segments (0-1)
            
        Returns:
            Array of signal segments
        """
        segment_samples = int(segment_length * self.sampling_rate)
        step_size = int(segment_samples * (1 - overlap))
        
        segments = []
        for start in range(0, len(signal_data) - segment_samples + 1, step_size):
            segment = signal_data[start:start + segment_samples]
            segments.append(segment)
        
        logger.debug(f"Created {len(segments)} segments of {segment_length}s each")
        return np.array(segments)
    
    def detect_r_peaks(self, signal_data: np.ndarray, 
                      min_distance: Optional[int] = None) -> np.ndarray:
        """
        Detect R-peaks in ECG signal.
        
        Args:
            signal_data: Preprocessed ECG signal
            min_distance: Minimum distance between peaks in samples
            
        Returns:
            Array of R-peak indices
        """
        if min_distance is None:
            # Default: minimum 0.6 seconds between R-peaks (100 BPM max)
            min_distance = int(0.6 * self.sampling_rate)
        
        # Find peaks with minimum distance constraint
        peaks, properties = find_peaks(
            signal_data,
            distance=min_distance,
            prominence=np.std(signal_data) * 0.5
        )
        
        logger.debug(f"Detected {len(peaks)} R-peaks")
        return peaks
    
    def calculate_heart_rate(self, r_peaks: np.ndarray) -> Dict[str, float]:
        """
        Calculate heart rate statistics from R-peaks.
        
        Args:
            r_peaks: Array of R-peak indices
            
        Returns:
            Dictionary with heart rate statistics
        """
        if len(r_peaks) < 2:
            return {'mean_hr': 0, 'std_hr': 0, 'min_hr': 0, 'max_hr': 0}
        
        # Calculate RR intervals in seconds
        rr_intervals = np.diff(r_peaks) / self.sampling_rate
        
        # Convert to heart rate (beats per minute)
        heart_rates = 60.0 / rr_intervals
        
        hr_stats = {
            'mean_hr': float(np.mean(heart_rates)),
            'std_hr': float(np.std(heart_rates)),
            'min_hr': float(np.min(heart_rates)),
            'max_hr': float(np.max(heart_rates)),
            'rr_intervals': rr_intervals.tolist()
        }
        
        logger.debug(f"Heart rate: {hr_stats['mean_hr']:.1f} ± {hr_stats['std_hr']:.1f} BPM")
        return hr_stats
