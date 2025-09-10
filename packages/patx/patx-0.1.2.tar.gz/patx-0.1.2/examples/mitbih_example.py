"""
Example usage of PatX with MIT-BIH Arrhythmia Database.

This example demonstrates how to use PatX for feature extraction
on ECG time series data for arrhythmia classification.
"""

import pandas as pd
import numpy as np
import time
import warnings
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from patx import PatternOptimizer, get_model, load_mitbih_data

warnings.filterwarnings('ignore')

# Configuration
DATASET = 'MITBIH'
METRIC = 'accuracy'
TASK_TYPE = 'classification'
TIME_SERIES_IDENTIFIERS = []

# PatX Configuration
MAX_N_TRIALS = 500
N_JOBS = -1
SHOW_PROGRESS = True
TEST_SIZE = 1/3
VAL_SIZE = 0.5
POLYNOMIAL_DEGREE = 3


def prepare_mitbih_data():
    """
    Prepare MIT-BIH Arrhythmia Database data for training.
    
    Returns
    -------
    dict
        Dictionary containing train/test splits and metadata
    """
    data = load_mitbih_data()
    X = data.drop('target', axis=1)
    y = data['target'].to_numpy()
    X_train, X_test, y_train, y_test = train_test_split(
        X.to_numpy(), y, test_size=TEST_SIZE, random_state=42, stratify=y
    )
    X_train_df = pd.DataFrame(X_train)
    X_test_df = pd.DataFrame(X_test)
    
    return {
        'X_train': X_train_df,
        'X_test': X_test_df,
        'y_train': y_train,
        'y_test': y_test,
        'input_data': X_train_df,
        'test_data': X_test_df,
        'dims': X_train_df.shape[1]
    }


def main():
    """Run the MIT-BIH example."""
    print("Loading MIT-BIH Arrhythmia Database...")
    data = prepare_mitbih_data()
    
    y_train = data['y_train']
    y_test = data['y_test']
    input_data = data['input_data']
    test_data = data['test_data']
    
    n_classes = len(np.unique(y_train))
    print(f"Dataset loaded: {input_data.shape[0]} training samples, {n_classes} classes")
    
    # Initialize model
    model = get_model(TASK_TYPE, 'MITBIH', n_classes)
    
    # Initialize PatternOptimizer
    optimizer = PatternOptimizer(
        input_data, y_train, 
        model=model, 
        max_n_trials=MAX_N_TRIALS,
        show_progress=SHOW_PROGRESS, 
        test_size=VAL_SIZE, 
        n_jobs=N_JOBS,
        dataset='MITBIH', 
        multiple_series=len(TIME_SERIES_IDENTIFIERS) > 0,
        X_test_data=test_data, 
        polynomial_degree=POLYNOMIAL_DEGREE,
        metric=METRIC, 
        val_size=VAL_SIZE,
        initial_features=None
    )
    
    print("Starting pattern extraction...")
    t0 = time.time()
    result = optimizer.feature_extraction()
    t1 = time.time()
    
    # Save parameters
    optimizer.save_parameters_to_json('MITBIH')
    
    # Extract results
    X_train = result['X_train']
    X_val = result['X_val']
    y_train_split = result['y_train']
    y_val = result['y_val']
    X_test = result['X_test']
    model = result['model']
    
    # Make predictions
    train_preds = model.predict(X_train)
    val_preds = model.predict(X_val)
    test_preds = model.predict(X_test)
    
    # Calculate scores
    train_score = accuracy_score(y_train_split, train_preds)
    val_score = accuracy_score(y_val, val_preds)
    test_score = accuracy_score(y_test, test_preds)
    
    # Print results
    print("\n" + "="*50)
    print("RESULTS")
    print("="*50)
    print(f"Train score: {train_score:.4f}")
    print(f"Val score: {val_score:.4f}")
    print(f"Test score: {test_score:.4f}")
    print(f"Processing time: {t1 - t0:.2f} seconds")
    print(f"Number of features: {X_train.shape[1]}")
    print(f"Number of patterns: {len(result['patterns'])}")
    print("="*50)
    
    # Visualize the discovered patterns
    print("\nVisualizing discovered patterns...")
    optimizer.visualize_patterns()
    print("Pattern visualization complete!")


if __name__ == "__main__":
    main()
