"""
Data validation utilities for ECG signals
"""

import numpy as np
from typing import Union, Optional
import logging

logger = logging.getLogger(__name__)


def validate_ecg_data(data: Union[np.ndarray, list]) -> np.ndarray:
    """
    Validate and clean ECG signal data.
    
    Args:
        data: ECG signal data
        
    Returns:
        Validated numpy array
        
    Raises:
        ValueError: If data is invalid
    """
    # Convert to numpy array
    if isinstance(data, list):
        data = np.array(data)
    elif not isinstance(data, np.ndarray):
        raise ValueError(f"ECG data must be numpy array or list, got {type(data)}")
    
    # Check if data is empty
    if data.size == 0:
        raise ValueError("ECG data is empty")
    
    # Ensure 1D array
    if data.ndim > 1:
        if data.shape[1] == 1:
            data = data.flatten()
        else:
            logger.warning(f"Multi-channel ECG data detected. Using first channel only.")
            data = data[:, 0]
    
    # Check for minimum length (at least 1 second at 360 Hz)
    if len(data) < 360:
        logger.warning(f"ECG signal is very short: {len(data)} samples")
    
    # Check for NaN or infinite values
    if np.any(np.isnan(data)):
        logger.warning("ECG data contains NaN values. Interpolating...")
        data = _interpolate_nan_values(data)
    
    if np.any(np.isinf(data)):
        logger.warning("ECG data contains infinite values. Clipping...")
        data = np.clip(data, -1e6, 1e6)
    
    # Check data type
    if not np.issubdtype(data.dtype, np.number):
        raise ValueError(f"ECG data must be numeric, got {data.dtype}")
    
    # Convert to float64 for processing
    data = data.astype(np.float64)
    
    logger.debug(f"Validated ECG data: {len(data)} samples, range: [{np.min(data):.3f}, {np.max(data):.3f}]")
    return data


def _interpolate_nan_values(data: np.ndarray) -> np.ndarray:
    """
    Interpolate NaN values in ECG signal.
    
    Args:
        data: ECG signal with potential NaN values
        
    Returns:
        ECG signal with NaN values interpolated
    """
    nan_mask = np.isnan(data)
    if not np.any(nan_mask):
        return data
    
    # Find valid indices
    valid_indices = np.where(~nan_mask)[0]
    nan_indices = np.where(nan_mask)[0]
    
    if len(valid_indices) == 0:
        raise ValueError("All ECG data values are NaN")
    
    # Interpolate NaN values
    interpolated_data = data.copy()
    interpolated_data[nan_indices] = np.interp(nan_indices, valid_indices, data[valid_indices])
    
    return interpolated_data


def validate_sampling_rate(sampling_rate: float) -> float:
    """
    Validate sampling rate parameter.
    
    Args:
        sampling_rate: Sampling rate in Hz
        
    Returns:
        Validated sampling rate
        
    Raises:
        ValueError: If sampling rate is invalid
    """
    if not isinstance(sampling_rate, (int, float)):
        raise ValueError(f"Sampling rate must be numeric, got {type(sampling_rate)}")
    
    if sampling_rate <= 0:
        raise ValueError(f"Sampling rate must be positive, got {sampling_rate}")
    
    if sampling_rate < 100:
        logger.warning(f"Very low sampling rate: {sampling_rate} Hz. ECG analysis may be unreliable.")
    elif sampling_rate > 2000:
        logger.warning(f"Very high sampling rate: {sampling_rate} Hz. Consider downsampling.")
    
    return float(sampling_rate)


def validate_file_format(file_path: str) -> str:
    """
    Validate file format for ECG data.
    
    Args:
        file_path: Path to ECG data file
        
    Returns:
        Validated file path
        
    Raises:
        ValueError: If file format is not supported
    """
    supported_formats = {'.csv', '.txt', '.npy', '.dat'}
    file_extension = file_path.lower().split('.')[-1]
    
    if f'.{file_extension}' not in supported_formats:
        raise ValueError(f"Unsupported file format: .{file_extension}. "
                        f"Supported formats: {', '.join(supported_formats)}")
    
    return file_path
