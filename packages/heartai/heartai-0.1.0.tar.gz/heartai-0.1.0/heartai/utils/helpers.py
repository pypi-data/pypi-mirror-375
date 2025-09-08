"""
Helper utilities for HeartAI
"""

import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def generate_sample_ecg(duration: float = 10.0, sampling_rate: float = 360.0, 
                       heart_rate: float = 75.0, noise_level: float = 0.1,
                       arrhythmia: bool = False) -> np.ndarray:
    """
    Generate synthetic ECG signal for testing and demonstration.
    
    Args:
        duration: Duration in seconds
        sampling_rate: Sampling rate in Hz
        heart_rate: Heart rate in BPM
        noise_level: Noise level (0-1)
        arrhythmia: Whether to include arrhythmia patterns
        
    Returns:
        Synthetic ECG signal
    """
    n_samples = int(duration * sampling_rate)
    t = np.linspace(0, duration, n_samples)
    
    # Calculate heart period
    heart_period = 60.0 / heart_rate
    
    # Generate basic ECG waveform
    ecg_signal = np.zeros(n_samples)
    
    # Generate heartbeats
    beat_times = np.arange(0, duration, heart_period)
    
    for beat_time in beat_times:
        beat_start = int(beat_time * sampling_rate)
        
        if arrhythmia and np.random.random() < 0.3:  # 30% chance of irregular beat
            # Create irregular beat pattern
            beat_signal = _generate_irregular_beat(sampling_rate)
        else:
            # Create normal beat pattern
            beat_signal = _generate_normal_beat(sampling_rate)
        
        # Add beat to signal
        beat_end = min(beat_start + len(beat_signal), n_samples)
        signal_end = min(len(beat_signal), beat_end - beat_start)
        ecg_signal[beat_start:beat_end] += beat_signal[:signal_end]
    
    # Add noise
    if noise_level > 0:
        noise = np.random.normal(0, noise_level, n_samples)
        ecg_signal += noise
    
    logger.info(f"Generated synthetic ECG: {duration}s, {heart_rate} BPM, "
               f"arrhythmia={arrhythmia}, noise={noise_level}")
    
    return ecg_signal


def _generate_normal_beat(sampling_rate: float) -> np.ndarray:
    """Generate a normal ECG beat (PQRST complex)."""
    # Beat duration: ~0.8 seconds
    beat_duration = 0.8
    n_samples = int(beat_duration * sampling_rate)
    t = np.linspace(0, beat_duration, n_samples)
    
    # P wave (atrial depolarization)
    p_wave = 0.1 * np.exp(-((t - 0.1) / 0.05) ** 2)
    
    # QRS complex (ventricular depolarization)
    q_wave = -0.05 * np.exp(-((t - 0.35) / 0.02) ** 2)
    r_wave = 1.0 * np.exp(-((t - 0.4) / 0.02) ** 2)
    s_wave = -0.1 * np.exp(-((t - 0.45) / 0.02) ** 2)
    
    # T wave (ventricular repolarization)
    t_wave = 0.3 * np.exp(-((t - 0.65) / 0.08) ** 2)
    
    # Combine all components
    beat = p_wave + q_wave + r_wave + s_wave + t_wave
    
    return beat


def _generate_irregular_beat(sampling_rate: float) -> np.ndarray:
    """Generate an irregular ECG beat (arrhythmia pattern)."""
    # Irregular beat with modified timing and amplitude
    beat_duration = 0.9  # Slightly longer
    n_samples = int(beat_duration * sampling_rate)
    t = np.linspace(0, beat_duration, n_samples)
    
    # Modified P wave
    p_wave = 0.08 * np.exp(-((t - 0.12) / 0.06) ** 2)
    
    # Modified QRS complex (wider, different amplitude)
    q_wave = -0.08 * np.exp(-((t - 0.38) / 0.025) ** 2)
    r_wave = 0.7 * np.exp(-((t - 0.42) / 0.025) ** 2)  # Lower R wave
    s_wave = -0.15 * np.exp(-((t - 0.48) / 0.025) ** 2)
    
    # Modified T wave (inverted or biphasic)
    t_wave = -0.2 * np.exp(-((t - 0.7) / 0.1) ** 2)
    
    # Add some extra noise/irregularity
    irregularity = 0.05 * np.random.normal(0, 1, n_samples)
    
    beat = p_wave + q_wave + r_wave + s_wave + t_wave + irregularity
    
    return beat


def calculate_signal_quality(ecg_signal: np.ndarray, sampling_rate: float = 360.0) -> dict:
    """
    Calculate signal quality metrics for ECG signal.
    
    Args:
        ecg_signal: ECG signal
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Dictionary with quality metrics
    """
    # Signal-to-noise ratio estimate
    signal_power = np.var(ecg_signal)
    
    # Estimate noise using high-frequency components
    from scipy.signal import butter, filtfilt
    nyquist = sampling_rate / 2
    high_cutoff = min(50, nyquist * 0.9)
    b, a = butter(4, high_cutoff / nyquist, btype='high')
    high_freq_signal = filtfilt(b, a, ecg_signal)
    noise_power = np.var(high_freq_signal)
    
    snr = 10 * np.log10(signal_power / max(noise_power, 1e-10))
    
    # Baseline wander (low-frequency drift)
    low_cutoff = 0.5
    b, a = butter(4, low_cutoff / nyquist, btype='low')
    baseline = filtfilt(b, a, ecg_signal)
    baseline_wander = np.std(baseline)
    
    # Saturation check
    signal_range = np.max(ecg_signal) - np.min(ecg_signal)
    saturation_ratio = np.sum(np.abs(ecg_signal) > 0.95 * np.max(np.abs(ecg_signal))) / len(ecg_signal)
    
    quality_metrics = {
        'snr_db': float(snr),
        'baseline_wander': float(baseline_wander),
        'signal_range': float(signal_range),
        'saturation_ratio': float(saturation_ratio),
        'quality_score': _calculate_quality_score(snr, baseline_wander, saturation_ratio)
    }
    
    return quality_metrics


def _calculate_quality_score(snr: float, baseline_wander: float, saturation_ratio: float) -> float:
    """Calculate overall quality score (0-100)."""
    # SNR component (0-40 points)
    snr_score = min(40, max(0, snr * 2))
    
    # Baseline wander component (0-30 points)
    baseline_score = max(0, 30 - baseline_wander * 10)
    
    # Saturation component (0-30 points)
    saturation_score = max(0, 30 - saturation_ratio * 100)
    
    total_score = snr_score + baseline_score + saturation_score
    return float(total_score)


def create_sample_dataset(n_normal: int = 100, n_arrhythmia: int = 100, 
                         duration: float = 10.0, sampling_rate: float = 360.0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create a sample dataset for training/testing.
    
    Args:
        n_normal: Number of normal ECG samples
        n_arrhythmia: Number of arrhythmia ECG samples
        duration: Duration of each sample in seconds
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Tuple of (signals, labels)
    """
    signals = []
    labels = []
    
    # Generate normal signals
    for i in range(n_normal):
        hr = np.random.normal(75, 10)  # Random heart rate around 75 BPM
        hr = max(50, min(120, hr))  # Clamp to reasonable range
        
        signal = generate_sample_ecg(
            duration=duration,
            sampling_rate=sampling_rate,
            heart_rate=hr,
            noise_level=np.random.uniform(0.05, 0.15),
            arrhythmia=False
        )
        signals.append(signal)
        labels.append(0)
    
    # Generate arrhythmia signals
    for i in range(n_arrhythmia):
        hr = np.random.normal(85, 15)  # Slightly higher heart rate
        hr = max(40, min(150, hr))  # Wider range for arrhythmia
        
        signal = generate_sample_ecg(
            duration=duration,
            sampling_rate=sampling_rate,
            heart_rate=hr,
            noise_level=np.random.uniform(0.1, 0.25),
            arrhythmia=True
        )
        signals.append(signal)
        labels.append(1)
    
    logger.info(f"Created sample dataset: {n_normal} normal + {n_arrhythmia} arrhythmia samples")
    
    return np.array(signals), np.array(labels)
