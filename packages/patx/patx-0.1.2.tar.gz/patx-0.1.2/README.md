# PatX - Pattern eXtraction for Time Series Feature Engineering

[![PyPI version](https://badge.fury.io/py/patx.svg)](https://badge.fury.io/py/patx)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PatX is a Python package for extracting polynomial patterns from time series data to create meaningful features for machine learning models. It uses Optuna optimization to automatically discover patterns that are most predictive for your target variable.

## Features

- **Automatic Pattern Discovery**: Uses optimization to find the most predictive polynomial patterns in your time series data
- **Multiple Series Support**: Handle datasets with multiple time series channels
- **Flexible Models**: Built-in support for LightGBM with easy extension to other models
- **Visualization**: Built-in tools to visualize discovered patterns
- **Easy Integration**: Simple API that works with scikit-learn workflows

## Installation

```bash
pip install patx
```

## Quick Start

```python
import pandas as pd
from patx import PatternOptimizer, get_model, load_mitbih_data
from sklearn.model_selection import train_test_split

# Load the included MIT-BIH Arrhythmia dataset
data = load_mitbih_data()
X = data.drop('target', axis=1)
y = data['target'].to_numpy()

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Initialize model
n_classes = len(pd.unique(y))
model = get_model(task_type='classification', dataset='MITBIH', n_classes=n_classes)

# Create PatternOptimizer
optimizer = PatternOptimizer(
    X_train=X_train,
    y_train=y_train,
    model=model,
    max_n_trials=100,
    test_size=0.3,
    n_jobs=-1,
    show_progress=True,
    dataset='MITBIH',
    multiple_series=False,
    X_test_data=X_test,
    metric='accuracy',
    polynomial_degree=3,
    val_size=0.5
)

# Extract features
result = optimizer.feature_extraction()

# Get the trained model and features
trained_model = result['model']
X_train_features = result['X_train']
X_test_features = result['X_test']

# Make predictions
predictions = trained_model.predict(X_test_features)

# Visualize the discovered patterns
optimizer.visualize_patterns()  # Visualizes all patterns
# Or visualize specific patterns:
# optimizer.visualize_patterns(pattern_indices=[0, 1])
```

## Example: MIT-BIH Arrhythmia Classification

```python
from examples.mitbih_example import main
main()
```

This example demonstrates using PatX on ECG time series data for arrhythmia classification.

## API Reference

### PatternOptimizer

The main class for pattern extraction.

**Parameters:**
- `X_train`: Training time series data
- `y_train`: Training targets
- `model`: Model instance with train() and predict() methods
- `max_n_trials`: Maximum optimization trials
- `test_size`: Test split ratio
- `n_jobs`: Number of parallel jobs
- `show_progress`: Show progress bar
- `dataset`: Dataset name
- `multiple_series`: Whether data has multiple series
- `X_test_data`: Test data for feature extraction
- `metric`: Evaluation metric ('accuracy', 'auc', 'rmse')
- `polynomial_degree`: Degree of polynomial patterns
- `val_size`: Validation split ratio
- `initial_features`: Optional initial features

**Methods:**
- `feature_extraction()`: Extract patterns and return features
- `save_parameters_to_json(dataset_name)`: Save pattern parameters
- `visualize_patterns(pattern_indices=None, dataset_name=None, specific_name='patterns')`: Visualize discovered patterns

### Models

Built-in model support:
- `get_model(task_type, dataset, n_classes)`: Get configured model
- `LightGBMModel`: LightGBM wrapper with consistent interface
- `evaluate_model_performance(model, X, y, metric)`: Evaluate model

### Data

- `load_mitbih_data()`: Load the included MIT-BIH Arrhythmia dataset

## Advanced Usage

### Multiple Time Series

For datasets with multiple time series channels:

```python
optimizer = PatternOptimizer(
    X_train=X_train_list,  # List of time series
    y_train=y_train,
    multiple_series=True,
    # ... other parameters
)
```

### Custom Models

You can use any model that implements `train()` and `predict()` methods:

```python
class CustomModel:
    def train(self, X_train, y_train, X_val=None, y_val=None):
        # Your training logic
        pass
    
    def predict(self, X):
        # Your prediction logic
        pass

model = CustomModel()
optimizer = PatternOptimizer(X_train, y_train, model=model, ...)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use PatX in your research, please cite:

```bibtex
@software{patx,
  title={PatX: Pattern eXtraction for Time Series Feature Engineering},
  author={Your Name},
  year={2025},
  url={https://github.com/Prgrmmrjns/patX}
}
```