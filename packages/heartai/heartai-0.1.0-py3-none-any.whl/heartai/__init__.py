"""
HeartAI - ECG/EKG signal processing and arrhythmia detection library
"""

__version__ = "0.1.0"
__author__ = "AhmetXHero"
__email__ = "ahmetxhero@gmail.com"

from .core.analyzer import ECGAnalyzer
from .core.preprocessing import ECGPreprocessor
from .core.models import ArrhythmiaDetector
from .visualization.plotter import ECGPlotter

__all__ = [
    "ECGAnalyzer",
    "ECGPreprocessor", 
    "ArrhythmiaDetector",
    "ECGPlotter",
]
