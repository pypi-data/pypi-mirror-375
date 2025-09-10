"""
PatX - Pattern eXtraction for Time Series Feature Engineering

A Python package for extracting polynomial patterns from time series data
to create meaningful features for machine learning models.
"""

from .core import PatternOptimizer
from .models import LightGBMModel, get_model, evaluate_model_performance
from .visualization import visualize_patterns

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "PatternOptimizer",
    "LightGBMModel", 
    "get_model",
    "evaluate_model_performance",
    "visualize_patterns"
]
