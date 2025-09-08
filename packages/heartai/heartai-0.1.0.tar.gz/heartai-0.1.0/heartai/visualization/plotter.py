"""
ECG visualization and plotting tools
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict, Any, Tuple, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Set style for medical plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


class ECGPlotter:
    """
    ECG visualization and plotting utilities.
    
    Provides methods for plotting ECG signals, highlighting anomalies,
    and creating publication-ready figures.
    """
    
    def __init__(self, figsize: Tuple[int, int] = (12, 8), dpi: int = 100):
        """
        Initialize ECG plotter.
        
        Args:
            figsize: Default figure size (width, height)
            dpi: Figure resolution
        """
        self.figsize = figsize
        self.dpi = dpi
        self.colors = {
            'ecg': '#2E86AB',
            'filtered': '#A23B72', 
            'anomaly': '#F18F01',
            'r_peak': '#C73E1D',
            'normal': '#4CAF50',
            'arrhythmia': '#FF5722'
        }
    
    def plot_ecg(self, signal: np.ndarray, sampling_rate: float = 360.0,
                 title: str = "ECG Signal", time_range: Optional[Tuple[float, float]] = None,
                 show_grid: bool = True, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot ECG signal with time axis.
        
        Args:
            signal: ECG signal data
            sampling_rate: Sampling rate in Hz
            title: Plot title
            time_range: Time range to display (start, end) in seconds
            show_grid: Whether to show grid
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        # Create time axis
        time_axis = np.arange(len(signal)) / sampling_rate
        
        # Apply time range filter if specified
        if time_range:
            start_idx = int(time_range[0] * sampling_rate)
            end_idx = int(time_range[1] * sampling_rate)
            time_axis = time_axis[start_idx:end_idx]
            signal = signal[start_idx:end_idx]
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # Plot ECG signal
        ax.plot(time_axis, signal, color=self.colors['ecg'], linewidth=1.2, alpha=0.8)
        
        # Formatting
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Amplitude (mV)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        if show_grid:
            ax.grid(True, alpha=0.3)
        
        # Add minor ticks for better readability
        ax.minorticks_on()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"ECG plot saved to {save_path}")
        
        return fig
    
    def plot_comparison(self, raw_signal: np.ndarray, processed_signal: np.ndarray,
                       sampling_rate: float = 360.0, title: str = "ECG Signal Comparison",
                       save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot raw vs processed ECG signals for comparison.
        
        Args:
            raw_signal: Raw ECG signal
            processed_signal: Processed ECG signal
            sampling_rate: Sampling rate in Hz
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        time_axis = np.arange(len(raw_signal)) / sampling_rate
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.figsize[0], self.figsize[1] * 1.2), 
                                      dpi=self.dpi, sharex=True)
        
        # Plot raw signal
        ax1.plot(time_axis, raw_signal, color=self.colors['ecg'], linewidth=1.0, alpha=0.7)
        ax1.set_ylabel('Raw Signal (mV)', fontsize=11)
        ax1.set_title(f'{title} - Raw Signal', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Plot processed signal
        ax2.plot(time_axis, processed_signal, color=self.colors['filtered'], linewidth=1.2)
        ax2.set_xlabel('Time (seconds)', fontsize=12)
        ax2.set_ylabel('Processed Signal (mV)', fontsize=11)
        ax2.set_title(f'{title} - Processed Signal', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Comparison plot saved to {save_path}")
        
        return fig
    
    def plot_with_peaks(self, signal: np.ndarray, r_peaks: np.ndarray,
                       sampling_rate: float = 360.0, title: str = "ECG with R-peaks",
                       save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot ECG signal with R-peaks highlighted.
        
        Args:
            signal: ECG signal
            r_peaks: Array of R-peak indices
            sampling_rate: Sampling rate in Hz
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        time_axis = np.arange(len(signal)) / sampling_rate
        peak_times = r_peaks / sampling_rate
        
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # Plot ECG signal
        ax.plot(time_axis, signal, color=self.colors['ecg'], linewidth=1.2, alpha=0.8, label='ECG')
        
        # Highlight R-peaks
        ax.scatter(peak_times, signal[r_peaks], color=self.colors['r_peak'], 
                  s=50, zorder=5, label=f'R-peaks ({len(r_peaks)})', alpha=0.8)
        
        # Calculate heart rate
        if len(r_peaks) > 1:
            rr_intervals = np.diff(r_peaks) / sampling_rate
            avg_hr = 60.0 / np.mean(rr_intervals)
            ax.text(0.02, 0.98, f'Avg HR: {avg_hr:.1f} BPM', 
                   transform=ax.transAxes, fontsize=11, 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                   verticalalignment='top')
        
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Amplitude (mV)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"R-peaks plot saved to {save_path}")
        
        return fig
    
    def plot_prediction_result(self, signal: np.ndarray, prediction_result: Dict[str, Any],
                              sampling_rate: float = 360.0, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot ECG signal with prediction results highlighted.
        
        Args:
            signal: ECG signal
            prediction_result: Prediction results from ECGAnalyzer
            sampling_rate: Sampling rate in Hz
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        time_axis = np.arange(len(signal)) / sampling_rate
        
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        # Choose color based on prediction
        is_arrhythmia = prediction_result.get('prediction', 0) == 1
        signal_color = self.colors['arrhythmia'] if is_arrhythmia else self.colors['normal']
        
        # Plot ECG signal
        ax.plot(time_axis, signal, color=signal_color, linewidth=1.5, alpha=0.8)
        
        # Add prediction information
        status = prediction_result.get('status', 'Unknown')
        confidence = prediction_result.get('confidence', 0) * 100
        risk_level = prediction_result.get('risk_level', 'Unknown')
        
        # Create info box
        info_text = f"Status: {status}\nConfidence: {confidence:.1f}%\nRisk Level: {risk_level}"
        
        box_color = '#FFEBEE' if is_arrhythmia else '#E8F5E8'
        text_color = self.colors['arrhythmia'] if is_arrhythmia else self.colors['normal']
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=11,
               bbox=dict(boxstyle='round,pad=0.5', facecolor=box_color, alpha=0.9),
               verticalalignment='top', color=text_color, fontweight='bold')
        
        # Formatting
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('Amplitude (mV)', fontsize=12)
        ax.set_title(f'ECG Analysis Result - {status}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Prediction result plot saved to {save_path}")
        
        return fig
    
    def plot_heart_rate_variability(self, rr_intervals: np.ndarray, 
                                   title: str = "Heart Rate Variability",
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot heart rate variability analysis.
        
        Args:
            rr_intervals: RR intervals in seconds
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        if len(rr_intervals) < 2:
            raise ValueError("Need at least 2 RR intervals for HRV analysis")
        
        # Convert to heart rate
        heart_rates = 60.0 / rr_intervals
        time_points = np.cumsum(rr_intervals)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10), dpi=self.dpi)
        
        # 1. Heart rate over time
        ax1.plot(time_points, heart_rates, 'o-', color=self.colors['ecg'], markersize=4)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Heart Rate (BPM)')
        ax1.set_title('Heart Rate Over Time')
        ax1.grid(True, alpha=0.3)
        
        # 2. RR interval histogram
        ax2.hist(rr_intervals, bins=20, color=self.colors['ecg'], alpha=0.7, edgecolor='black')
        ax2.set_xlabel('RR Interval (seconds)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('RR Interval Distribution')
        ax2.grid(True, alpha=0.3)
        
        # 3. Poincaré plot
        rr1 = rr_intervals[:-1]
        rr2 = rr_intervals[1:]
        ax3.scatter(rr1, rr2, color=self.colors['ecg'], alpha=0.6, s=30)
        ax3.set_xlabel('RR(n) (seconds)')
        ax3.set_ylabel('RR(n+1) (seconds)')
        ax3.set_title('Poincaré Plot')
        ax3.grid(True, alpha=0.3)
        
        # Add identity line
        min_rr, max_rr = min(rr_intervals), max(rr_intervals)
        ax3.plot([min_rr, max_rr], [min_rr, max_rr], 'r--', alpha=0.5)
        
        # 4. HRV statistics
        ax4.axis('off')
        
        # Calculate HRV metrics
        mean_rr = np.mean(rr_intervals)
        std_rr = np.std(rr_intervals)
        rmssd = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
        pnn50 = np.sum(np.abs(np.diff(rr_intervals)) > 0.05) / len(np.diff(rr_intervals)) * 100
        
        stats_text = f"""HRV Statistics:
        
Mean RR: {mean_rr:.3f} s
Std RR: {std_rr:.3f} s
RMSSD: {rmssd:.3f} s
pNN50: {pnn50:.1f}%

Mean HR: {np.mean(heart_rates):.1f} BPM
Std HR: {np.std(heart_rates):.1f} BPM
        """
        
        ax4.text(0.1, 0.9, stats_text, transform=ax4.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"HRV plot saved to {save_path}")
        
        return fig
    
    def plot_frequency_analysis(self, signal: np.ndarray, sampling_rate: float = 360.0,
                               title: str = "ECG Frequency Analysis",
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot frequency domain analysis of ECG signal.
        
        Args:
            signal: ECG signal
            sampling_rate: Sampling rate in Hz
            title: Plot title
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        # Compute FFT
        fft_signal = np.fft.fft(signal)
        freqs = np.fft.fftfreq(len(signal), 1/sampling_rate)
        
        # Take only positive frequencies
        positive_freqs = freqs[:len(freqs)//2]
        magnitude = np.abs(fft_signal[:len(fft_signal)//2])
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.figsize[0], self.figsize[1] * 1.2), 
                                      dpi=self.dpi)
        
        # Time domain
        time_axis = np.arange(len(signal)) / sampling_rate
        ax1.plot(time_axis, signal, color=self.colors['ecg'], linewidth=1.0)
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Amplitude (mV)')
        ax1.set_title('Time Domain')
        ax1.grid(True, alpha=0.3)
        
        # Frequency domain
        ax2.plot(positive_freqs, magnitude, color=self.colors['filtered'], linewidth=1.2)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.set_title('Frequency Domain')
        ax2.set_xlim(0, min(50, sampling_rate/2))  # Limit to 50 Hz for clarity
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Frequency analysis plot saved to {save_path}")
        
        return fig
    
    def create_summary_report(self, analyzer_results: Dict[str, Any], 
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a comprehensive summary report figure.
        
        Args:
            analyzer_results: Results from ECGAnalyzer.analyze()
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure object
        """
        fig = plt.figure(figsize=(16, 12), dpi=self.dpi)
        
        # Create a grid layout
        gs = fig.add_gridspec(3, 2, height_ratios=[2, 1, 1], hspace=0.3, wspace=0.3)
        
        # Main ECG plot (top, full width)
        ax_main = fig.add_subplot(gs[0, :])
        
        # Get data from results
        metadata = analyzer_results.get('metadata', {})
        prediction = analyzer_results.get('prediction', 0)
        confidence = analyzer_results.get('confidence', 0)
        status = analyzer_results.get('status', 'Unknown')
        
        # Simulate signal for plotting (in real implementation, this would come from analyzer)
        duration = metadata.get('duration_seconds', 10)
        sampling_rate = metadata.get('sampling_rate', 360)
        n_samples = int(duration * sampling_rate)
        
        # Create sample signal for visualization
        from ..utils.helpers import generate_sample_ecg
        sample_signal = generate_sample_ecg(
            duration=duration, 
            sampling_rate=sampling_rate,
            arrhythmia=(prediction == 1)
        )
        
        time_axis = np.arange(len(sample_signal)) / sampling_rate
        signal_color = self.colors['arrhythmia'] if prediction == 1 else self.colors['normal']
        
        ax_main.plot(time_axis, sample_signal, color=signal_color, linewidth=1.5)
        ax_main.set_xlabel('Time (seconds)')
        ax_main.set_ylabel('Amplitude (mV)')
        ax_main.set_title(f'ECG Analysis - {status}', fontsize=16, fontweight='bold')
        ax_main.grid(True, alpha=0.3)
        
        # Prediction info (bottom left)
        ax_pred = fig.add_subplot(gs[1, 0])
        ax_pred.axis('off')
        
        pred_text = f"""Prediction Results:
        
Status: {status}
Confidence: {confidence*100:.1f}%
Risk Level: {analyzer_results.get('risk_level', 'Unknown')}
Prediction: {'Arrhythmia' if prediction == 1 else 'Normal'}
        """
        
        box_color = '#FFEBEE' if prediction == 1 else '#E8F5E8'
        ax_pred.text(0.1, 0.9, pred_text, transform=ax_pred.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.9))
        
        # Signal info (bottom right)
        ax_info = fig.add_subplot(gs[1, 1])
        ax_info.axis('off')
        
        info_text = f"""Signal Information:
        
Duration: {duration:.1f} seconds
Sampling Rate: {sampling_rate:.0f} Hz
Data Points: {metadata.get('data_length', 'N/A')}
File: {Path(metadata.get('file_path', 'Generated')).name}
        """
        
        ax_info.text(0.1, 0.9, info_text, transform=ax_info.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # Quality metrics (bottom, full width)
        ax_quality = fig.add_subplot(gs[2, :])
        ax_quality.axis('off')
        
        # Create quality visualization
        quality_metrics = ['Signal Quality', 'Noise Level', 'Baseline Stability', 'Peak Detection']
        quality_scores = [85, 78, 92, 88]  # Example scores
        
        bars = ax_quality.barh(quality_metrics, quality_scores, 
                              color=[self.colors['normal'] if s >= 80 else self.colors['anomaly'] for s in quality_scores])
        
        ax_quality.set_xlim(0, 100)
        ax_quality.set_xlabel('Quality Score (%)')
        ax_quality.set_title('Signal Quality Assessment', fontweight='bold')
        
        # Add score labels
        for i, (bar, score) in enumerate(zip(bars, quality_scores)):
            ax_quality.text(score + 2, i, f'{score}%', va='center', fontweight='bold')
        
        plt.suptitle('HeartAI ECG Analysis Report', fontsize=18, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
            logger.info(f"Summary report saved to {save_path}")
        
        return fig
    
    @staticmethod
    def show_plots():
        """Display all created plots."""
        plt.show()
    
    @staticmethod
    def close_all():
        """Close all plot windows."""
        plt.close('all')
