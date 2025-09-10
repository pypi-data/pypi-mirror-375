"""
Model definitions and evaluation utilities for PatX.
"""

import lightgbm as lgb
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error
import numpy as np


def get_lgb_params(task_type, dataset, n_classes=None):
    """
    Get LightGBM parameters for different tasks and datasets.
    
    Parameters
    ----------
    task_type : str
        Type of task ('classification' or 'regression')
    dataset : str
        Dataset name
    n_classes : int, optional
        Number of classes for multiclass classification
        
    Returns
    -------
    dict
        LightGBM parameters
    """
    params = {
        'learning_rate': 0.1,
        'max_depth': 3,
        'num_iterations': 100,
        'random_state': 42,
        'num_threads': 1,   
        'force_col_wise': True,
        'verbosity': -1,
        'data_sample_strategy': 'goss',
    }
    
    if task_type == 'classification':
        if dataset == 'REMC':
            params['objective'] = 'binary'
            params['metric'] = 'auc'
        else:
            params['objective'] = 'multiclass'
            params['metric'] = 'multi_logloss'
            if n_classes is not None:
                params['num_class'] = n_classes
    else:
        params['objective'] = 'regression'
        params['metric'] = 'rmse'
    
    return params


class LightGBMModel:
    """
    Wrapper class for LightGBM models with consistent interface.
    """
    
    def __init__(self, params):
        """
        Initialize LightGBM model.
        
        Parameters
        ----------
        params : dict
            LightGBM parameters
        """
        self.params = params
        self.booster = None
    
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Train the LightGBM model.
        
        Parameters
        ----------
        X_train : array-like
            Training features
        y_train : array-like
            Training targets
        X_val : array-like, optional
            Validation features
        y_val : array-like, optional
            Validation targets
            
        Returns
        -------
        self
            Trained model instance
        """
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_sets = []
        if X_val is not None and y_val is not None:
            valid_sets = [lgb.Dataset(X_val, label=y_val, reference=train_data)]
        
        self.booster = lgb.train(
            self.params, 
            train_data, 
            valid_sets=valid_sets, 
            callbacks=[lgb.early_stopping(10, verbose=False)] if valid_sets else None
        )
        return self
    
    def predict(self, X):
        """
        Make predictions.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Predictions
        """
        preds = self.booster.predict(X)
        if self.params.get('objective') == 'multiclass':
            return np.argmax(preds, axis=1)
        elif self.params.get('objective') == 'binary':
            return (preds > 0.5).astype(int)
        return preds
    
    def predict_proba(self, X):
        """
        Get prediction probabilities.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Prediction probabilities
        """
        preds = self.booster.predict(X)
        if self.params.get('objective') == 'binary':
            return np.column_stack([1 - preds, preds])
        else:
            return preds
    
    def predict_proba_positive(self, X):
        """
        Get probability of positive class for binary classification.
        
        Parameters
        ----------
        X : array-like
            Features to predict on
            
        Returns
        -------
        array-like
            Probability of positive class
        """
        preds = self.predict_proba(X)
        if preds.ndim == 2:
            return preds[:, 1]
        return preds


def get_model(task_type, dataset, n_classes=None):
    """
    Get a model instance for the specified task and dataset.
    
    Parameters
    ----------
    task_type : str
        Type of task ('classification' or 'regression')
    dataset : str
        Dataset name
    n_classes : int, optional
        Number of classes for multiclass classification
        
    Returns
    -------
    LightGBMModel
        Configured model instance
    """
    params = get_lgb_params(task_type, dataset, n_classes)
    return LightGBMModel(params)


def evaluate_model_performance(model, X, y, metric):
    """
    Evaluate model performance using the specified metric.
    
    Parameters
    ----------
    model : object
        Trained model with predict methods
    X : array-like
        Features
    y : array-like
        True targets
    metric : str
        Evaluation metric ('auc', 'accuracy', 'rmse')
        
    Returns
    -------
    float
        Performance score
    """
    if metric == 'auc':
        if len(np.unique(y)) > 2:
            y_pred = model.predict_proba(X)
            score = roc_auc_score(y, y_pred, multi_class='ovr', average='macro')
        else:
            y_pred = model.predict_proba_positive(X)
            score = roc_auc_score(y, y_pred)
    elif metric == 'accuracy':
        y_pred = model.predict(X)
        score = accuracy_score(y, y_pred)
    elif metric == 'rmse':
        y_pred = model.predict(X)
        score = np.sqrt(mean_squared_error(y, y_pred))
    return score
