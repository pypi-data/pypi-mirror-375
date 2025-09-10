"""
PatX - Pattern eXtraction for Time Series Feature Engineering

A Python package for extracting polynomial patterns from time series data
to create meaningful features for machine learning models.
"""

from .core import PatternOptimizer
from .models import LightGBMModel, get_model, evaluate_model_performance

__version__ = "0.1.0"
__author__ = "Jonas Wolber"
__email__ = "jonascw@web.de"

__all__ = [
    "PatternOptimizer",
    "LightGBMModel", 
    "get_model",
    "evaluate_model_performance"
]
