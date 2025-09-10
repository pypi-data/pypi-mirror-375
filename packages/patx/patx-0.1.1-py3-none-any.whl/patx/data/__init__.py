"""Data module for PatX package."""

import os
import pandas as pd
from pathlib import Path

def get_data_path():
    """Get the path to the data directory."""
    return Path(__file__).parent

def load_mitbih_data():
    """
    Load the MIT-BIH Arrhythmia Database data.
    
    Returns
    -------
    pd.DataFrame
        DataFrame containing the processed MIT-BIH data
    """
    data_path = get_data_path() / "mitbih_processed.csv"
    return pd.read_csv(data_path)
