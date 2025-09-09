""
Machine learning module for financial time series prediction.
Includes feature engineering, model training, and prediction utilities.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List, Union, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings

class FeatureEngineer:
    """Feature engineering for financial time series data."""
    
    def __init__(self, lookback: int = 10):
        """
        Initialize feature engineer.
        
        Args:
            lookback: Number of periods to look back for feature creation
        """
        self.lookback = lookback
    
    def create_features(self, data: pd.Series) -> pd.DataFrame:
        """
        Create technical features from price/return data.
        
        Args:
            data: Time series data (prices or returns)
            
        Returns:
            DataFrame with engineered features
        """
        df = pd.DataFrame(index=data.index)
        
        # Basic features
        df['returns'] = data.pct_change()
        df['log_returns'] = np.log1p(df['returns'])
        
        # Momentum features
        for period in [5, 10, 20]:
            df[f'momentum_{period}'] = data.pct_change(periods=period)
        
        # Volatility features
        for period in [5, 10, 20]:
            df[f'volatility_{period}'] = df['returns'].rolling(period).std()
        
        # Moving averages
        for period in [5, 10, 20, 50, 200]:
            df[f'ma_{period}'] = data.rolling(period).mean()
            df[f'ma_ratio_{period}'] = data / df[f'ma_{period}'] - 1
        
        # Drop NaN values created by rolling windows
        df = df.dropna()
        
        return df
    
    def create_sequences(self, data: np.ndarray, target: np.ndarray, 
                        sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for time series prediction.
        
        Args:
            data: Feature data
            target: Target values
            sequence_length: Length of input sequences
            
        Returns:
            Tuple of (X, y) arrays for model training
        """
        X, y = [], []
        for i in range(len(data) - sequence_length):
            X.append(data[i:(i + sequence_length)])
            y.append(target[i + sequence_length])
        return np.array(X), np.array(y)


class ModelEvaluator:
    """Evaluate time series prediction models."""
    
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate regression metrics.
        
        Args:
            y_true: True target values
            y_pred: Predicted values
            
        Returns:
            Dictionary of evaluation metrics
        """
        return {
            'mse': mean_squared_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred),
            'direction_accuracy': np.mean(np.sign(y_true[1:] - y_true[:-1]) == 
                                        np.sign(y_pred[1:] - y_pred[:-1]))
        }
    
    @staticmethod
    def time_series_cv(model, X: np.ndarray, y: np.ndarray, 
                      n_splits: int = 5) -> Dict[str, List[float]]:
        """
        Perform time series cross-validation.
        
        Args:
            model: Model implementing fit/predict interface
            X: Feature matrix
            y: Target vector
            n_splits: Number of CV folds
            
        Returns:
            Dictionary of evaluation metrics across folds
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        metrics = {'mse': [], 'rmse': [], 'mae': [], 'r2': [], 'direction_accuracy': []}
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            fold_metrics = ModelEvaluator.calculate_metrics(y_test, y_pred)
            for k, v in fold_metrics.items():
                metrics[k].append(v)
        
        # Calculate mean and std of metrics
        result = {}
        for k, v in metrics.items():
            result[f'mean_{k}'] = np.mean(v)
            result[f'std_{k}'] = np.std(v)
        
        return result


def prepare_data_for_lstm(features: pd.DataFrame, target: pd.Series, 
                        sequence_length: int = 10, 
                        test_size: float = 0.2) -> Tuple[np.ndarray, np.ndarray, 
                                                       np.ndarray, np.ndarray]:
    """
    Prepare data for LSTM models.
    
    Args:
        features: DataFrame of features
        target: Series of target values
        sequence_length: Length of input sequences
        test_size: Fraction of data to use for testing
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    # Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    # Create sequences
    X, y = [], []
    for i in range(len(scaled_features) - sequence_length):
        X.append(scaled_features[i:(i + sequence_length)])
        y.append(target.iloc[i + sequence_length])
    
    X = np.array(X)
    y = np.array(y)
    
    # Split into train/test
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    return X_train, X_test, y_train, y_test
